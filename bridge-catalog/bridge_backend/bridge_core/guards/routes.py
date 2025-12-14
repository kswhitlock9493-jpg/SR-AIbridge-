"""
Guard status routes for Sanctum Cascade Protocol
Provides health check endpoints for monitoring guard status
"""
import os
import logging
from fastapi import APIRouter
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/api/guards/status")
async def get_guards_status():
    """Get overall guard status"""
    return {
        "netlify_guard": await netlify_guard_status(),
        "integrity_guard": await integrity_guard_status(),
        "umbra_link": await umbra_link_status(),
    }


@router.get("/api/guards/netlify/status")
async def netlify_guard_status():
    """Get Netlify Guard status"""
    publish_path = os.getenv("NETLIFY_PUBLISH_PATH")
    token_configured = bool(os.getenv("NETLIFY_AUTH_TOKEN"))
    
    # Check if publish path exists
    path_exists = False
    if publish_path:
        path_exists = Path(publish_path).exists()
    
    return {
        "enabled": True,
        "publish_path": publish_path,
        "path_exists": path_exists,
        "token_configured": token_configured,
        "status": "ok" if (publish_path and path_exists and token_configured) else "degraded"
    }


@router.get("/api/guards/integrity/status")
async def integrity_guard_status():
    """Get Integrity Guard status"""
    defer_seconds = os.getenv("INTEGRITY_DEFER_SECONDS", "3")
    
    return {
        "enabled": True,
        "defer_seconds": float(defer_seconds),
        "status": "ok"
    }


@router.get("/api/guards/umbra/status")
async def umbra_link_status():
    """Get Umbra⇄Genesis link status"""
    genesis_enabled = os.getenv("GENESIS_MODE", "enabled").lower() == "enabled"
    umbra_enabled = os.getenv("UMBRA_ENABLED", "true").lower() == "true"
    
    # Try to check Genesis bus connectivity
    bus_accessible = False
    try:
        from bridge_backend.genesis.bus import GenesisEventBus
        bus = GenesisEventBus()
        bus_accessible = True
    except Exception as e:
        logger.debug(f"Genesis bus check failed: {e}")
    
    return {
        "enabled": genesis_enabled and umbra_enabled,
        "genesis_enabled": genesis_enabled,
        "umbra_enabled": umbra_enabled,
        "bus_accessible": bus_accessible,
        "status": "ok" if bus_accessible else "degraded"
    }


@router.get("/api/guards/health")
async def guards_health():
    """Simple health check endpoint"""
    status = await get_guards_status()
    
    # Check if any guard is degraded
    all_ok = all(
        guard.get("status") == "ok" 
        for guard in status.values()
    )
    
    return {
        "status": "healthy" if all_ok else "degraded",
        "guards": status
    }
