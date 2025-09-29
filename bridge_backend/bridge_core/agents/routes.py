from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bridge_backend.bridge_core.protocols.registry import list_registry, get_entry, activate_protocol, vault_protocol

router = APIRouter(prefix="/agents", tags=["agents"])

class AgentStateChange(BaseModel):
    action: str  # "activate" or "vault"

@router.get("")
def list_agents():
    """Return all agents with name + state."""
    return {"agents": list_registry()}

@router.get("/{name}")
def agent_status(name: str):
    e = get_entry(name)
    if not e:
        raise HTTPException(status_code=404, detail="agent_not_found")
    return {"name": e.name, "state": e.state}

@router.post("/{name}/activate")
def agent_activate(name: str):
    if not activate_protocol(name):
        raise HTTPException(status_code=404, detail="agent_not_found")
    return {"name": name, "state": "active"}

@router.post("/{name}/vault")
def agent_vault(name: str):
    if not vault_protocol(name):
        raise HTTPException(status_code=404, detail="agent_not_found")
    return {"name": name, "state": "vaulted"}