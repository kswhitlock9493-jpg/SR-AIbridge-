"""
Phoenix Protocol - Pydantic Schemas
Built following BUILD_DOSSIER.md specifications
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


# Guardian Schemas
class GuardianBase(BaseModel):
    name: str
    status: str = "active"
    capabilities: List[str] = Field(default_factory=list)


class GuardianCreate(GuardianBase):
    pass


class GuardianResponse(GuardianBase):
    id: int
    health_score: float
    last_heartbeat: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Agent Schemas
class AgentBase(BaseModel):
    name: str
    role: str  # captain, agent
    captain: Optional[str] = None
    status: str = "online"
    capabilities: List[str] = Field(default_factory=list)


class AgentCreate(AgentBase):
    pass


class AgentResponse(AgentBase):
    id: int
    last_heartbeat: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Mission Schemas
class MissionBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"  # low, medium, high, critical
    captain: str
    role: str  # captain, agent


class MissionCreate(MissionBase):
    pass


class MissionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class MissionResponse(MissionBase):
    id: int
    status: str
    assigned_agents: List[int] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Vault Log Schemas
class VaultLogCreate(BaseModel):
    level: str  # info, warning, error, critical
    message: str
    source: Optional[str] = None
    log_metadata: Dict[str, Any] = Field(default_factory=dict)  # Renamed from 'metadata'


class VaultLogResponse(VaultLogCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Admiral Key Schemas
class AdmiralKeyCreate(BaseModel):
    key_name: str


class AdmiralKeyResponse(BaseModel):
    id: int
    key_name: str
    public_key: str
    created_at: datetime
    last_used: Optional[datetime] = None

    class Config:
        from_attributes = True


# Fleet Ship Schemas
class FleetShipBase(BaseModel):
    name: str
    role: str
    status: str = "online"
    location: Optional[str] = None
    deployment_status: str = "docked"


class FleetShipCreate(FleetShipBase):
    pass


class FleetShipResponse(FleetShipBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Captain Message Schemas
class CaptainMessageCreate(BaseModel):
    from_captain: str
    to_captain: Optional[str] = None  # None for broadcast
    message: str
    priority: str = "normal"


class CaptainMessageResponse(CaptainMessageCreate):
    id: int
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Health Check Response
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0-phoenix"


class FullHealthResponse(HealthResponse):
    components: Dict[str, str]
    metrics: Dict[str, Any]
