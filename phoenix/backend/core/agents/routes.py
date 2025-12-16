"""
Phoenix Protocol - Agent Management
Built following BUILD_DOSSIER.md specifications
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List, Optional

import db
from models import Agent
from schemas import AgentCreate, AgentResponse

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=List[AgentResponse])
async def list_agents(
    role: Optional[str] = None,
    status: Optional[str] = None,
    session: AsyncSession = Depends(db.get_session)
):
    """List all agents with optional filtering"""
    query = select(Agent)
    
    if role:
        query = query.where(Agent.role == role)
    if status:
        query = query.where(Agent.status == status)
    
    result = await session.execute(query)
    agents = result.scalars().all()
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    session: AsyncSession = Depends(db.get_session)
):
    """Get specific agent by ID"""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(
    agent_data: AgentCreate,
    session: AsyncSession = Depends(db.get_session)
):
    """Register a new agent"""
    
    # Check if agent name already exists
    result = await session.execute(select(Agent).where(Agent.name == agent_data.name))
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Agent name already exists")
    
    # Validate role
    if agent_data.role not in ["captain", "agent"]:
        raise HTTPException(status_code=400, detail="Role must be 'captain' or 'agent'")
    
    # Create agent
    agent = Agent(
        name=agent_data.name,
        role=agent_data.role,
        captain=agent_data.captain,
        status=agent_data.status,
        capabilities=agent_data.capabilities,
        last_heartbeat=datetime.utcnow()
    )
    
    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    
    return agent


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    session: AsyncSession = Depends(db.get_session)
):
    """Delete an agent"""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    await session.delete(agent)
    await session.commit()
    
    return {"status": "deleted", "agent_id": agent_id}


@router.post("/{agent_id}/heartbeat")
async def agent_heartbeat(
    agent_id: int,
    session: AsyncSession = Depends(db.get_session)
):
    """Update agent heartbeat"""
    result = await session.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.last_heartbeat = datetime.utcnow()
    agent.status = "online"
    
    await session.commit()
    
    return {"status": "heartbeat_updated", "timestamp": agent.last_heartbeat}
