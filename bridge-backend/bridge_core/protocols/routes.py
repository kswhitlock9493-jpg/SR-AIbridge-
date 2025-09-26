from fastapi import APIRouter, HTTPException
from .registry import get_entry

router = APIRouter()

@router.get("/{name}/lore")
def protocol_lore(name: str):
    e = get_entry(name)
    if not e:
        raise HTTPException(status_code=404, detail="protocol_not_found")
    return {"name": e.name, "lore": e.lore()}

@router.get("/{name}/policy")
def protocol_policy(name: str):
    e = get_entry(name)
    if not e:
        raise HTTPException(status_code=404, detail="protocol_not_found")
    return {"name": e.name, "policy": e.policy()}