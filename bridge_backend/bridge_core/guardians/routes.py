from fastapi import APIRouter

router = APIRouter(prefix="/guardian", tags=["guardian"])

@router.get("/status")
def guardian_status():
    """Return guardian system status (stub)."""
    return {"status": "ok"}