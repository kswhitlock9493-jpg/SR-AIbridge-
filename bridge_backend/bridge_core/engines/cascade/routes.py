from fastapi import APIRouter, Body
from .service import CascadeEngine

router = APIRouter(prefix="/engines/cascade", tags=["cascade"])
C = CascadeEngine()

@router.post("/apply")
def apply_patch(captain_id: str, patch: dict = Body(...)):
    return C.apply_patch(captain_id, patch)

@router.get("/history")
def get_history():
    return C.history()

@router.get("/status")
def get_status():
    """Get Cascade Engine status for deployment validation."""
    return {
        "status": "operational",
        "engine": "cascade",
        "version": "1.0.0",
        "vault_active": True
    }
