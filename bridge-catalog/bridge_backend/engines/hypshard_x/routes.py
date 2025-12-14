"""
HXO FastAPI Routes
API endpoints for plan submission, status, and control
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
import uuid

from .models import HXOPlan, HXOStage, PlanStatus
from .core import get_hxo_core

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/hxo", tags=["HXO"])


def check_admiral_permission():
    """Check if user has admiral permission (mock for now)"""
    # In a real implementation, this would check RBAC
    # For now, always allow
    return True


@router.post("/plan")
async def create_plan(
    plan_request: Dict[str, Any],
    is_admiral: bool = Depends(check_admiral_permission)
) -> Dict[str, Any]:
    """
    Create an HXO plan from a request.
    Admiral-only endpoint.
    
    Request body:
    {
        "name": "deploy_full_stack",
        "stages": [
            {
                "id": "pack_backend",
                "kind": "deploy.pack",
                "slo_ms": 120000
            }
        ],
        "constraints": {"max_shards": 500000}
    }
    """
    if not is_admiral:
        raise HTTPException(status_code=403, detail="Admiral permission required")
    
    try:
        # Generate plan ID
        plan_id = str(uuid.uuid4())
        
        # Parse stages
        stages = []
        for stage_data in plan_request.get("stages", []):
            stage = HXOStage(**stage_data)
            stages.append(stage)
        
        # Create plan
        plan = HXOPlan(
            plan_id=plan_id,
            name=plan_request["name"],
            stages=stages,
            constraints=plan_request.get("constraints", {}),
            submitted_by=plan_request.get("submitted_by", "admiral")
        )
        
        return {
            "plan_id": plan_id,
            "name": plan.name,
            "stages": len(stages),
            "status": "created"
        }
    
    except Exception as e:
        logger.error(f"[HXO API] Failed to create plan: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/submit")
async def submit_plan(
    submit_request: Dict[str, Any],
    is_admiral: bool = Depends(check_admiral_permission)
) -> Dict[str, Any]:
    """
    Submit a plan for execution.
    Admiral-only endpoint.
    
    Request body:
    {
        "plan_id": "..."
    }
    """
    if not is_admiral:
        raise HTTPException(status_code=403, detail="Admiral permission required")
    
    try:
        plan_id = submit_request["plan_id"]
        
        # For now, we'll need to recreate the plan since we don't have a plan store yet
        # In a full implementation, plans would be stored between create and submit
        raise HTTPException(
            status_code=501,
            detail="Plan submission requires plan storage - use create_and_submit instead"
        )
    
    except KeyError:
        raise HTTPException(status_code=400, detail="plan_id required")
    except Exception as e:
        logger.error(f"[HXO API] Failed to submit plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-and-submit")
async def create_and_submit_plan(
    plan_request: Dict[str, Any],
    is_admiral: bool = Depends(check_admiral_permission)
) -> Dict[str, Any]:
    """
    Create and immediately submit a plan for execution.
    Admiral-only endpoint.
    
    Combines /plan and /submit into one call for convenience.
    """
    if not is_admiral:
        raise HTTPException(status_code=403, detail="Admiral permission required")
    
    try:
        # Generate plan ID
        plan_id = str(uuid.uuid4())
        
        # Parse stages
        stages = []
        for stage_data in plan_request.get("stages", []):
            stage = HXOStage(**stage_data)
            stages.append(stage)
        
        # Create plan
        plan = HXOPlan(
            plan_id=plan_id,
            name=plan_request["name"],
            stages=stages,
            constraints=plan_request.get("constraints", {}),
            submitted_by=plan_request.get("submitted_by", "admiral")
        )
        
        # Submit plan
        hxo = get_hxo_core()
        submitted_plan_id = await hxo.submit_plan(plan)
        
        # Get initial status
        status = await hxo.get_status(submitted_plan_id)
        
        return {
            "plan_id": submitted_plan_id,
            "name": plan.name,
            "status": "submitted",
            "merkle_seed": status.merkle_root if status else None,
            "total_shards": status.total_shards if status else 0
        }
    
    except Exception as e:
        logger.error(f"[HXO API] Failed to create and submit plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{plan_id}")
async def get_plan_status(plan_id: str) -> Dict[str, Any]:
    """
    Get live status of a plan.
    
    Returns:
    {
        "plan_id": "...",
        "plan_name": "...",
        "total_shards": 100,
        "pending_shards": 10,
        "done_shards": 90,
        "failed_shards": 0,
        "eta_seconds": 30.5
    }
    """
    try:
        hxo = get_hxo_core()
        status = await hxo.get_status(plan_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        return status.model_dump()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HXO API] Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/abort/{plan_id}")
async def abort_plan(
    plan_id: str,
    is_admiral: bool = Depends(check_admiral_permission)
) -> Dict[str, Any]:
    """
    Abort a running plan.
    Admiral-only endpoint.
    """
    if not is_admiral:
        raise HTTPException(status_code=403, detail="Admiral permission required")
    
    try:
        hxo = get_hxo_core()
        success = await hxo.abort_plan(plan_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        return {
            "plan_id": plan_id,
            "status": "aborted"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HXO API] Failed to abort plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/replay/{plan_id}")
async def replay_plan(
    plan_id: str,
    is_admiral: bool = Depends(check_admiral_permission)
) -> Dict[str, Any]:
    """
    Replay failed subtrees of a plan.
    Admiral-only endpoint.
    """
    if not is_admiral:
        raise HTTPException(status_code=403, detail="Admiral permission required")
    
    try:
        # TODO: Implement replay logic
        raise HTTPException(status_code=501, detail="Replay not yet implemented")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HXO API] Failed to replay plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{plan_id}")
async def get_plan_report(plan_id: str) -> Dict[str, Any]:
    """
    Get final report for a plan (includes Merkle root and Truth cert).
    
    Returns:
    {
        "plan_id": "...",
        "plan_name": "...",
        "merkle_root": "abc123...",
        "truth_certified": true,
        "total_shards": 100,
        "done_shards": 100,
        "failed_shards": 0
    }
    """
    try:
        hxo = get_hxo_core()
        status = await hxo.get_status(plan_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        report = status.model_dump()
        report["report_type"] = "final"
        
        return report
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[HXO API] Failed to get report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
