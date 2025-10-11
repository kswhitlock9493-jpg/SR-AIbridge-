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
    files: Optional[List[str]] = None
    validate_compliance: bool = True

class StatusUpdate(BaseModel):
    status: str
    result: Optional[dict] = None

class LOCUpdate(BaseModel):
    total_lines: int
    files_counted: int
    by_extension: dict

@router.post("/task")
def create_task(req: TaskIn):
    tc = AE.create_task(
        req.project, req.captain, req.objective, req.permissions, req.mode,
        files=req.files, validate_compliance=req.validate_compliance
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
def get_compliance(task_id: str):
    """Get compliance validation for a task"""
    validation = AE.get_compliance_validation(task_id)
    if not validation:
        raise HTTPException(404, "validation_not_found")
    return {"validation": validation}

@router.post("/task/{task_id}/loc")
def update_loc(task_id: str, update: LOCUpdate):
    """Update LOC metrics for a task"""
    tc = AE.update_task_loc(task_id, update.dict())
    if not tc:
        raise HTTPException(404, "task_not_found")
    return {"task": tc.__dict__}