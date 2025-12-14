"""
Genesis API Routes
Health check and introspection endpoints for Genesis framework
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/genesis", tags=["genesis"])

# Check if Genesis is enabled
GENESIS_ENABLED = os.getenv("GENESIS_MODE", "enabled").lower() == "enabled"


@router.get("/pulse")
async def genesis_pulse() -> Dict[str, Any]:
    """
    Genesis heartbeat endpoint
    Returns current pulse and health status of the organism
    """
    if not GENESIS_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Genesis framework not enabled. Set GENESIS_MODE=enabled to enable."
        )
    
    try:
        from bridge_backend.genesis.introspection import genesis_introspection
        from bridge_backend.genesis.orchestration import genesis_orchestrator
        
        health = genesis_introspection.get_health_status()
        heartbeat = genesis_introspection.get_heartbeat_status()
        orchestrator_status = genesis_orchestrator.get_status()
        
        return {
            "ok": True,
            "pulse": "alive",
            "health": health,
            "heartbeat": heartbeat,
            "orchestrator": orchestrator_status,
        }
    except Exception as e:
        logger.error(f"Genesis pulse check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/manifest")
async def get_genesis_manifest() -> Dict[str, Any]:
    """
    Get the complete Genesis unified manifest
    Shows all registered engines and their relationships
    """
    if not GENESIS_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Genesis framework not enabled. Set GENESIS_MODE=enabled to enable."
        )
    
    try:
        from bridge_backend.genesis.manifest import genesis_manifest
        
        return genesis_manifest.get_manifest()
    except Exception as e:
        logger.error(f"Failed to get Genesis manifest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/manifest/{engine_name}")
async def get_engine_manifest(engine_name: str) -> Dict[str, Any]:
    """
    Get manifest for a specific engine
    
    Args:
        engine_name: Name of the engine
    """
    if not GENESIS_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Genesis framework not enabled. Set GENESIS_MODE=enabled to enable."
        )
    
    try:
        from bridge_backend.genesis.manifest import genesis_manifest
        
        engine = genesis_manifest.get_engine(engine_name)
        if not engine:
            raise HTTPException(
                status_code=404,
                detail=f"Engine '{engine_name}' not found in Genesis manifest"
            )
        
        return engine
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get engine manifest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def genesis_health() -> Dict[str, Any]:
    """
    Get detailed health status of all Genesis components
    """
    if not GENESIS_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Genesis framework not enabled. Set GENESIS_MODE=enabled to enable."
        )
    
    try:
        from bridge_backend.genesis.introspection import genesis_introspection
        
        return genesis_introspection.get_health_status()
    except Exception as e:
        logger.error(f"Failed to get Genesis health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/echo")
async def genesis_echo() -> Dict[str, Any]:
    """
    Get Genesis echo report - comprehensive introspection data
    """
    if not GENESIS_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Genesis framework not enabled. Set GENESIS_MODE=enabled to enable."
        )
    
    try:
        from bridge_backend.genesis.introspection import genesis_introspection
        
        return genesis_introspection.generate_echo_report()
    except Exception as e:
        logger.error(f"Failed to generate Genesis echo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/map")
async def genesis_system_map() -> Dict[str, Any]:
    """
    Get system topology map showing all engines and their relationships
    """
    if not GENESIS_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Genesis framework not enabled. Set GENESIS_MODE=enabled to enable."
        )
    
    try:
        from bridge_backend.genesis.introspection import genesis_introspection
        
        return genesis_introspection.get_system_map()
    except Exception as e:
        logger.error(f"Failed to get Genesis system map: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events")
async def genesis_event_history(limit: int = 100) -> Dict[str, Any]:
    """
    Get recent event history from Genesis bus
    
    Args:
        limit: Maximum number of events to return (default: 100)
    """
    if not GENESIS_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Genesis framework not enabled. Set GENESIS_MODE=enabled to enable."
        )
    
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        history = genesis_bus.get_event_history(limit)
        stats = genesis_bus.get_stats()
        
        return {
            "events": history,
            "count": len(history),
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"Failed to get Genesis event history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def genesis_stats() -> Dict[str, Any]:
    """
    Get Genesis bus statistics
    """
    if not GENESIS_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Genesis framework not enabled. Set GENESIS_MODE=enabled to enable."
        )
    
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        return genesis_bus.get_stats()
    except Exception as e:
        logger.error(f"Failed to get Genesis stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
