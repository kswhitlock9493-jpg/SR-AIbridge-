from fastapi import APIRouter

router = APIRouter(prefix="/guardian", tags=["guardian"])

# Guardian list for system snapshot (placeholder data)
GUARDIANS = []

@router.get("/status")
def guardian_status():
    """Return guardian system status (stub)."""
    return {"status": "ok"}