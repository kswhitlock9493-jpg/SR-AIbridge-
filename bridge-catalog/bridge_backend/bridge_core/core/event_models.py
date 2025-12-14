"""
Core event models for unified event bus
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime


class BridgeEvent(BaseModel):
    """Base event model"""
    kind: str
    timestamp: str
    payload: Optional[Dict[str, Any]] = None


class HeritageEvent(BridgeEvent):
    """Heritage subsystem event"""
    pass


class MASEvent(BridgeEvent):
    """Multi-Agent System event"""
    task_id: Optional[str] = None
    agent: Optional[str] = None


class FederationEvent(BridgeEvent):
    """Federation event"""
    node_id: Optional[str] = None
    

class FaultEvent(BridgeEvent):
    """Fault injection event"""
    message_id: Optional[str] = None


class HealEvent(BridgeEvent):
    """Self-healing event"""
    original_message: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None


class AnchorEvent(BridgeEvent):
    """Agent anchor event"""
    agent: str


class MetricsUpdate(BaseModel):
    """Metrics update event"""
    kind: str = "metrics.update"
    queue: int = 0
    active: int = 0
    completed: int = 0
    win_rates: Dict[str, float] = {}
    health: Dict[str, float] = {}
