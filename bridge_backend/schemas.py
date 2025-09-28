"""
Pydantic schemas for SR-AIbridge API
Separated from SQLAlchemy models for clean architecture
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# === Guardian Schemas ===
class GuardianCreate(BaseModel):
    """Schema for creating a guardian"""
    name: str = Field(default="System Guardian", description="Guardian name")
    status: str = Field(default="active", description="Guardian status")


class GuardianResponse(BaseModel):
    """Schema for guardian API responses"""
    id: int
    name: str
    status: str
    last_selftest: Optional[datetime] = None
    last_action: Optional[str] = None
    health_score: float
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === Vault Log Schemas ===
class VaultLogCreate(BaseModel):
    """Schema for creating vault logs"""
    agent_name: str = Field(description="Name of the agent creating the log")
    action: str = Field(description="Action performed")
    details: str = Field(description="Detailed description of the action")
    log_level: str = Field(default="info", description="Log level (info, warning, error)")


class VaultLogResponse(BaseModel):
    """Schema for vault log API responses"""
    id: int
    agent_name: str
    action: str
    details: str
    log_level: str
    timestamp: datetime
    guardian_id: Optional[int] = None

    class Config:
        from_attributes = True


# === Mission Schemas ===
class MissionCreate(BaseModel):
    """Schema for creating missions"""
    title: str = Field(description="Mission title")
    description: str = Field(default="", description="Mission description")
    status: str = Field(default="active", description="Mission status")
    priority: str = Field(default="normal", description="Mission priority")
    objectives: Optional[str] = Field(default=None, description="Mission objectives as JSON string")


class MissionUpdate(BaseModel):
    """Schema for updating missions"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    progress: Optional[int] = None
    objectives: Optional[str] = None


class MissionResponse(BaseModel):
    """Schema for mission API responses"""
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    agent_id: Optional[int] = None  
    assigned_agents: Optional[str] = None
    progress: int
    start_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    objectives: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === Agent Schemas ===
class AgentCreate(BaseModel):
    """Schema for creating agents"""
    name: str = Field(description="Agent name")
    endpoint: Optional[str] = Field(default=None, description="Agent endpoint URL")
    capabilities: Optional[str] = Field(default="", description="Agent capabilities as JSON string")
    location: Optional[str] = Field(default=None, description="Agent location")


class AgentUpdate(BaseModel):
    """Schema for updating agents"""
    name: Optional[str] = None
    endpoint: Optional[str] = None
    capabilities: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    health_score: Optional[float] = None


class AgentResponse(BaseModel):
    """Schema for agent API responses"""
    id: int
    name: str
    endpoint: Optional[str] = None
    capabilities: Optional[str] = None
    status: str
    last_heartbeat: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    health_score: float
    location: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# === System Status Schemas ===
class DatabaseHealthResponse(BaseModel):
    """Schema for database health responses"""
    status: str
    connection: str
    health_score: float
    counts: Dict[str, int]
    message: str


class SystemStatusResponse(BaseModel):
    """Schema for system status responses"""
    service: str
    version: str
    status: str
    admiral: str
    agents_online: int
    agentsOnline: int  # Alternative naming for frontend compatibility
    active_missions: int
    activeMissions: int  # Alternative naming for frontend compatibility
    total_agents: int
    total_missions: int
    fleet_count: int
    vault_logs: int
    system_health: str
    database: Dict[str, Any]
    features: Dict[str, bool]
    timestamp: str


class HealthCheckResponse(BaseModel):
    """Schema for health check responses"""
    status: str
    service: str
    version: str
    database: Optional[str] = None
    error: Optional[str] = None
    timestamp: str
    self_heal_available: Optional[bool] = None


# === Captain Message Schemas ===
class CaptainMessageCreate(BaseModel):
    """Schema for creating captain messages"""
    from_: str = Field(alias="from", description="Message sender")
    to: str = Field(description="Message recipient")
    message: str = Field(description="Message content")


class CaptainMessageResponse(BaseModel):
    """Schema for captain message responses"""
    id: Optional[int] = None
    from_: str = Field(alias="from")
    to: str
    message: str
    timestamp: datetime

    class Config:
        populate_by_name = True


# === Fleet Schemas ===
class FleetShipResponse(BaseModel):
    """Schema for fleet ship responses"""
    id: int
    name: str
    class_: str = Field(alias="class")
    captain: str
    status: str
    location: str
    mission: Optional[str] = None

    class Config:
        populate_by_name = True


# === Activity Feed Schemas ===
class ActivityResponse(BaseModel):
    """Schema for activity feed responses"""
    id: Optional[int] = None
    type: str
    agent: str
    action: str
    details: str
    timestamp: datetime
    level: str = "info"


# === API Response Schemas ===
class SuccessResponse(BaseModel):
    """Generic success response schema"""
    status: str = "success"
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ErrorResponse(BaseModel):
    """Generic error response schema"""
    status: str = "error"
    error: str
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    self_heal_available: bool = True


class ListResponse(BaseModel):
    """Generic list response schema"""
    status: str = "success"
    count: int
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())