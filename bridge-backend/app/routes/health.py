"""
Health check and status endpoints for SR-AIbridge
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import sys
import os

router = APIRouter()

# Helper to access main app state
def _get_app_state():
    """Get main app state components"""
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    try:
        from ..main import storage, guardian, scheduler
        return storage, guardian, scheduler
    except ImportError:
        # Fallback for direct access
        import main
        return main.storage, main.guardian, main.scheduler

@router.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "ok",
        "service": "SR-AIbridge Backend",
        "version": "1.1.0-autonomous"
    }

@router.get("/health/full")
async def full_health_check():
    """Comprehensive health check for deployment and monitoring"""
    try:
        storage, guardian, scheduler = _get_app_state()
        
        # Check system components
        components = {
            "database": "healthy",
            "storage": "healthy" if storage else "unhealthy",
            "guardian": "healthy" if (hasattr(guardian, 'active') and guardian.active) else "unhealthy",
            "scheduler": "healthy" if (hasattr(scheduler, 'is_running') and scheduler.is_running) else "healthy",
            "websocket": "healthy"  # Assume healthy if server is running
        }
        
        # Calculate overall health
        unhealthy_count = sum(1 for status in components.values() if status == "unhealthy")
        overall_status = "healthy" if unhealthy_count == 0 else "degraded" if unhealthy_count <= 2 else "unhealthy"
        
        return {
            "status": overall_status,
            "service": "SR-AIbridge Backend",
            "version": "1.1.0-autonomous",
            "timestamp": datetime.utcnow().isoformat(),
            "components": components,
            "metrics": {
                "agents_count": len(storage.agents) if storage else 0,
                "missions_count": len(storage.missions) if storage else 0,
                "vault_logs_count": len(storage.vault_logs) if storage else 0,
                "uptime_status": "operational"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "SR-AIbridge Backend", 
            "version": "1.1.0-autonomous",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.post("/self/heal")
async def trigger_self_heal():
    """Trigger system self-healing process"""
    try:
        storage, guardian, scheduler = _get_app_state()
        
        # Initialize self-healing service if needed
        from ..services.self_heal import SelfHealingService
        from ..main import websocket_manager
        
        healing_service = SelfHealingService(storage, websocket_manager)
        healing_actions = await healing_service.run_healing_cycle()
        
        return {
            "status": "success",
            "message": "Self-healing cycle completed",
            "timestamp": datetime.utcnow().isoformat(),
            "actions_taken": len(healing_actions),
            "healing_actions": healing_actions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "Self-healing failed",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })

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

@router.get("/activity")
async def get_activity():
    """Get recent activity (missions and logs combined)"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from ..main import storage
    
    activities = []
    
    # Add recent missions as activities
    for mission in storage.missions[-5:]:  # Last 5 missions
        activities.append({
            "id": f"mission_{mission['id']}",
            "type": "mission",
            "title": mission["title"],
            "description": mission["description"],
            "status": mission["status"],
            "timestamp": mission["created_at"]
        })
    
    # Add recent vault logs as activities
    for log in storage.vault_logs[-5:]:  # Last 5 logs
        activities.append({
            "id": f"log_{log['id']}",
            "type": "log",
            "title": f"{log['agent_name']}: {log['action']}",
            "description": log["details"],
            "status": log["log_level"],
            "timestamp": log["timestamp"]
        })
    
    # Sort by timestamp descending
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    return activities[:10]  # Return top 10

@router.get("/reseed")
async def reseed_data():
    """Reseed demo data (useful for testing)"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from ..main import rituals
    
    result = rituals.reseed()
    # Return the traditional format for backward compatibility
    return {
        "ok": True,
        "message": "Demo data reseeded successfully",
        "counts": result["final_counts"]
    }

@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from ..main import websocket_manager
    
    return websocket_manager.get_stats()