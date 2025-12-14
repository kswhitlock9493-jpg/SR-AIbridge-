from fastapi import APIRouter

router = APIRouter(tags=["doctrine"])

@router.get("/doctrine")
def doctrine_logs():
    """Return doctrine logs (alias for /vault/logs, stub)."""
    return {"logs": []}