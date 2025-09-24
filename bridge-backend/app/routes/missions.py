"""
Mission management endpoints for SR-AIbridge
Handles mission creation, listing, and task aliases
"""
from fastapi import APIRouter, HTTPException
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

class Agent(BaseModel):
    id: Optional[int] = None
    name: str
    endpoint: str
    status: str = "online"
    capabilities: List[str] = []
    last_heartbeat: Optional[datetime] = None

class AgentCreate(BaseModel):
    name: str
    endpoint: str
    capabilities: List[str] = []

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

# Agent endpoints
@router.get("/agents", response_model=List[Agent])
async def list_agents():
    """Get all registered agents"""
    from ..main import storage
    return [Agent(**agent) for agent in storage.agents]

@router.post("/agents", response_model=Agent)
async def register_agent(agent_create: AgentCreate):
    """Register a new agent"""
    from ..main import storage
    
    agent_data = {
        "id": storage.get_next_id(),
        "name": agent_create.name,
        "endpoint": agent_create.endpoint,
        "status": "online",
        "capabilities": agent_create.capabilities,
        "last_heartbeat": datetime.utcnow()
    }
    storage.agents.append(agent_data)
    return Agent(**agent_data)

@router.post("/agents/register", response_model=Agent)
async def register_agent_alt(agent_create: AgentCreate):
    """Register a new agent (alternative endpoint)"""
    return await register_agent(agent_create)

@router.delete("/agents/{agent_id}")
async def remove_agent(agent_id: int):
    """Remove an agent by ID"""
    from ..main import storage
    
    for i, agent in enumerate(storage.agents):
        if agent.get("id") == agent_id:
            del storage.agents[i]
            return {"message": f"Agent {agent_id} removed successfully"}
    
    raise HTTPException(status_code=404, detail="Agent not found")