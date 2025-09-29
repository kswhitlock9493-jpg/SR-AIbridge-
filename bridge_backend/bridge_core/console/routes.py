from fastapi import APIRouter
from bridge_core.protocols.registry import list_registry
from bridge_core.guardians.routes import GUARDIANS
from datetime import datetime

router = APIRouter(prefix="/console", tags=["console"])

@router.get("/snapshot")
def snapshot():
    """
    Return a unified system snapshot:
    - protocols
    - guardians
    - timestamp
    """
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "protocols": list_registry(),
        "guardians": GUARDIANS,
        "status": "ok",
    }

@router.get("/summary")
def summary():
    """
    Shorter status summary for dashboards.
    """
    protocols = list_registry()
    active = [p for p in protocols if p["state"] == "active"]
    return {
        "status": "ok",
        "protocols_total": len(protocols),
        "protocols_active": len(active),
        "guardians_total": len(GUARDIANS),
    }