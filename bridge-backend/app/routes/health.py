"""
Health check and status endpoints for SR-AIbridge
"""
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "ok",
        "service": "SR-AIbridge Backend",
        "version": "1.1.0-autonomous"
    }

@router.get("/status")
async def get_status():
    """Get overall system status"""
    # Import here to avoid circular imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    # Import the main app state
    from fastapi import Request
    from ..main import storage, guardian, scheduler
    
    return {
        "status": "operational",
        "timestamp": "2024-01-20T12:00:00Z",
        "agents": {
            "total": len(storage.agents),
            "online": len([a for a in storage.agents if a.get("status") == "online"])
        },
        "missions": {
            "total": len(storage.missions),
            "active": len([m for m in storage.missions if m.get("status") == "active"])
        },
        "vault_logs": len(storage.vault_logs),
        "captain_messages": len(storage.captain_messages),
        "armada_fleet": len(storage.armada_fleet),
        "guardian": {
            "active": guardian.active if hasattr(guardian, 'active') else False,
            "status": guardian.selftest_status if hasattr(guardian, 'selftest_status') else "unknown"
        },
        "scheduler": {
            "active": scheduler.is_running if hasattr(scheduler, 'is_running') else False
        }
    }

@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "SR-AIbridge Backend",
        "version": "1.1.0-autonomous",
        "description": "Fully autonomous SR-AIbridge with real-time WebSocket updates",
        "endpoints": {
            "status": "/status",
            "guardian": "/guardian/status",
            "agents": "/agents",
            "missions": "/missions",
            "vault_logs": "/vault/logs",
            "captain_chat": "/captains/messages",
            "armada": "/armada/status",
            "armada_orders": "/armada/order",
            "websocket": "/ws",
            "websocket_stats": "/ws/stats",
            "reseed": "/reseed",
            "rituals": {
                "seed": "/rituals/seed",
                "cleanup": "/rituals/cleanup", 
                "reseed": "/rituals/reseed"
            }
        },
        "features": {
            "autonomous_scheduler": True,
            "guardian_daemon": True,
            "websocket_support": True,
            "real_time_updates": True,
            "in_memory_storage": True
        }
    }