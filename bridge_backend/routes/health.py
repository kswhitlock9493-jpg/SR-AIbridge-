# bridge_backend/routes/health.py
from fastapi import APIRouter
import os
from ..runtime.ports import resolve_port, check_listen

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def health_live():
    """Liveness probe for Render health checks"""
    return {"status": "ok", "alive": True}


@router.get("/ports")
def health_ports():
    env_port = os.getenv("PORT")
    resolved = resolve_port()
    occupied, note = check_listen("0.0.0.0", resolved)
    return {
        "env": {"PORT": env_port},
        "resolved_port": resolved,
        "bind_host": "0.0.0.0",
        "listener_state": "occupied" if occupied else "free",
        "note": note,
    }

@router.get("/runtime")
def health_runtime():
    return {
        "flags": {
            "BLUEPRINTS_ENABLED": os.getenv("BLUEPRINTS_ENABLED", "false").lower() == "true",
        }
    }
