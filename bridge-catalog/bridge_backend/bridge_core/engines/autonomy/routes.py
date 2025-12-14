from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from .service import AutonomyEngine

router = APIRouter(prefix="/engines/autonomy", tags=["autonomy"])
AE = AutonomyEngine()

class TaskIn(BaseModel):
    project: str
    captain: str
    objective: str
    permissions: dict
    mode: str = "screen"
    verify_originality: bool = True  # Enable anti-copyright & compliance checks by default
    files: Optional[List[str]] = None  # Optional: specific files to check
    validate_compliance: bool = True  # Alias for verify_originality for backward compatibility

class StatusUpdate(BaseModel):
    status: str
    result: Optional[dict] = None

@router.post("/task")
def create_task(req: TaskIn):
    # Use validate_compliance if verify_originality not explicitly set
    verify = req.verify_originality if req.verify_originality is not None else req.validate_compliance
    tc = AE.create_task(
        req.project, 
        req.captain, 
        req.objective, 
        req.permissions, 
        req.mode,
        verify,
        req.files
    )
    return {"task": tc.__dict__}

@router.post("/task/{task_id}/status")
def update_status(task_id: str, update: StatusUpdate):
    tc = AE.update_status(task_id, update.status, update.result)
    if not tc:
        raise HTTPException(404, "task_not_found")
    return {"task": tc.__dict__}

@router.get("/tasks")
def list_tasks():
    return {"tasks": AE.list_tasks()}

@router.get("/task/{task_id}/compliance")
def get_compliance_validation(task_id: str):
    """Retrieve compliance validation results for a task"""
    validation = AE.get_compliance_validation(task_id)
    if not validation:
        raise HTTPException(404, "task_not_found")
    return {"compliance_validation": validation}

class LOCUpdate(BaseModel):
    """Request model for updating LOC metrics"""
    pass  # Trigger recalculation

@router.post("/task/{task_id}/loc")
def update_task_loc(task_id: str, update: Optional[LOCUpdate] = None):
    """Update LOC metrics for a task"""
    result = AE.update_task_loc(task_id)
    if not result:
        raise HTTPException(404, "task_not_found")
    return {"loc_metrics": result}

class DeploymentEvent(BaseModel):
    """Request model for deployment events"""
    platform: str  # netlify, render, github
    event_type: str  # start, success, failure, progress
    status: str = "unknown"
    metadata: Optional[dict] = None

@router.post("/deployment/event")
async def record_deployment_event(event: DeploymentEvent):
    """
    Record a deployment event and publish to Genesis bus for autonomy monitoring.
    This endpoint integrates autonomy engine with Netlify, Render, and GitHub deployments.
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            return {"status": "skipped", "message": "Genesis bus disabled"}
        
        from datetime import datetime, UTC
        
        # Construct event payload
        deployment_event = {
            "platform": event.platform,
            "event_type": event.event_type,
            "status": event.status,
            "timestamp": datetime.now(UTC).isoformat(),
            "metadata": event.metadata or {}
        }
        
        # Publish to platform-specific topic
        topic = f"deploy.{event.platform.lower()}"
        await genesis_bus.publish(topic, deployment_event)
        
        # Also publish to generic deployment topic based on event type
        if event.event_type in ["start", "starting", "initiated"]:
            await genesis_bus.publish("deploy.platform.start", deployment_event)
        elif event.event_type in ["success", "completed", "deployed"]:
            await genesis_bus.publish("deploy.platform.success", deployment_event)
        elif event.event_type in ["failure", "failed", "error"]:
            await genesis_bus.publish("deploy.platform.failure", deployment_event)
        
        return {
            "status": "success",
            "message": f"Deployment event published to {topic}",
            "event": deployment_event
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to record deployment event: {str(e)}")

@router.get("/deployment/status")
def get_deployment_status():
    """Get deployment monitoring status from autonomy engine"""
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        return {
            "genesis_enabled": genesis_bus.is_enabled(),
            "platforms_monitored": ["netlify", "render", "github"],
            "topics": [
                "deploy.netlify",
                "deploy.render", 
                "deploy.github",
                "deploy.platform.start",
                "deploy.platform.success",
                "deploy.platform.failure"
            ],
            "status": "active" if genesis_bus.is_enabled() else "disabled"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }