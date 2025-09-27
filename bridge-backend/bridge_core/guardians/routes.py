from fastapi import APIRouter

router = APIRouter(prefix="/guardians", tags=["guardians"])

# Placeholder set of guardians — extend when DB ready
GUARDIANS = [
    {"id": "prim", "name": "Prim", "role": "Coordinator", "state": "active"},
    {"id": "oracle", "name": "Oracle", "role": "Vision", "state": "standby"},
    {"id": "plex", "name": "Plex", "role": "Engineer", "state": "active"},
    {"id": "merlin", "name": "Merlin", "role": "Strategist", "state": "standby"},
    {"id": "vanguard", "name": "Vanguard", "role": "Tactician", "state": "active"},
    {"id": "co", "name": "Co", "role": "Mediator", "state": "standby"},
    {"id": "claudewatcher", "name": "Claudewatcher", "role": "Analyst", "state": "active"},
]

@router.get("")
def list_guardians():
    """Return all guardians."""
    return {"guardians": GUARDIANS}

@router.get("/{gid}")
def guardian_detail(gid: str):
    """Return one guardian by ID."""
    g = next((x for x in GUARDIANS if x["id"] == gid), None)
    if not g:
        return {"error": "guardian_not_found"}
    return g