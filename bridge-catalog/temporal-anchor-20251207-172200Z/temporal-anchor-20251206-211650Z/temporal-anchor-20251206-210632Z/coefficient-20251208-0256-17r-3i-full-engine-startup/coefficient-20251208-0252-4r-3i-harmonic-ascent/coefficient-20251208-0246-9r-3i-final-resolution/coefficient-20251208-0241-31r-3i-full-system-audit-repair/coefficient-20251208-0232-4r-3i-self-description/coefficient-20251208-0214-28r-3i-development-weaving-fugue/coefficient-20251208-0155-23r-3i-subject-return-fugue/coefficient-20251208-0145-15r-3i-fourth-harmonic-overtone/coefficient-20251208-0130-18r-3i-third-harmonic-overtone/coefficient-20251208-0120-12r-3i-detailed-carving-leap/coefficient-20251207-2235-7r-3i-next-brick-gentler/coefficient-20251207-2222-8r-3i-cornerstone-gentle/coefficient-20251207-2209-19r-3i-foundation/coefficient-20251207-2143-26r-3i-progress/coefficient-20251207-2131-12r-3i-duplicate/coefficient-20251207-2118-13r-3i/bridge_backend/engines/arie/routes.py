"""
ARIE Routes - API endpoints for autonomous repository integrity
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from .core import ARIEEngine
from .models import (
    ScanRequest, RollbackRequest, Summary, PolicyType, ARIEConfig
)

router = APIRouter(prefix="/api/arie", tags=["arie"])

# Global engine instance
_engine: Optional[ARIEEngine] = None


def get_engine() -> ARIEEngine:
    """Get or create ARIE engine instance"""
    global _engine
    if _engine is None:
        _engine = ARIEEngine()
    return _engine


async def check_permission(capability: str) -> bool:
    """
    Check if user has permission for ARIE operation
    Placeholder - will be integrated with Permission Engine
    """
    # TODO: Integrate with Permission Engine
    # For now, allow all operations
    return True


@router.post("/run", response_model=Summary)
async def run_scan(request: ScanRequest):
    """
    Run ARIE scan and optionally apply fixes
    
    Permissions required:
    - arie:scan for dry_run
    - arie:fix for apply=True
    """
    # Check permissions
    required_capability = "arie:fix" if request.apply else "arie:scan"
    if not await check_permission(required_capability):
        raise HTTPException(status_code=403, detail=f"Missing capability: {required_capability}")
    
    engine = get_engine()
    
    summary = engine.run(
        policy=request.policy,
        dry_run=request.dry_run,
        apply=request.apply,
        paths=request.paths
    )
    
    return summary


@router.get("/report", response_model=Summary)
async def get_report():
    """
    Get the last ARIE run report
    
    Permissions required: arie:scan
    """
    if not await check_permission("arie:scan"):
        raise HTTPException(status_code=403, detail="Missing capability: arie:scan")
    
    engine = get_engine()
    summary = engine.get_last_report()
    
    if not summary:
        raise HTTPException(status_code=404, detail="No reports available")
    
    return summary


@router.post("/rollback")
async def rollback_patch(request: RollbackRequest):
    """
    Rollback a specific patch
    
    Permissions required: arie:rollback
    """
    if not await check_permission("arie:rollback"):
        raise HTTPException(status_code=403, detail="Missing capability: arie:rollback")
    
    engine = get_engine()
    rollback = engine.rollback(request.patch_id, force=request.force)
    
    if not rollback.success:
        raise HTTPException(status_code=400, detail=rollback.error)
    
    return rollback


@router.get("/config", response_model=ARIEConfig)
async def get_config():
    """Get current ARIE configuration"""
    if not await check_permission("arie:scan"):
        raise HTTPException(status_code=403, detail="Missing capability: arie:scan")
    
    engine = get_engine()
    return engine.config


@router.post("/config", response_model=ARIEConfig)
async def update_config(config: ARIEConfig):
    """
    Update ARIE configuration
    
    Permissions required: arie:configure
    """
    if not await check_permission("arie:configure"):
        raise HTTPException(status_code=403, detail="Missing capability: arie:configure")
    
    engine = get_engine()
    engine.config = config
    
    return config
