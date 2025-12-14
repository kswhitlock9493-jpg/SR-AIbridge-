"""
Env Steward API Routes
Admiral-tier environment orchestration endpoints
"""

from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional, List
import logging
from .core import steward
from .models import PlanRequest, ApplyRequest, DiffReport, Plan, ApplyResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/steward", tags=["steward"])


@router.post("/diff", response_model=DiffReport)
async def diff(
    providers: List[str] = Query(default=["render", "netlify", "github"]),
    dry_run: bool = Query(default=True)
):
    """
    Compute environment drift against Blueprint EnvSpec
    
    - **providers**: List of providers to check
    - **dry_run**: If True, don't make any changes
    
    Returns computed diff matched to Blueprint EnvSpec.
    """
    if not steward.is_enabled():
        raise HTTPException(503, "Steward engine is disabled")
    
    try:
        return await steward.diff(providers, dry_run=dry_run)
    except Exception as e:
        logger.exception(f"Diff failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/plan", response_model=Plan)
async def plan(req: PlanRequest):
    """
    Create an execution plan for environment changes
    
    - **providers**: List of providers to plan for
    - **strategy**: Planning strategy (safe-phased, immediate, etc.)
    
    Returns a signed plan (hash, mutation_window_id).
    """
    if not steward.is_enabled():
        raise HTTPException(503, "Steward engine is disabled")
    
    try:
        return await steward.plan(req.providers, strategy=req.strategy)
    except Exception as e:
        logger.exception(f"Plan creation failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/cap/issue")
async def issue_cap(
    reason: str = Query(..., description="Reason for capability"),
    ttl_seconds: int = Query(default=600, description="Capability lifetime in seconds"),
    window_id: Optional[str] = Query(default=None, description="Optional window to bind to"),
    x_actor: Optional[str] = Header(default=None, alias="X-Actor")
):
    """
    Issue a capability token (ADMIRAL-TIER ONLY)
    
    - **reason**: Reason for capability (for audit)
    - **ttl_seconds**: Time to live in seconds (default: 600)
    - **window_id**: Optional mutation window to bind to
    
    Requires admiral role. Returns cap_token (ephemeral).
    """
    if not steward.is_enabled():
        raise HTTPException(503, "Steward engine is disabled")
    
    # Get owner handle from environment
    import os
    owner_handle = os.getenv("STEWARD_OWNER_HANDLE", "")
    
    # Default to owner if no actor provided (for testing)
    actor = x_actor or owner_handle
    
    try:
        cap_token = await steward.issue_cap(
            actor=actor,
            reason=reason,
            ttl_seconds=ttl_seconds,
            window_id=window_id
        )
        return {
            "cap_token": cap_token,
            "ttl_seconds": ttl_seconds,
            "actor": actor,
            "reason": reason
        }
    except PermissionError as e:
        raise HTTPException(403, str(e))
    except Exception as e:
        logger.exception(f"Capability issuance failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/apply", response_model=ApplyResult)
async def apply(
    req: ApplyRequest,
    x_bridge_cap: Optional[str] = Header(default=None, alias="X-Bridge-Cap"),
    x_actor: Optional[str] = Header(default=None, alias="X-Actor")
):
    """
    Execute a plan (ADMIRAL-TIER ONLY)
    
    - **plan**: The plan to execute
    - **confirm**: Must be True to execute
    
    Headers:
    - **X-Bridge-Cap**: Capability token (required)
    - **X-Actor**: Actor name (required)
    
    Executes via adapters; publishes steward.result.
    """
    if not steward.is_enabled():
        raise HTTPException(503, "Steward engine is disabled")
    
    if not steward.is_write_enabled():
        raise HTTPException(403, "Write mode is disabled (STEWARD_WRITE_ENABLED=false)")
    
    if not req.confirm:
        raise HTTPException(400, "Must confirm apply operation")
    
    if not x_bridge_cap:
        raise HTTPException(401, "Missing X-Bridge-Cap header")
    
    if not x_actor:
        raise HTTPException(401, "Missing X-Actor header")
    
    try:
        return await steward.apply(req.plan, x_bridge_cap, x_actor)
    except PermissionError as e:
        raise HTTPException(403, str(e))
    except Exception as e:
        logger.exception(f"Apply failed: {e}")
        raise HTTPException(500, str(e))


@router.get("/status")
async def status():
    """
    Get Steward engine status
    
    Returns current configuration and state.
    """
    import os
    return {
        "enabled": steward.is_enabled(),
        "write_enabled": steward.is_write_enabled(),
        "owner_handle": os.getenv("STEWARD_OWNER_HANDLE", ""),
        "cap_ttl_seconds": int(os.getenv("STEWARD_CAP_TTL_SECONDS", "600"))
    }
