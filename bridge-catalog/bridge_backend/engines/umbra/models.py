"""
Umbra Triage Mesh Models
Schemas for tickets, incidents, heal plans, and reports
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class TriageSeverity(str, Enum):
    """Severity levels for triage tickets"""
    CRITICAL = "critical"
    HIGH = "high"
    WARNING = "warning"
    INFO = "info"


class TriageStatus(str, Enum):
    """Status of triage tickets"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    HEALED = "healed"
    CLOSED = "closed"
    FAILED = "failed"


class TriageKind(str, Enum):
    """Type of triage signal"""
    BUILD = "build"
    DEPLOY = "deploy"
    RUNTIME = "runtime"
    API = "api"
    ENDPOINT = "endpoint"
    WEBHOOK = "webhook"


class HealAction(BaseModel):
    """Individual heal action"""
    action_type: str = Field(..., description="Type of healing action")
    target: str = Field(..., description="Target of the action")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in seconds")


class HealPlan(BaseModel):
    """Healing plan for a triage ticket"""
    plan_id: str = Field(..., description="Unique plan identifier")
    ticket_id: str = Field(..., description="Associated ticket ID")
    actions: List[HealAction] = Field(default_factory=list, description="List of heal actions")
    parity_prechecks: List[str] = Field(default_factory=list, description="Parity checks to run before healing")
    truth_policy: str = Field(default="standard", description="Truth certification policy")
    rollback_plan: Optional[Dict[str, Any]] = Field(None, description="Rollback plan if healing fails")
    certified: bool = Field(default=False, description="Whether plan is Truth-certified")
    certification_signature: Optional[str] = Field(None, description="Truth certification signature")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Incident(BaseModel):
    """Incident extracted from signals"""
    incident_id: str = Field(..., description="Unique incident identifier")
    kind: TriageKind = Field(..., description="Type of incident")
    severity: TriageSeverity = Field(..., description="Severity level")
    source: str = Field(..., description="Source of the incident (render, netlify, github, etc.)")
    message: str = Field(..., description="Incident message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TriageTicket(BaseModel):
    """Triage ticket combining correlated incidents"""
    ticket_id: str = Field(..., description="Unique ticket identifier (e.g., UM-2025-10-12-0012)")
    kind: TriageKind = Field(..., description="Primary kind of issue")
    source: str = Field(..., description="Primary source")
    signals: List[str] = Field(default_factory=list, description="List of signal types")
    severity: TriageSeverity = Field(..., description="Ticket severity")
    incidents: List[Incident] = Field(default_factory=list, description="Correlated incidents")
    status: TriageStatus = Field(default=TriageStatus.OPEN, description="Ticket status")
    heal_plan: Optional[HealPlan] = Field(None, description="Associated heal plan")
    healed_at: Optional[datetime] = Field(None, description="When ticket was healed")
    closed_at: Optional[datetime] = Field(None, description="When ticket was closed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True


class Report(BaseModel):
    """Triage run report"""
    report_id: str = Field(..., description="Unique report identifier")
    run_timestamp: datetime = Field(default_factory=datetime.utcnow)
    tickets_opened: int = Field(default=0, description="Number of tickets opened")
    tickets_healed: int = Field(default=0, description="Number of tickets healed")
    tickets_failed: int = Field(default=0, description="Number of tickets that failed healing")
    critical_count: int = Field(default=0, description="Number of critical issues")
    warning_count: int = Field(default=0, description="Number of warnings")
    heal_plans_generated: int = Field(default=0, description="Number of heal plans generated")
    heal_plans_applied: int = Field(default=0, description="Number of heal plans applied")
    duration_seconds: float = Field(default=0.0, description="Duration of the run in seconds")
    summary: str = Field(default="", description="Summary of the run")
    tickets: List[TriageTicket] = Field(default_factory=list, description="Tickets from this run")
    
    class Config:
        use_enum_values = True
