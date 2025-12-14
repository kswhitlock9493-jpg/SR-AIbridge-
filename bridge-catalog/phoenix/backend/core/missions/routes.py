"""
Phoenix Protocol - Mission Management
Built following BUILD_DOSSIER.md specifications
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List, Optional

import db
from models import Mission
from schemas import MissionCreate, MissionUpdate, MissionResponse

router = APIRouter(prefix="/missions", tags=["missions"])


@router.get("", response_model=List[MissionResponse])
async def list_missions(
    captain: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    session: AsyncSession = Depends(db.get_session)
):
    """List all missions with optional filtering"""
    query = select(Mission)
    
    if captain:
        query = query.where(Mission.captain == captain)
    if role:
        query = query.where(Mission.role == role)
    if status:
        query = query.where(Mission.status == status)
    if priority:
        query = query.where(Mission.priority == priority)
    
    result = await session.execute(query)
    missions = result.scalars().all()
    return missions


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(
    mission_id: int,
    session: AsyncSession = Depends(db.get_session)
):
    """Get specific mission by ID"""
    result = await session.execute(select(Mission).where(Mission.id == mission_id))
    mission = result.scalar_one_or_none()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    return mission


@router.post("", response_model=MissionResponse, status_code=201)
async def create_mission(
    mission_data: MissionCreate,
    session: AsyncSession = Depends(db.get_session)
):
    """Create a new mission"""
    
    # Validate priority
    if mission_data.priority not in ["low", "medium", "high", "critical"]:
        raise HTTPException(
            status_code=400,
            detail="Priority must be 'low', 'medium', 'high', or 'critical'"
        )
    
    # Validate role
    if mission_data.role not in ["captain", "agent"]:
        raise HTTPException(status_code=400, detail="Role must be 'captain' or 'agent'")
    
    # Create mission
    mission = Mission(
        title=mission_data.title,
        description=mission_data.description,
        priority=mission_data.priority,
        captain=mission_data.captain,
        role=mission_data.role,
        status="pending",
        assigned_agents=[]
    )
    
    session.add(mission)
    await session.commit()
    await session.refresh(mission)
    
    return mission


@router.put("/{mission_id}", response_model=MissionResponse)
async def update_mission(
    mission_id: int,
    mission_update: MissionUpdate,
    session: AsyncSession = Depends(db.get_session)
):
    """Update a mission"""
    result = await session.execute(select(Mission).where(Mission.id == mission_id))
    mission = result.scalar_one_or_none()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    # Update fields if provided
    if mission_update.title is not None:
        mission.title = mission_update.title
    if mission_update.description is not None:
        mission.description = mission_update.description
    if mission_update.priority is not None:
        if mission_update.priority not in ["low", "medium", "high", "critical"]:
            raise HTTPException(status_code=400, detail="Invalid priority")
        mission.priority = mission_update.priority
    if mission_update.status is not None:
        if mission_update.status not in ["pending", "active", "completed", "failed"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        mission.status = mission_update.status
        
        # Set completed_at if status is completed or failed
        if mission_update.status in ["completed", "failed"]:
            mission.completed_at = datetime.utcnow()
    
    mission.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(mission)
    
    return mission


@router.delete("/{mission_id}")
async def delete_mission(
    mission_id: int,
    session: AsyncSession = Depends(db.get_session)
):
    """Delete a mission"""
    result = await session.execute(select(Mission).where(Mission.id == mission_id))
    mission = result.scalar_one_or_none()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    await session.delete(mission)
    await session.commit()
    
    return {"status": "deleted", "mission_id": mission_id}


@router.post("/{mission_id}/assign")
async def assign_agents_to_mission(
    mission_id: int,
    agent_ids: List[int],
    session: AsyncSession = Depends(db.get_session)
):
    """Assign agents to a mission"""
    result = await session.execute(select(Mission).where(Mission.id == mission_id))
    mission = result.scalar_one_or_none()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    # Update assigned agents
    mission.assigned_agents = agent_ids
    mission.updated_at = datetime.utcnow()
    
    # Update status to active if it was pending
    if mission.status == "pending":
        mission.status = "active"
    
    await session.commit()
    
    return {
        "status": "agents_assigned",
        "mission_id": mission_id,
        "agent_ids": agent_ids
    }
