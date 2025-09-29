from fastapi import APIRouter

router = APIRouter(prefix="/guardian", tags=["guardian"])

# Guardian list for system snapshot (placeholder data)
GUARDIANS = []

@router.get("/status")
def guardian_status():
    """Return guardian system status (stub)."""
    return {"status": "ok"}

# Add the /guardians endpoint (no prefix) for compatibility
guardians_router = APIRouter(tags=["guardians"])

@guardians_router.get("/guardians")
def list_guardians():
    """List all guardians."""
    return {"guardians": GUARDIANS}