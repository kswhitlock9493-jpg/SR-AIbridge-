"""
Mission management endpoints for SR-AIbridge
Handles mission creation, listing, and task aliases
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(tags=["missions"])

# Models (these should eventually be moved to a models module)
class Mission(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    status: str = "active"
    priority: str = "normal"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MissionCreate(BaseModel):
    title: str
    description: str
    status: str = "active"
    priority: str = "normal"

@router.get("/missions", response_model=List[Mission])
async def list_missions():
    """Get all missions"""
    from ..main import storage
    return [Mission(**mission) for mission in storage.missions]

@router.post("/missions", response_model=Mission)
async def create_mission(mission_create: MissionCreate):
    """Create a new mission"""
    from ..main import storage
    
    mission_data = {
        "id": storage.get_next_id(),
        "title": mission_create.title,
        "description": mission_create.description,
        "status": mission_create.status,
        "priority": mission_create.priority,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    storage.missions.append(mission_data)
    return Mission(**mission_data)

# Task aliases for compatibility
@router.get("/tasks")
async def get_tasks():
    """Get tasks (alias for missions for compatibility)"""
    return await list_missions()

@router.post("/tasks")
async def create_task(task_data: dict):
    """Create a new task (alias for mission creation)"""
    mission_create = MissionCreate(
        title=task_data.get("title", "New Task"),
        description=task_data.get("description", ""),
        status="active",
        priority=task_data.get("priority", "normal")
    )
    return await create_mission(mission_create)