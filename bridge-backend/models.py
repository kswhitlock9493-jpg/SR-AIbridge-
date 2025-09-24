"""
SQLAlchemy models for SR-AIbridge
SQLite-first design with Guardian, VaultLog, Mission models
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, func
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

Base = declarative_base()

# SQLAlchemy ORM Models
class Guardian(Base):
    """Guardian system monitoring model"""
    __tablename__ = "guardians"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, default="System Guardian")
    status = Column(String(50), nullable=False, default="active")
    last_selftest = Column(DateTime, nullable=True)
    last_action = Column(String(255), nullable=True)
    health_score = Column(Float, default=100.0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class VaultLog(Base):
    """Vault logging system model"""
    __tablename__ = "vault_logs"
    
    id = Column(Integer, primary_key=True)
    agent_name = Column(String(255), nullable=False)
    action = Column(String(255), nullable=False)
    details = Column(Text, nullable=False)
    log_level = Column(String(50), nullable=False, default="info")
    timestamp = Column(DateTime, server_default=func.now())
    guardian_id = Column(Integer, nullable=True)  # Optional reference to guardian

class Mission(Base):
    """Mission tracking model"""
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    priority = Column(String(50), nullable=False, default="normal")
    agent_id = Column(Integer, nullable=True)
    assigned_agents = Column(Text, nullable=True)  # JSON string for multiple agents
    progress = Column(Integer, default=0)
    start_time = Column(DateTime, nullable=True)
    estimated_completion = Column(DateTime, nullable=True)
    objectives = Column(Text, nullable=True)  # JSON string for objectives list
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Agent(Base):
    """Agent tracking model"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    endpoint = Column(String(255), nullable=True)  # Made optional for seeded agents
    capabilities = Column(Text, nullable=True)  # JSON string
    status = Column(String(50), default="online")
    last_heartbeat = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)  # Alternative to heartbeat
    health_score = Column(Float, default=100.0)
    location = Column(String(255), nullable=True)  # Agent location
    created_at = Column(DateTime, server_default=func.now())

# Pydantic models for API
class GuardianCreate(BaseModel):
    name: str = "System Guardian"
    status: str = "active"

class GuardianResponse(BaseModel):
    id: int
    name: str
    status: str
    last_selftest: Optional[datetime] = None
    last_action: Optional[str] = None
    health_score: float
    active: bool
    created_at: datetime
    updated_at: datetime

class VaultLogCreate(BaseModel):
    agent_name: str
    action: str
    details: str
    log_level: str = "info"

class VaultLogResponse(BaseModel):
    id: int
    agent_name: str
    action: str
    details: str
    log_level: str
    timestamp: datetime
    guardian_id: Optional[int] = None

class MissionCreate(BaseModel):
    title: str
    description: str = ""
    status: str = "active"
    priority: str = "normal"

class MissionResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    agent_id: Optional[int] = None
    progress: int
    created_at: datetime
    updated_at: datetime

class AgentCreate(BaseModel):
    name: str
    endpoint: str
    capabilities: str = ""

class AgentResponse(BaseModel):
    id: int
    name: str
    endpoint: str
    capabilities: Optional[str] = None
    status: str
    last_heartbeat: Optional[datetime] = None
    created_at: datetime