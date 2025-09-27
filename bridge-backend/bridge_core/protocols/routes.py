from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .registry import list_registry, get_entry, invoke_protocol

router = APIRouter(prefix="/bridge-core/protocols", tags=["protocols"])

class InvokeIn(BaseModel):
    payload: dict = {}

@router.get("/registry")
def protocols_registry():
    return {"protocols": list_registry()}

@router.get("/{name}")
def protocol_status(name: str):
    e = get_entry(name)
    if not e:
        raise HTTPException(status_code=404, detail="protocol_not_found")
    return {"name": e.name, "state": e.state}

@router.post("/{name}/invoke")
async def protocol_invoke(name: str, req: InvokeIn):
    # Always delegate to registry stub. Never 500 if vaulted/missing.
    result = await invoke_protocol(name, req.payload or {})
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="protocol_not_found")
    return result
