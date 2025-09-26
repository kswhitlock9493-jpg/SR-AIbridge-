from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .registry import list_registry, get_entry, seal

router = APIRouter(prefix="/bridge-core/protocols", tags=["protocols"])

# ... existing endpoints (registry, status, invoke, lore, policy) ...

@router.post("/{name}/seal")
def protocol_seal(name: str):
    e = get_entry(name)
    if not e:
        raise HTTPException(status_code=404, detail="protocol_not_found")
    return seal(name, details={"sealed_via_api": True})
