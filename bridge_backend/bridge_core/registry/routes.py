from fastapi import APIRouter, HTTPException, Query
from .agents_registry import AgentRegistry

router = APIRouter(prefix="/registry/agents", tags=["agents-registry"])
R = AgentRegistry()

@router.get("/all")
def list_all(project: str | None = Query(None)):
    return R.list_all(project=project)

@router.get("/{agent_id}")
def get_agent(agent_id: str):
    m = R.get_agent(agent_id)
    if not m:
        raise HTTPException(status_code=404, detail="agent_not_found")
    return {"manifest": m}

@router.get("/project/{project}")
def project_agents(project: str):
    return {"agents": R.resolve_project_agents(project)}
