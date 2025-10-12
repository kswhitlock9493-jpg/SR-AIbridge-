"""
Autonomy Decision Layer Models
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class Incident(BaseModel):
    """
    Represents an incident that requires autonomous decision-making
    """
    kind: str = Field(..., description="Incident type (e.g., deploy.netlify.preview_failed)")
    source: str = Field(..., description="Source of the incident (e.g., github, render, netlify)")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional incident details")
    timestamp: Optional[str] = Field(default=None, description="Incident timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "kind": "deploy.netlify.preview_failed",
                "source": "github",
                "details": {"run_id": "12345678"}
            }
        }


class Decision(BaseModel):
    """
    Represents an autonomous decision made by the Governor
    """
    action: str = Field(..., description="Action to take (NOOP, RETRY, REPAIR_CONFIG, REPAIR_CODE, SYNC_ENVS, ROLLBACK, ESCALATE)")
    reason: str = Field(..., description="Reason for the decision")
    targets: Optional[List[str]] = Field(default=None, description="Target platforms or components")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional decision metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "REPAIR_CONFIG",
                "reason": "preview_failed",
                "targets": ["netlify"]
            }
        }
