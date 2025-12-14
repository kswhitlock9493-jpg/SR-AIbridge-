"""
Pydantic models for Env Steward
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


class EnvVarChange(BaseModel):
    """Single environment variable change"""
    key: str
    old_value: Optional[str] = None  # Hashed or None for new vars
    new_value: Optional[str] = None  # Hashed or None for deletions
    action: str = Field(..., description="create, update, or delete")
    is_secret: bool = False


class DiffReport(BaseModel):
    """Environment drift report"""
    has_drift: bool
    providers: List[str]
    changes: List[EnvVarChange] = []
    missing_in_render: List[str] = []
    missing_in_netlify: List[str] = []
    missing_in_github: List[str] = []
    extra_in_render: List[str] = []
    extra_in_netlify: List[str] = []
    conflicts: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Plan(BaseModel):
    """Execution plan for environment changes"""
    id: str
    providers: List[str]
    strategy: str = "safe-phased"
    phases: List[Dict[str, Any]] = []
    mutation_window_id: Optional[str] = None
    certified: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ApplyResult(BaseModel):
    """Result of apply operation"""
    ok: bool
    plan_id: str
    changes_applied: int = 0
    change_counts: Dict[str, int] = Field(default_factory=dict)
    rollback_ref: Optional[str] = None
    errors: List[str] = []
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PlanRequest(BaseModel):
    """Request to create a plan"""
    providers: List[str] = ["render", "netlify", "github"]
    strategy: str = "safe-phased"


class ApplyRequest(BaseModel):
    """Request to apply a plan"""
    plan: Plan
    confirm: bool = False
