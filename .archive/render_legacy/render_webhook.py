"""
Render Webhook Handler
Normalizes Render deploy/build signals and emits to Umbra Triage Mesh
"""

from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import logging
import os
import hmac
import hashlib

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/render", tags=["webhooks"])


def verify_render_signature(payload: bytes, signature: Optional[str], secret: Optional[str]) -> bool:
    """
    Verify Render webhook signature using HMAC
    
    Args:
        payload: Request body bytes
        signature: Signature from header
        secret: Webhook secret
        
    Returns:
        True if signature is valid
    """
    if not secret:
        # No secret configured
        allow_unverified = os.getenv("UMBRA_ALLOW_UNVERIFIED_WEBHOOKS", "false").lower() == "true"
        if allow_unverified:
            logger.warning("[Render Webhook] No secret configured, allowing unverified webhook (UMBRA_ALLOW_UNVERIFIED_WEBHOOKS=true)")
            return True
        logger.error("[Render Webhook] No secret configured and UMBRA_ALLOW_UNVERIFIED_WEBHOOKS=false")
        return False
    
    if not signature:
        logger.error("[Render Webhook] No signature provided")
        return False
    
    # Compute expected signature
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    return hmac.compare_digest(signature, expected)


@router.post("")
async def handle_render_webhook(
    request: Request,
    x_render_signature: Optional[str] = Header(None)
):
    """
    Handle Render webhook events
    
    Processes deploy and build signals from Render and emits to Umbra Triage Mesh
    
    **RBAC**: Public (signature verification required)
    """
    try:
        # Get payload
        payload = await request.body()
        
        # Verify signature
        secret = os.getenv("RENDER_WEBHOOK_SECRET")
        if not verify_render_signature(payload, x_render_signature, secret):
            logger.error("[Render Webhook] Invalid signature")
            raise HTTPException(status_code=401, detail="invalid_signature")
        
        # Parse JSON
        import json
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("[Render Webhook] Invalid JSON payload")
            raise HTTPException(status_code=400, detail="invalid_json")
        
        # Extract event details
        event_type = event.get("type", "unknown")
        service = event.get("service", {})
        deploy = event.get("deploy", {})
        
        # Normalize to Umbra signal
        signal = {
            "kind": "deploy",
            "source": "render",
            "severity": "info",
            "message": f"Render {event_type}",
            "metadata": {
                "event_type": event_type,
                "service_id": service.get("id"),
                "service_name": service.get("name"),
                "deploy_id": deploy.get("id"),
                "deploy_status": deploy.get("status"),
                "commit": deploy.get("commit", {}).get("id")
            }
        }
        
        # Determine severity based on deploy status
        deploy_status = deploy.get("status", "").lower()
        if deploy_status in ["failed", "build_failed", "deploy_failed"]:
            signal["severity"] = "critical"
            signal["message"] = f"Render deploy failed: {deploy.get('id')}"
        elif deploy_status in ["cancelled"]:
            signal["severity"] = "warning"
        
        # Emit to Umbra via Genesis
        try:
            from bridge_backend.genesis.bus import genesis_bus
            
            if genesis_bus.is_enabled():
                await genesis_bus.publish("triage.signal.deploy", signal)
                logger.info(f"[Render Webhook] Emitted signal: {event_type}")
        except Exception as e:
            logger.warning(f"[Render Webhook] Failed to emit to Genesis: {e}")
        
        # Also directly ingest to Umbra
        try:
            from bridge_backend.engines.umbra.core import UmbraTriageCore
            
            core = UmbraTriageCore()
            if core.enabled:
                await core.ingest_signal(signal)
                logger.info(f"[Render Webhook] Ingested to Umbra: {event_type}")
        except Exception as e:
            logger.warning(f"[Render Webhook] Failed to ingest to Umbra: {e}")
        
        return {
            "status": "processed",
            "event_type": event_type,
            "signal_emitted": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Render Webhook] Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
