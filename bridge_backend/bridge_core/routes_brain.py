from fastapi import APIRouter

router = APIRouter(prefix="/brain", tags=["brain"])

@router.get("")
def brain_console():
    """Return brain console status (stub)."""
    return {"brain": "online"}