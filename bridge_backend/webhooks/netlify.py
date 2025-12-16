"""
Netlify Webhook Handler
Normalizes Netlify deploy/build signals and emits to Umbra Triage Mesh
"""

from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import logging
import os
import hmac
import hashlib

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/netlify", tags=["webhooks"])


def verify_netlify_signature(payload: bytes, signature: Optional[str], secret: Optional[str]) -> bool:
    """
    Verify Netlify webhook signature using HMAC SHA256
    
    Args:
        payload: Request body bytes
        signature: Signature from header (format: "sha256=...")
        secret: Webhook secret
        
    Returns:
        True if signature is valid
    """
    if not secret:
        # No secret configured
        allow_unverified = os.getenv("UMBRA_ALLOW_UNVERIFIED_WEBHOOKS", "false").lower() == "true"
        if allow_unverified:
            logger.warning("[Netlify Webhook] No secret configured, allowing unverified webhook (UMBRA_ALLOW_UNVERIFIED_WEBHOOKS=true)")
            return True
        logger.error("[Netlify Webhook] No secret configured and UMBRA_ALLOW_UNVERIFIED_WEBHOOKS=false")
        return False
    
    if not signature:
        logger.error("[Netlify Webhook] No signature provided")
        return False
    
    # Extract hex signature (remove "sha256=" prefix if present)
    sig_value = signature.replace("sha256=", "") if signature.startswith("sha256=") else signature
    
    # Compute expected signature
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    return hmac.compare_digest(sig_value, expected)


@router.post("")
async def handle_netlify_webhook(
    request: Request,
    x_netlify_signature: Optional[str] = Header(None)
):
    """
    Handle Netlify webhook events
    
    Processes deploy and build signals from Netlify and emits to Umbra Triage Mesh
    
    **RBAC**: Public (signature verification required)
    """
    try:
        # Get payload
        payload = await request.body()
        
        # Verify signature
        secret = os.getenv("NETLIFY_DEPLOY_WEBHOOK_SECRET")
        if not verify_netlify_signature(payload, x_netlify_signature, secret):
            logger.error("[Netlify Webhook] Invalid signature")
            raise HTTPException(status_code=401, detail="invalid_signature")
        
        # Parse JSON
        import json
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("[Netlify Webhook] Invalid JSON payload")
            raise HTTPException(status_code=400, detail="invalid_json")
        
        # Extract event details
        event_type = event.get("name", "unknown")  # deploy-building, deploy-failed, deploy-succeeded
        site = event.get("site_name", "unknown")
        deploy_id = event.get("id", "")
        state = event.get("state", "")
        context = event.get("context", "production")
        
        # Normalize to Umbra signal
        signal = {
            "kind": "deploy",
            "source": "netlify",
            "severity": "info",
            "message": f"Netlify {event_type}",
            "metadata": {
                "event_type": event_type,
                "site_name": site,
                "deploy_id": deploy_id,
                "state": state,
                "context": context,
                "commit_ref": event.get("commit_ref"),
                "commit_url": event.get("commit_url")
            }
        }
        
        # Determine severity based on event type
        if event_type in ["deploy-failed", "deploy_failed"]:
            signal["severity"] = "critical"
            signal["message"] = f"Netlify deploy failed: {site}"
        elif state == "error":
            signal["severity"] = "critical"
            signal["message"] = f"Netlify error: {site}"
        elif event_type in ["deploy-building", "deploy_building"]:
            signal["severity"] = "info"
        elif event_type in ["deploy-succeeded", "deploy_succeeded"]:
            signal["severity"] = "info"
        
        # Check for specific issues
        error_message = event.get("error_message", "")
        if error_message:
            signal["severity"] = "critical"
            signal["message"] = f"Netlify error: {error_message}"
            signal["metadata"]["error_message"] = error_message
        
        # Emit to Umbra via Genesis
        try:
            from bridge_backend.genesis.bus import genesis_bus
            
            if genesis_bus.is_enabled():
                await genesis_bus.publish("triage.signal.deploy", signal)
                logger.info(f"[Netlify Webhook] Emitted signal: {event_type}")
        except Exception as e:
            logger.warning(f"[Netlify Webhook] Failed to emit to Genesis: {e}")
        
        # Also directly ingest to Umbra
        try:
            from bridge_backend.engines.umbra.core import UmbraTriageCore
            
            core = UmbraTriageCore()
            if core.enabled:
                await core.ingest_signal(signal)
                logger.info(f"[Netlify Webhook] Ingested to Umbra: {event_type}")
        except Exception as e:
            logger.warning(f"[Netlify Webhook] Failed to ingest to Umbra: {e}")
        
        return {
            "status": "processed",
            "event_type": event_type,
            "signal_emitted": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Netlify Webhook] Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
