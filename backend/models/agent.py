from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class AgentStatus(str, Enum):
    """Agent status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"


class AgentCapability(BaseModel):
    """Agent capability model"""
    name: str
    version: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class Agent(BaseModel):
    """Agent model with heartbeat and capability tracking"""
    id: str
    name: str
    endpoint: str
    status: AgentStatus = AgentStatus.OFFLINE
    capabilities: List[AgentCapability] = []
    last_heartbeat: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentRegistration(BaseModel):
    """Model for agent registration requests"""
    name: str
    endpoint: str
    capabilities: List[AgentCapability] = []
    metadata: Optional[Dict[str, Any]] = None


class AgentHeartbeat(BaseModel):
    """Model for agent heartbeat requests"""
    agent_id: str
    status: AgentStatus = AgentStatus.ONLINE
    metadata: Optional[Dict[str, Any]] = None


class TaskDelegation(BaseModel):
    """Model for task delegation requests"""
    task_id: str
    required_capability: str
    task_data: Dict[str, Any]
    priority: int = 1