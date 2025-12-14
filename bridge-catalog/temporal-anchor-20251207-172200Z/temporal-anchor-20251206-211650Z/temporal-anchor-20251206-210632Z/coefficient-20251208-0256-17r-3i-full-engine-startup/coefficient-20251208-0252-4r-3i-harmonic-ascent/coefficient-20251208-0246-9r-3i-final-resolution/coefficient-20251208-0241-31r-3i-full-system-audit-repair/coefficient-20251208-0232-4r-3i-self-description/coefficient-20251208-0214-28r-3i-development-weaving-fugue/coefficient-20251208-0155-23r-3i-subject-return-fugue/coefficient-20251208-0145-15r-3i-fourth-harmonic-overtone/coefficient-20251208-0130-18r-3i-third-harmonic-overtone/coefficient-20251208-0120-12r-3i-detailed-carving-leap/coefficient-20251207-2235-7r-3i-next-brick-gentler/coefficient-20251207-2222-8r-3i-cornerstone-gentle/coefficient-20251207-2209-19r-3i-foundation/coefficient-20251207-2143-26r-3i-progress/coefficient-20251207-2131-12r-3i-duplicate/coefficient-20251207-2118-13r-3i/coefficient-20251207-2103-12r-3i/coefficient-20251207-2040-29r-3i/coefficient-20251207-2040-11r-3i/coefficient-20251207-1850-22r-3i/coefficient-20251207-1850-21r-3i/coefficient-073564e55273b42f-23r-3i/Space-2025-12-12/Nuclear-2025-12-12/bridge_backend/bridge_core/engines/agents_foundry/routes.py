from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from .service import AgentsFoundry

router = APIRouter(prefix="/engines/agents", tags=["agents"])
F = AgentsFoundry()

class CreateIn(BaseModel):
    name: str = Field(min_length=2)
    archetype: str = Field(description="jarvis | poe | aeon | custom")
    role: str
    project: str
    captain: str
    permissions: Dict[str, List[str]] = {}
    indoctrination: Optional[List[str]] = None
    tone: Optional[str] = None
    notes: Optional[str] = None

@router.get("/templates")
def templates():
    """List starter archetypes (Jarvis / Poe / Aeon)."""
    return {"archetypes": F.templates()}

@router.post("/create")
def create_agent(payload: CreateIn):
    try:
        m = F.create(
            name=payload.name,
            archetype=payload.archetype,
            role=payload.role,
            project=payload.project,
            captain=payload.captain,
            permissions=payload.permissions or {},
            indoctrination=payload.indoctrination or [],
            tone=payload.tone,
            notes=payload.notes,
        )
        return {"ok": True, "manifest": m.__dict__}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list")
def list_agents(project: Optional[str] = Query(None)):
    return {"agents": F.list(project=project)}

@router.get("/{agent_id}")
def get_agent(agent_id: str):
    m = F.get(agent_id)
    if not m:
        raise HTTPException(status_code=404, detail="agent_not_found")
    return {"manifest": m.__dict__}

@router.post("/{agent_id}/activate")
def activate(agent_id: str):
    m = F.set_state(agent_id, "active")
    if not m:
        raise HTTPException(status_code=404, detail="agent_not_found")
    return {"ok": True, "state": m.state, "id": m.id}

@router.post("/{agent_id}/retire")
def retire(agent_id: str):
    m = F.set_state(agent_id, "retired")
    if not m:
        raise HTTPException(status_code=404, detail="agent_not_found")
    return {"ok": True, "state": m.state, "id": m.id}
