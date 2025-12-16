"""
Heritage Bridge Routes
API endpoints for heritage subsystem demos and controls
"""

from fastapi import APIRouter, HTTPException, WebSocket
from .demos.shakedown import run_shakedown
from .demos.mas_demo import run_mas
from .demos.federation_demo import run_federation
from .federation.live_ws import websocket_endpoint

router = APIRouter(prefix="/heritage", tags=["Heritage Bridge"])


@router.post("/demo/{mode}")
async def start_demo(mode: str):
    """
    Start a heritage demo
    
    Args:
        mode: Demo mode (shakedown, mas, federation)
    """
    if mode == "shakedown":
        await run_shakedown()
    elif mode == "mas":
        await run_mas()
    elif mode == "federation":
        await run_federation()
    else:
        raise HTTPException(400, f"Unknown demo mode: {mode}")
    
    return {"status": f"Started {mode} demo", "mode": mode}


@router.get("/demo/modes")
async def list_demo_modes():
    """List available demo modes"""
    return {
        "modes": [
            {
                "id": "shakedown",
                "name": "Shakedown Test",
                "description": "Basic system stress test with simulated events"
            },
            {
                "id": "mas",
                "name": "MAS Healing",
                "description": "Multi-Agent System fault injection and self-healing demo"
            },
            {
                "id": "federation",
                "name": "Federation",
                "description": "Cross-bridge task forwarding and heartbeat demo"
            }
        ]
    }


@router.websocket("/ws/stats")
async def websocket_stats(websocket: WebSocket):
    """WebSocket endpoint for real-time event streaming"""
    await websocket_endpoint(websocket)


@router.get("/status")
async def heritage_status():
    """Get heritage subsystem status"""
    return {
        "status": "operational",
        "subsystems": {
            "event_bus": "active",
            "mas": "ready",
            "federation": "ready",
            "agents": "ready",
            "demos": "ready"
        },
        "version": "1.0.0"
    }
