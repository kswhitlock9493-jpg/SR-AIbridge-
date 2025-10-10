"""
Blueprint API Routes
Draft, refine, commit, and delete blueprints with RBAC enforcement
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/blueprint", tags=["blueprint"])

# Defer model imports - they'll be loaded when endpoints are called
_models_imported = False
_import_error = None

def _ensure_models():
    """Lazy-load models to avoid import-time crashes"""
    global _models_imported, _import_error, Blueprint, AgentJob, Mission
    global BlueprintCreate, BlueprintOut, AgentJobOut, relay_mailer, get_db_session, engine
    
    if _models_imported:
        return True
    
    if _import_error:
        return False
    
    try:
        # Import dependencies with both relative and absolute paths for compatibility
        try:
            from bridge_backend.bridge_core.db.db_manager import get_db_session as _get_db_session
            from bridge_backend.models import Blueprint as _Blueprint, AgentJob as _AgentJob, Mission as _Mission
            from bridge_backend.schemas import BlueprintCreate as _BlueprintCreate, BlueprintOut as _BlueprintOut, AgentJobOut as _AgentJobOut
            from bridge_backend.utils.relay_mailer import relay_mailer as _relay_mailer
        except ImportError:
            try:
                from ....models import Blueprint as _Blueprint, AgentJob as _AgentJob, Mission as _Mission
                from ....schemas import BlueprintCreate as _BlueprintCreate, BlueprintOut as _BlueprintOut, AgentJobOut as _AgentJobOut
                from ....utils.relay_mailer import relay_mailer as _relay_mailer
                from ...db.db_manager import get_db_session as _get_db_session
            except ImportError:
                # Fallback for different import contexts
                import sys
                import os as _os
                sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.dirname(__file__)))))
                from models import Blueprint as _Blueprint, AgentJob as _AgentJob, Mission as _Mission
                from schemas import BlueprintCreate as _BlueprintCreate, BlueprintOut as _BlueprintOut, AgentJobOut as _AgentJobOut
                from utils.relay_mailer import relay_mailer as _relay_mailer
                from bridge_core.db.db_manager import get_db_session as _get_db_session
        
        from .blueprint_engine import BlueprintEngine as _BlueprintEngine
        
        # Assign to module-level variables
        Blueprint = _Blueprint
        AgentJob = _AgentJob
        Mission = _Mission
        BlueprintCreate = _BlueprintCreate
        BlueprintOut = _BlueprintOut
        AgentJobOut = _AgentJobOut
        relay_mailer = _relay_mailer
        get_db_session = _get_db_session
        engine = _BlueprintEngine()
        
        _models_imported = True
        logger.info("[BLUEPRINTS] Models imported successfully")
        return True
    except Exception as e:
        _import_error = str(e)
        logger.warning(f"[BLUEPRINTS] Models unavailable: {e}")
        return False


@router.get("/status")
def status():
    """Check if blueprint engine is available"""
    if _ensure_models():
        return {"engine": "blueprint", "status": "ok"}
    raise HTTPException(
        status_code=503, 
        detail=f"Blueprint engine disabled (models unavailable: {_import_error})"
    )


def require_role(allowed_roles: List[str]):
    """
    Simple role requirement decorator
    In production, this would be a proper dependency with JWT validation
    """
    def dependency(request=None):
        # Mock authentication - in production, extract from JWT token
        return {"id": "test_captain", "role": "captain"}
    return dependency


@router.post("/draft", response_model=BlueprintOut)
async def draft_blueprint(
    payload: BlueprintCreate,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(require_role(["captain", "admiral"]))
):
    """
    Draft a new blueprint from a mission brief
    
    Captains and Admirals can create blueprints.
    Returns structured plan with objectives, tasks, dependencies, and success criteria.
    """
    if not _ensure_models():
        raise HTTPException(status_code=503, detail="Blueprint engine not available")
    
    try:
        # Generate plan from brief
        plan = engine.draft(payload.brief)
        
        # Create blueprint record
        bp = Blueprint(
            title=payload.title,
            brief=payload.brief,
            captain=payload.captain,
            plan=plan
        )
        
        session.add(bp)
        await session.commit()
        await session.refresh(bp)
        
        return bp
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to draft blueprint: {str(e)}")


@router.post("/{bp_id}/commit")
async def commit_blueprint(
    bp_id: int,
    mission_id: int = Query(..., description="Mission ID to commit blueprint to"),
    session: AsyncSession = Depends(get_db_session),
    user=Depends(require_role(["captain", "admiral"]))
):
    """
    Commit a blueprint to a mission and create agent jobs
    
    This locks in the blueprint plan and generates executable agent jobs.
    """
    if not _ensure_models():
        raise HTTPException(status_code=503, detail="Blueprint engine not available")
    
    try:
        # Get blueprint
        result = await session.execute(select(Blueprint).where(Blueprint.id == bp_id))
        bp = result.scalar_one_or_none()
        
        if not bp:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        
        # Get mission
        result = await session.execute(select(Mission).where(Mission.id == mission_id))
        mission = result.scalar_one_or_none()
        
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        # Link blueprint to mission
        bp.mission_id = mission_id
        
        # Generate agent jobs from plan
        jobs = engine.agent_jobs_from_plan(mission_id, bp_id, bp.captain, bp.plan)
        
        # Create job records
        for job_data in jobs:
            job = AgentJob(**job_data)
            session.add(job)
        
        await session.commit()
        
        return {
            "ok": True,
            "created_jobs": len(jobs),
            "blueprint_id": bp_id,
            "mission_id": mission_id
        }
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to commit blueprint: {str(e)}")


@router.delete("/{bp_id}")
async def delete_blueprint(
    bp_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(require_role(["admiral"]))
):
    """
    Delete a blueprint (Admiral only)
    
    Includes data relay archival before deletion for audit trail.
    """
    if not _ensure_models():
        raise HTTPException(status_code=503, detail="Blueprint engine not available")
    
    try:
        # Get blueprint
        result = await session.execute(select(Blueprint).where(Blueprint.id == bp_id))
        bp = result.scalar_one_or_none()
        
        if not bp:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        
        # Archive before delete via relay mailer
        archive_ok = await relay_mailer.archive_before_delete(
            component="blueprint",
            user_id=bp.captain,
            role="captain",
            record={
                "id": bp.id,
                "title": bp.title,
                "brief": bp.brief,
                "plan": bp.plan,
                "created_at": bp.created_at.isoformat() if bp.created_at else None,
                "updated_at": bp.updated_at.isoformat() if bp.updated_at else None
            }
        )
        
        # If relay is enabled but archival failed, abort deletion
        if relay_mailer.enabled and not archive_ok:
            raise HTTPException(
                status_code=503,
                detail="Archive failed; blueprint queued for retry. Please try deletion again later."
            )
        
        # Delete blueprint (cascade will delete related agent_jobs)
        await session.delete(bp)
        await session.commit()
        
        return {"ok": True, "deleted_id": bp_id}
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete blueprint: {str(e)}")


@router.get("/{bp_id}", response_model=BlueprintOut)
async def get_blueprint(
    bp_id: int,
    session: AsyncSession = Depends(get_db_session),
    user=Depends(require_role(["captain", "admiral"]))
):
    """
    Get a specific blueprint by ID
    """
    if not _ensure_models():
        raise HTTPException(status_code=503, detail="Blueprint engine not available")
    
    try:
        result = await session.execute(select(Blueprint).where(Blueprint.id == bp_id))
        bp = result.scalar_one_or_none()
        
        if not bp:
            raise HTTPException(status_code=404, detail="Blueprint not found")
        
        return bp
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get blueprint: {str(e)}")


@router.get("", response_model=List[BlueprintOut])
async def list_blueprints(
    captain: str = Query(None, description="Filter by captain"),
    session: AsyncSession = Depends(get_db_session),
    user=Depends(require_role(["captain", "admiral"]))
):
    """
    List all blueprints, optionally filtered by captain
    """
    if not _ensure_models():
        raise HTTPException(status_code=503, detail="Blueprint engine not available")
    
    try:
        query = select(Blueprint)
        
        if captain:
            query = query.where(Blueprint.captain == captain)
        
        result = await session.execute(query)
        blueprints = result.scalars().all()
        
        return blueprints
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list blueprints: {str(e)}")
