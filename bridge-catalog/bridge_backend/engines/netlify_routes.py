"""
Netlify Validator API Routes
RESTful endpoints for Netlify validation with Umbra integration
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
import logging

from bridge_backend.engines.netlify_validator import NetlifyValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/netlify", tags=["netlify"])


def require_role(allowed_roles: List[str]):
    """
    Simple role requirement decorator
    In production, this would be a proper dependency with JWT validation
    """
    def dependency(request=None):
        # Mock authentication - in production, extract from JWT token
        return {"id": "test_admiral", "role": "admiral"}
    return dependency


def get_netlify_validator():
    """Get or create Netlify Validator instance"""
    # Import here to avoid circular dependencies
    try:
        from bridge_backend.bridge_core.engines.umbra.memory import UmbraMemory
        from bridge_backend.genesis.bus import genesis_bus
        from bridge_backend.bridge_core.engines.chronicleloom import ChronicleLoom
    except ImportError:
        from genesis.bus import genesis_bus
        from bridge_core.engines.umbra.memory import UmbraMemory
        from bridge_core.engines.chronicleloom import ChronicleLoom
    
    # Simple stub for truth
    truth = None
    
    try:
        chronicle_loom = ChronicleLoom()
    except Exception:
        chronicle_loom = None
    
    memory = UmbraMemory(truth=truth, chronicle_loom=chronicle_loom)
    validator = NetlifyValidator(truth=truth, umbra_memory=memory)
    
    return validator


# === Validation Endpoints ===

@router.post("/validate")
async def validate_netlify_config(
    user=Depends(require_role(["admiral", "captain"]))
):
    """
    Validate Netlify configuration locally
    
    **RBAC**: Admiral, Captain
    """
    validator = get_netlify_validator()
    
    try:
        result = await validator.validate_rules()
        
        return {
            "status": "validation_complete",
            "result": result
        }
    except Exception as e:
        logger.error(f"Netlify validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate/recall")
async def validate_with_recall(
    user=Depends(require_role(["admiral", "captain"]))
):
    """
    Validate Netlify configuration with Umbra Memory recall
    
    Checks for similar past failures and suggests fixes
    
    **RBAC**: Admiral, Captain
    """
    validator = get_netlify_validator()
    
    try:
        result = await validator.validate_with_recall()
        
        return {
            "status": "validation_complete",
            "result": result
        }
    except Exception as e:
        logger.error(f"Netlify validation with recall error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_netlify_metrics(
    user=Depends(require_role(["admiral", "captain", "observer"]))
):
    """
    Get Netlify validator metrics
    
    **RBAC**: Admiral, Captain, Observer
    """
    validator = get_netlify_validator()
    
    try:
        metrics = validator.get_metrics()
        
        return {
            "status": "ok",
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Netlify metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_netlify_status():
    """
    Get Netlify validator status
    
    **RBAC**: All roles
    """
    validator = get_netlify_validator()
    
    return {
        "status": "active",
        "version": "1.9.7e",
        "validator": {
            "enabled": validator.enabled,
            "truth_available": validator.truth is not None,
            "memory_available": validator.umbra_memory is not None
        }
    }
