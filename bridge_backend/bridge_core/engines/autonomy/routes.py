from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
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

class StatusUpdate(BaseModel):
    status: str
    result: Optional[dict] = None

@router.post("/task")
def create_task(req: TaskIn):
    tc = AE.create_task(
        req.project, 
        req.captain, 
        req.objective, 
        req.permissions, 
        req.mode,
        req.verify_originality
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