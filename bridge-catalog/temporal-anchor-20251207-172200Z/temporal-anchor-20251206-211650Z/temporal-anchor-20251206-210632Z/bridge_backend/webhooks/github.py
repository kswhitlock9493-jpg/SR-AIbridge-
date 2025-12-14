"""
GitHub Webhook Handler
Normalizes GitHub workflow/check signals and emits to Umbra Triage Mesh
"""

from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
import logging
import os
import hmac
import hashlib

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/github", tags=["webhooks"])


def verify_github_signature(payload: bytes, signature: Optional[str], secret: Optional[str]) -> bool:
    """
    Verify GitHub webhook signature using HMAC SHA256
    
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
            logger.warning("[GitHub Webhook] No secret configured, allowing unverified webhook (UMBRA_ALLOW_UNVERIFIED_WEBHOOKS=true)")
            return True
        logger.error("[GitHub Webhook] No secret configured and UMBRA_ALLOW_UNVERIFIED_WEBHOOKS=false")
        return False
    
    if not signature:
        logger.error("[GitHub Webhook] No signature provided")
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
async def handle_github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    """
    Handle GitHub webhook events
    
    Processes workflow run, check suite, and deployment signals and emits to Umbra Triage Mesh
    
    **RBAC**: Public (signature verification required)
    """
    try:
        # Get payload
        payload = await request.body()
        
        # Verify signature
        secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        if not verify_github_signature(payload, x_hub_signature_256, secret):
            logger.error("[GitHub Webhook] Invalid signature")
            raise HTTPException(status_code=401, detail="invalid_signature")
        
        # Parse JSON
        import json
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("[GitHub Webhook] Invalid JSON payload")
            raise HTTPException(status_code=400, detail="invalid_json")
        
        # Determine event type and extract relevant data
        event_type = x_github_event or "unknown"
        
        signal = None
        
        if event_type == "workflow_run":
            # GitHub Actions workflow run event
            workflow_run = event.get("workflow_run", {})
            conclusion = workflow_run.get("conclusion")
            status = workflow_run.get("status")
            
            signal = {
                "kind": "build",
                "source": "github",
                "severity": "info",
                "message": f"GitHub workflow {workflow_run.get('name', 'unknown')}",
                "metadata": {
                    "event_type": event_type,
                    "workflow_id": workflow_run.get("id"),
                    "workflow_name": workflow_run.get("name"),
                    "status": status,
                    "conclusion": conclusion,
                    "run_number": workflow_run.get("run_number"),
                    "commit_sha": workflow_run.get("head_sha"),
                    "repository": event.get("repository", {}).get("full_name")
                }
            }
            
            # Determine severity
            if conclusion == "failure":
                signal["severity"] = "critical"
                signal["message"] = f"GitHub workflow failed: {workflow_run.get('name', 'unknown')}"
            elif conclusion == "cancelled":
                signal["severity"] = "warning"
                signal["message"] = f"GitHub workflow cancelled: {workflow_run.get('name', 'unknown')}"
            elif conclusion == "success":
                signal["severity"] = "info"
        
        elif event_type == "check_suite":
            # GitHub check suite event
            check_suite = event.get("check_suite", {})
            conclusion = check_suite.get("conclusion")
            status = check_suite.get("status")
            
            signal = {
                "kind": "build",
                "source": "github",
                "severity": "info",
                "message": f"GitHub check suite",
                "metadata": {
                    "event_type": event_type,
                    "check_suite_id": check_suite.get("id"),
                    "status": status,
                    "conclusion": conclusion,
                    "commit_sha": check_suite.get("head_sha"),
                    "repository": event.get("repository", {}).get("full_name")
                }
            }
            
            if conclusion == "failure":
                signal["severity"] = "critical"
                signal["message"] = "GitHub check suite failed"
        
        elif event_type == "deployment_status":
            # GitHub deployment status event
            deployment_status = event.get("deployment_status", {})
            state = deployment_status.get("state")
            
            signal = {
                "kind": "deploy",
                "source": "github",
                "severity": "info",
                "message": f"GitHub deployment {state}",
                "metadata": {
                    "event_type": event_type,
                    "deployment_id": event.get("deployment", {}).get("id"),
                    "state": state,
                    "environment": event.get("deployment", {}).get("environment"),
                    "repository": event.get("repository", {}).get("full_name")
                }
            }
            
            if state in ["error", "failure"]:
                signal["severity"] = "critical"
                signal["message"] = f"GitHub deployment failed: {event.get('deployment', {}).get('environment')}"
        
        else:
            logger.info(f"[GitHub Webhook] Ignoring event type: {event_type}")
            return {
                "status": "ignored",
                "event_type": event_type
            }
        
        # Emit signal if we have one
        if signal:
            # Emit to Umbra via Genesis
            try:
                from bridge_backend.genesis.bus import genesis_bus
                
                if genesis_bus.is_enabled():
                    topic = f"triage.signal.{signal['kind']}"
                    await genesis_bus.publish(topic, signal)
                    logger.info(f"[GitHub Webhook] Emitted signal: {event_type}")
            except Exception as e:
                logger.warning(f"[GitHub Webhook] Failed to emit to Genesis: {e}")
            
            # Also directly ingest to Umbra
            try:
                from bridge_backend.engines.umbra.core import UmbraTriageCore
                
                core = UmbraTriageCore()
                if core.enabled:
                    await core.ingest_signal(signal)
                    logger.info(f"[GitHub Webhook] Ingested to Umbra: {event_type}")
            except Exception as e:
                logger.warning(f"[GitHub Webhook] Failed to ingest to Umbra: {e}")
        
        return {
            "status": "processed",
            "event_type": event_type,
            "signal_emitted": signal is not None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[GitHub Webhook] Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
