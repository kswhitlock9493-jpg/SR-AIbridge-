"""
SQLAlchemy models for SR-AIbridge
SQLite-first design with Guardian, VaultLog, Mission, Agent models
Pydantic schemas have been moved to schemas.py for clean separation
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, func, ForeignKey, JSON, Enum as PgEnum
from datetime import datetime
import enum

Base = declarative_base()

# Enums for AgentJob status
class JobStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"
    skipped = "skipped"

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
    captain = Column(String(255), nullable=True)  # Captain owner of the mission
    role = Column(String(50), nullable=False, default="captain")  # 'captain' or 'agent'
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
    role = Column(String(50), nullable=False, default="agent")  # 'captain' or 'agent'
    captain = Column(String(255), nullable=True)  # If this is a captain's personal agent
    last_heartbeat = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)  # Alternative to heartbeat
    health_score = Column(Float, default=100.0)
    location = Column(String(255), nullable=True)  # Agent location
    created_at = Column(DateTime, server_default=func.now())

class Blueprint(Base):
    """Blueprint planning model for missions"""
    __tablename__ = "blueprints"
    
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True)
    captain = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    brief = Column(Text, nullable=False)
    plan = Column(JSON, nullable=False)  # objectives/tasks/deps/artifacts stored as JSON
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    mission = relationship("Mission", back_populates="blueprint", foreign_keys=[mission_id])
    agent_jobs = relationship("AgentJob", back_populates="blueprint", cascade="all, delete-orphan")

class AgentJob(Base):
    """Agent job tracking for blueprint execution"""
    __tablename__ = "agent_jobs"
    
    id = Column(Integer, primary_key=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False, index=True)
    blueprint_id = Column(Integer, ForeignKey("blueprints.id"), nullable=False)
    captain = Column(String(255), nullable=False, index=True)
    agent_name = Column(String(255), nullable=True, index=True)
    role = Column(String(50), nullable=False, default="agent")  # agent/captain/admiral
    task_key = Column(String(50), nullable=False, index=True)  # e.g., "T2.1"
    task_desc = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="queued")  # Using string for SQLite compatibility
    inputs = Column(JSON, nullable=False, default=dict)
    outputs = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    mission_rel = relationship("Mission", back_populates="agent_jobs", foreign_keys=[mission_id])
    blueprint = relationship("Blueprint", back_populates="agent_jobs", foreign_keys=[blueprint_id])

# Add reverse relationships to Mission
Mission.blueprint = relationship("Blueprint", uselist=False, back_populates="mission")
Mission.agent_jobs = relationship("AgentJob", back_populates="mission_rel")

# Note: Pydantic schemas have been moved to schemas.py for better separation of concerns