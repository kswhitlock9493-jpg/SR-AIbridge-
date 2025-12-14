"""
Forge API Routes
v1.9.7f - Cascade Synchrony

Provides API endpoints for Forge integration and status monitoring.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from .forge_core import forge_integrate_engines, get_forge_status, load_forge_registry
from .synchrony import get_synchrony_status, synchrony

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/forge", tags=["Forge"])


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """
    Get current status of the Forge system.
    
    Returns:
        Forge system status including mode, self-heal, and synchrony settings
    """
    forge_status = get_forge_status()
    sync_status = get_synchrony_status()
    
    return {
        "forge": forge_status,
        "synchrony": sync_status,
        "version": "v1.9.7f",
        "protocol": "cascade_synchrony"
    }


@router.get("/registry")
async def get_registry() -> Dict[str, Any]:
    """
    Get the current Forge registry mapping.
    
    Returns:
        Engine to path mappings from bridge_forge.json
    """
    registry = load_forge_registry()
    
    return {
        "registry": registry,
        "engine_count": len(registry),
        "version": "v1.9.7f"
    }


@router.post("/integrate")
async def integrate() -> Dict[str, Any]:
    """
    Manually trigger Forge engine integration.
    
    Requires FORGE_MODE=enabled.
    
    Returns:
        Integration results including success and failure counts
    """
    try:
        result = forge_integrate_engines()
        
        if result.get("forge_mode") != "enabled":
            raise HTTPException(
                status_code=400,
                detail="FORGE_MODE must be set to 'enabled' to use this endpoint"
            )
        
        return result
        
    except Exception as e:
        logger.error(f"[Forge API] Integration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heal/{subsystem}")
async def trigger_healing(subsystem: str, error: Dict[str, Any]) -> Dict[str, Any]:
    """
    Manually trigger healing sequence for a subsystem.
    
    Args:
        subsystem: Name of the subsystem to heal
        error: Error details
    
    Returns:
        Healing event ID and status
    """
    try:
        event_id = synchrony.detect_error(subsystem, error)
        
        if event_id is None:
            raise HTTPException(
                status_code=400,
                detail="CASCADE_SYNC must be set to 'true' to trigger healing"
            )
        
        return {
            "event_id": event_id,
            "subsystem": subsystem,
            "status": "healing_initiated",
            "synchrony_enabled": synchrony.enabled
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Forge API] Healing trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recover/{platform}")
async def trigger_recovery(platform: str, error: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trigger auto-recovery for a specific platform.
    
    Args:
        platform: Platform name (render, netlify, github, bridge)
        error: Error details
    
    Returns:
        Recovery status
    """
    try:
        success = synchrony.auto_recover(platform, error)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Recovery not initiated for {platform}. Check CASCADE_SYNC setting."
            )
        
        return {
            "platform": platform,
            "status": "recovery_initiated",
            "success": success
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Forge API] Recovery trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topology")
async def get_topology() -> Dict[str, Any]:
    """
    Get the Forge topology visualization map.
    
    Returns:
        Topology map from forge_topology.json
    """
    try:
        import json
        from pathlib import Path
        
        topology_path = Path(".github/forge_topology.json")
        
        if not topology_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Topology map not found at .github/forge_topology.json"
            )
        
        with open(topology_path, "r") as f:
            topology = json.load(f)
        
        return topology
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Forge API] Topology retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
