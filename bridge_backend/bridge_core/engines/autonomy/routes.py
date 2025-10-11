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