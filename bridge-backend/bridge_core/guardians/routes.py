from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/guardians", tags=["guardians"])

# Placeholder in-memory registry for guardians
GUARDIANS = {
    "System": {"name": "System", "state": "online"},
    "Protocol": {"name": "Protocol", "state": "watching"},
    "Armada": {"name": "Armada", "state": "ready"},
}

@router.get("")
def list_guardians():
    """Return all guardians with state."""
    return {"guardians": list(GUARDIANS.values())}

@router.get("/{name}")
def guardian_status(name: str):
    g = GUARDIANS.get(name)
    if not g:
        raise HTTPException(status_code=404, detail="guardian_not_found")
    return g