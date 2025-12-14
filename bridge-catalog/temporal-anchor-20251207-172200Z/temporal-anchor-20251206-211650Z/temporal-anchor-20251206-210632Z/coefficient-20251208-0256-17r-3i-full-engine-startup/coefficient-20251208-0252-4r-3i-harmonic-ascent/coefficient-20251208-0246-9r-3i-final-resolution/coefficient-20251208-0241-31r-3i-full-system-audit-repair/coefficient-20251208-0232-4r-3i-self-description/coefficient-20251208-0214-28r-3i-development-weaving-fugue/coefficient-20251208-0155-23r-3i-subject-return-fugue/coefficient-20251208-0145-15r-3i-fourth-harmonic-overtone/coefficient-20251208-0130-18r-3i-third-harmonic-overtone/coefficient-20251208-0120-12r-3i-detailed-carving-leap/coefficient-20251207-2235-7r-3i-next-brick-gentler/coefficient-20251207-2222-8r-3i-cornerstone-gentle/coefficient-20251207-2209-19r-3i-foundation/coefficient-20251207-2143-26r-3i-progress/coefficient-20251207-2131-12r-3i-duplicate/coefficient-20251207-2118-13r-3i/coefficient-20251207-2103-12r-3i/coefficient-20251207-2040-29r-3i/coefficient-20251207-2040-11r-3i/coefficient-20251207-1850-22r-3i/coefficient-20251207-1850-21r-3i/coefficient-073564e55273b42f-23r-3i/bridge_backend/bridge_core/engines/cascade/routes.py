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
    # Check if vault is accessible
    vault_active = False
    try:
        from .service import VAULT_CASCADE
        vault_active = VAULT_CASCADE.exists()
    except (ImportError, AttributeError, OSError):
        # Import/attribute errors if vault not configured
        # OSError for filesystem permission issues
        pass
    
    return {
        "status": "operational",
        "engine": "cascade",
        "version": "1.0.0",
        "vault_active": vault_active
    }
