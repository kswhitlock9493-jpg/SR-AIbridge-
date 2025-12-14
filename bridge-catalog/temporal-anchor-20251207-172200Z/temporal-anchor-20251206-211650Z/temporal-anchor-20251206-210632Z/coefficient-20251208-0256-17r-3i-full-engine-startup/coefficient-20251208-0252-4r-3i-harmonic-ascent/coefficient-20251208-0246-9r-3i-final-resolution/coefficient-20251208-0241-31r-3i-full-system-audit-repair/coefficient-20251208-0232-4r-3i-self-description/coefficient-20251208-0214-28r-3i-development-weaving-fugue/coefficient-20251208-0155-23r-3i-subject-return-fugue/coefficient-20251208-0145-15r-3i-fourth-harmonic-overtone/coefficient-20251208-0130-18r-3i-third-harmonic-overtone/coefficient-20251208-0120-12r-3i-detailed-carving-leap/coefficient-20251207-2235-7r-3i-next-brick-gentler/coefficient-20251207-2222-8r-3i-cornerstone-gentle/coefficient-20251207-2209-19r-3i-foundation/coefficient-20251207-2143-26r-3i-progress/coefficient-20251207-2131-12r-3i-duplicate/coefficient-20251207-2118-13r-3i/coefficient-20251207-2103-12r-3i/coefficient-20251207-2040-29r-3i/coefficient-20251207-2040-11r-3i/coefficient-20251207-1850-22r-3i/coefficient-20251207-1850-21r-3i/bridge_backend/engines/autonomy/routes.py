"""
Autonomy Decision Layer Routes

REST API for submitting incidents and triggering autonomous actions.
All routes RBAC-gated behind autonomy:operate (admiral-only by default).
"""

from fastapi import APIRouter, Depends, HTTPException
from .governor import AutonomyGovernor
from .models import Incident, Decision
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/autonomy", tags=["autonomy"])


def require_perm(perm: str):
    """
    Permission dependency for autonomy routes
    
    For now, this is a simple pass-through. In production, this should:
    - Check user role (admiral-only for autonomy:operate)
    - Verify permission scopes
    - Raise HTTPException(403) if unauthorized
    """
    async def _check():
        # TODO: Implement proper RBAC check
        # For now, allow all requests (will be gated by middleware)
        return True
    return _check


@router.post("/incident")
async def submit_incident(
    incident: Incident,
    _=Depends(require_perm("autonomy:operate"))
) -> Dict[str, Any]:
    """
    Submit an incident for autonomous decision-making
    
    Args:
        incident: Incident details (kind, source, details)
        
    Returns:
        Dict with incident, decision, and result
    """
    try:
        gov = AutonomyGovernor()
        decision = await gov.decide(incident)
        result = await gov.execute(decision)
        
        return {
            "incident": incident.model_dump(),
            "decision": decision.model_dump(),
            "result": result
        }
    except Exception as e:
        logger.exception(f"[Autonomy] Incident handling failed: {e}")
        raise HTTPException(status_code=500, detail=f"Incident handling failed: {str(e)}")


@router.post("/trigger")
async def trigger(
    decision: Decision,
    _=Depends(require_perm("autonomy:operate"))
) -> Dict[str, Any]:
    """
    Manually trigger a decision (bypass incident evaluation)
    
    Args:
        decision: Decision to execute
        
    Returns:
        Dict with decision and result
    """
    try:
        gov = AutonomyGovernor()
        result = await gov.execute(decision)
        
        return {
            "decision": decision.model_dump(),
            "result": result
        }
    except Exception as e:
        logger.exception(f"[Autonomy] Decision execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Decision execution failed: {str(e)}")


@router.get("/status")
async def get_status(
    _=Depends(require_perm("autonomy:operate"))
) -> Dict[str, Any]:
    """
    Get autonomy engine status
    
    Returns:
        Dict with status, config, and stats
    """
    import os
    
    return {
        "enabled": os.getenv("AUTONOMY_ENABLED", "true").lower() == "true",
        "config": {
            "max_actions_per_hour": int(os.getenv("AUTONOMY_MAX_ACTIONS_PER_HOUR", "6")),
            "cooldown_minutes": int(os.getenv("AUTONOMY_COOLDOWN_MINUTES", "5")),
            "fail_streak_trip": int(os.getenv("AUTONOMY_FAIL_STREAK_TRIP", "3"))
        },
        "status": "active"
    }


@router.post("/circuit")
async def control_circuit(
    action: str,
    _=Depends(require_perm("autonomy:operate"))
) -> Dict[str, Any]:
    """
    Control circuit breaker state (open/close)
    
    Args:
        action: "open" or "close"
        
    Returns:
        Dict with circuit state
    """
    if action not in ["open", "close"]:
        raise HTTPException(status_code=400, detail="action must be 'open' or 'close'")
    
    # For now, just return status
    # TODO: Implement persistent circuit state
    return {
        "circuit": action,
        "message": f"Circuit breaker {action}d (not yet implemented)"
    }
