from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .registry import list_registry, get_entry

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
    return {"protocol": e.name, "state": e.state, "status": "ok"}

@router.post("/{name}/invoke")
async def protocol_invoke(name: str, req: InvokeIn):
    e = get_entry(name)
    if not e:
        raise HTTPException(status_code=404, detail="protocol_not_found")
    # Always use the guaranteed contract handler
    async def default_handler(payload: dict):
        return {
            "protocol": e.name,
            "state": e.state,
            "status": "ok",
            "echo": payload,
        }
    return await default_handler(req.payload)

@router.get("/{name}/lore")
def protocol_lore(name: str):
    e = get_entry(name)
    if not e:
        raise HTTPException(status_code=404, detail="protocol_not_found")
    return {"protocol": e.name, "lore": e.lore()}

@router.get("/{name}/policy")
def protocol_policy(name: str):
    e = get_entry(name)
    if not e:
        raise HTTPException(status_code=404, detail="protocol_not_found")
    return {"protocol": e.name, "policy": e.policy()}
