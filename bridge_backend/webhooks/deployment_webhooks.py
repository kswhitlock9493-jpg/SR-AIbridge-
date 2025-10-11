"""
Deployment Webhook Routes
Webhook endpoints for Netlify, Render, and GitHub to notify autonomy engine of deployment events
"""

from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional, Dict, Any
from datetime import datetime, UTC
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/deployment", tags=["webhooks", "deployment"])


async def publish_to_genesis(platform: str, event_type: str, status: str, metadata: Dict[str, Any]):
    """Publish deployment event to Genesis bus"""
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.info("Genesis bus disabled, skipping deployment webhook event")
            return False
        
        # Construct event payload
        event = {
            "platform": platform,
            "event_type": event_type,
            "status": status,
            "timestamp": datetime.now(UTC).isoformat(),
            "metadata": metadata
        }
        
        # Publish to platform-specific topic
        topic = f"deploy.{platform.lower()}"
        await genesis_bus.publish(topic, event)
        logger.info(f"✅ Published deployment webhook event to {topic}: {event_type}")
        
        # Also publish to generic deployment topic based on event type
        if event_type in ["start", "starting", "initiated", "building"]:
            await genesis_bus.publish("deploy.platform.start", event)
        elif event_type in ["success", "completed", "deployed", "ready"]:
            await genesis_bus.publish("deploy.platform.success", event)
        elif event_type in ["failure", "failed", "error"]:
            await genesis_bus.publish("deploy.platform.failure", event)
        
        return True
    except Exception as e:
        logger.error(f"Failed to publish deployment webhook event: {e}")
        return False


@router.post("/netlify")
async def netlify_webhook(request: Request, x_netlify_event: Optional[str] = Header(None)):
    """
    Netlify deployment webhook endpoint.
    
    Netlify sends deployment notifications with the following events:
    - deploy-building: Build started
    - deploy-succeeded: Deployment successful
    - deploy-failed: Deployment failed
    """
    try:
        body = await request.json()
        
        event_type = x_netlify_event or body.get("state", "unknown")
        
        # Map Netlify event to our event type
        status_map = {
            "deploy-building": ("start", "building"),
            "deploy-succeeded": ("success", "deployed"),
            "deploy-failed": ("failure", "failed"),
            "ready": ("success", "ready"),
            "building": ("start", "building"),
            "error": ("failure", "error")
        }
        
        our_event_type, status = status_map.get(event_type, ("unknown", "unknown"))
        
        # Extract metadata
        metadata = {
            "netlify_event": event_type,
            "site_id": body.get("site_id"),
            "deploy_id": body.get("id"),
            "deploy_url": body.get("deploy_ssl_url") or body.get("url"),
            "commit_ref": body.get("commit_ref"),
            "branch": body.get("branch"),
            "build_id": body.get("build_id"),
            "context": body.get("context"),
            "raw_body": body
        }
        
        # Publish to Genesis
        success = await publish_to_genesis("netlify", our_event_type, status, metadata)
        
        return {
            "status": "success" if success else "skipped",
            "platform": "netlify",
            "event_type": our_event_type,
            "netlify_event": event_type
        }
    except Exception as e:
        logger.error(f"Netlify webhook error: {e}")
        raise HTTPException(500, f"Webhook processing failed: {str(e)}")


@router.post("/render")
async def render_webhook(request: Request):
    """
    Render deployment webhook endpoint.
    
    Render sends deployment notifications with various event types.
    """
    try:
        body = await request.json()
        
        # Render webhook structure (example):
        # {"service": {...}, "deploy": {...}, "status": "live"}
        event_type = body.get("status", "unknown")
        
        # Map Render event to our event type
        status_map = {
            "build_in_progress": ("start", "building"),
            "live": ("success", "deployed"),
            "build_failed": ("failure", "failed"),
            "deactivated": ("failure", "deactivated"),
            "pre_deploy_in_progress": ("start", "preparing"),
            "update_in_progress": ("start", "updating")
        }
        
        our_event_type, status = status_map.get(event_type, ("unknown", event_type))
        
        # Extract metadata
        service = body.get("service", {})
        deploy = body.get("deploy", {})
        
        metadata = {
            "render_event": event_type,
            "service_id": service.get("id"),
            "service_name": service.get("name"),
            "deploy_id": deploy.get("id"),
            "commit": deploy.get("commit", {}).get("id"),
            "branch": service.get("branch"),
            "region": service.get("region"),
            "raw_body": body
        }
        
        # Publish to Genesis
        success = await publish_to_genesis("render", our_event_type, status, metadata)
        
        return {
            "status": "success" if success else "skipped",
            "platform": "render",
            "event_type": our_event_type,
            "render_event": event_type
        }
    except Exception as e:
        logger.error(f"Render webhook error: {e}")
        raise HTTPException(500, f"Webhook processing failed: {str(e)}")


@router.post("/github")
async def github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    GitHub webhook endpoint for deployment events.
    
    Handles GitHub deployment and workflow_run events.
    """
    try:
        body = await request.json()
        
        event_type = x_github_event or "unknown"
        
        # Handle different GitHub webhook events
        if event_type == "deployment":
            deployment = body.get("deployment", {})
            our_event_type = "start"
            status = "deploying"
            metadata = {
                "github_event": event_type,
                "deployment_id": deployment.get("id"),
                "ref": deployment.get("ref"),
                "sha": deployment.get("sha"),
                "environment": deployment.get("environment"),
                "description": deployment.get("description"),
                "raw_body": body
            }
        elif event_type == "deployment_status":
            deployment_status = body.get("deployment_status", {})
            state = deployment_status.get("state", "unknown")
            
            status_map = {
                "pending": ("start", "pending"),
                "success": ("success", "deployed"),
                "failure": ("failure", "failed"),
                "error": ("failure", "error"),
                "in_progress": ("start", "deploying")
            }
            
            our_event_type, status = status_map.get(state, ("unknown", state))
            
            metadata = {
                "github_event": event_type,
                "deployment_id": deployment_status.get("deployment", {}).get("id"),
                "state": state,
                "target_url": deployment_status.get("target_url"),
                "description": deployment_status.get("description"),
                "environment": deployment_status.get("environment"),
                "raw_body": body
            }
        elif event_type == "workflow_run":
            workflow_run = body.get("workflow_run", {})
            conclusion = workflow_run.get("conclusion")
            
            status_map = {
                "success": ("success", "completed"),
                "failure": ("failure", "failed"),
                "cancelled": ("failure", "cancelled"),
                None: ("start", "running")
            }
            
            our_event_type, status = status_map.get(conclusion, ("unknown", "unknown"))
            
            metadata = {
                "github_event": event_type,
                "workflow_id": workflow_run.get("id"),
                "workflow_name": workflow_run.get("name"),
                "head_branch": workflow_run.get("head_branch"),
                "head_sha": workflow_run.get("head_sha"),
                "conclusion": conclusion,
                "html_url": workflow_run.get("html_url"),
                "raw_body": body
            }
        else:
            # Generic event handling
            our_event_type = "unknown"
            status = "unknown"
            metadata = {
                "github_event": event_type,
                "raw_body": body
            }
        
        # Publish to Genesis
        success = await publish_to_genesis("github", our_event_type, status, metadata)
        
        return {
            "status": "success" if success else "skipped",
            "platform": "github",
            "event_type": our_event_type,
            "github_event": event_type
        }
    except Exception as e:
        logger.error(f"GitHub webhook error: {e}")
        raise HTTPException(500, f"Webhook processing failed: {str(e)}")


@router.get("/status")
def webhook_status():
    """Get webhook endpoint status"""
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        return {
            "status": "active" if genesis_bus.is_enabled() else "disabled",
            "genesis_enabled": genesis_bus.is_enabled(),
            "endpoints": {
                "netlify": "/webhooks/deployment/netlify",
                "render": "/webhooks/deployment/render",
                "github": "/webhooks/deployment/github"
            },
            "supported_platforms": ["netlify", "render", "github"],
            "message": "Webhook endpoints ready for deployment event integration"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
