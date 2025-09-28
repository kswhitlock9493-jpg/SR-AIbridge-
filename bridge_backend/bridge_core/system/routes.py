from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/metrics")
def system_metrics():
    """Return basic runtime metrics (stub until Prometheus integration)."""
    now = datetime.utcnow().isoformat() + "Z"
    return {
        "timestamp": now,
        "uptime": "mock-uptime",
        "requests": {"total": 0, "errors": 0},
    }

@router.post("/repair")
def system_repair():
    """Trigger a mock system repair operation."""
    return {"status": "repair_started", "time": datetime.utcnow().isoformat() + "Z"}

@router.get("/diagnostics")
def system_diagnostics():
    """Return static diagnostic info."""
    return {
        "checks": [
            {"name": "db", "status": "standby"},
            {"name": "vault", "status": "ok"},
            {"name": "agents", "status": "ok"},
        ]
    }