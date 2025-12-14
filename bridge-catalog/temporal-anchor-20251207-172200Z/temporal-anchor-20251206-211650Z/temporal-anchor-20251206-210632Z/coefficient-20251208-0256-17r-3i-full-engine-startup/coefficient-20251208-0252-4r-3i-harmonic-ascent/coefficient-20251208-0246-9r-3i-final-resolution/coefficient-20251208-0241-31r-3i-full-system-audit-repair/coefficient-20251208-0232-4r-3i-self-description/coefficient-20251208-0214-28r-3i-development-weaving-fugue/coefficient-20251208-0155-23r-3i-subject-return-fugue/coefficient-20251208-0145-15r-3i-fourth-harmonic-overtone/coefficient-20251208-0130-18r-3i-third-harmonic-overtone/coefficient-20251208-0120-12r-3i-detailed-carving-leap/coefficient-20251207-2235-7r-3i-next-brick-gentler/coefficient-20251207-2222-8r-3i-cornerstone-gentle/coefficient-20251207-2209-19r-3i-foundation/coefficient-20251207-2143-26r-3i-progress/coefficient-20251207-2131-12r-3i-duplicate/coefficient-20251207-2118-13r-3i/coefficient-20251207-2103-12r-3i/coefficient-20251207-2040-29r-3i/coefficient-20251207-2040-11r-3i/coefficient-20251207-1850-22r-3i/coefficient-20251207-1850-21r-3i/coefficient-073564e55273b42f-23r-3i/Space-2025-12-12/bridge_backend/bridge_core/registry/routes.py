from fastapi import APIRouter, HTTPException, Query, Depends
from .agents_registry import AgentRegistry

router = APIRouter(prefix="/registry", tags=["agents-registry"])
R = AgentRegistry()

# Import CascadeEngine for tier management
try:
    from bridge_core.engines.cascade.service import CascadeEngine
except ImportError:
    from bridge_backend.bridge_core.engines.cascade.service import CascadeEngine

# Feature matrix for different tiers
FEATURE_MATRIX = {
    "free": [
        {"label": "Basic Autonomy (7h)", "available": True},
        {"label": "Creativity Bay Access", "available": False},
        {"label": "Leviathan Deep Search", "available": False},
        {"label": "Screen Engines", "available": False},
    ],
    "paid": [
        {"label": "Extended Autonomy (14h)", "available": True},
        {"label": "Creativity Bay Access", "available": True},
        {"label": "Leviathan Deep Search", "available": True},
        {"label": "Screen Engines", "available": False},
    ],
    "admiral": [
        {"label": "24/7 Full Autonomy", "available": True},
        {"label": "Creativity Bay Access", "available": True},
        {"label": "Leviathan Deep Search", "available": True},
        {"label": "Screen Engines", "available": True},
    ],
}

# Mock authentication for now - in production this would be real auth
def current_user(user_id: str = Query(default="test_captain")):
    """Mock user authentication - returns user ID from query param"""
    class User:
        def __init__(self, user_id):
            self.id = user_id
    return User(user_id)

@router.get("/tier/me")
def get_my_tier(user: str = Depends(current_user)):
    """Get the current tier for the authenticated captain"""
    # Cascade decides real tier (stripe is source, cascade enforces)
    state = CascadeEngine().get_state(user.id)
    tier = state.get("tier", "free")
    return {
        "tier": tier,
        "status": state.get("status", "unknown"),
        "features": FEATURE_MATRIX.get(tier, FEATURE_MATRIX["free"]),
    }

@router.get("/agents/all")
def list_all(project: str | None = Query(None)):
    return R.list_all(project=project)

@router.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    m = R.get_agent(agent_id)
    if not m:
        raise HTTPException(status_code=404, detail="agent_not_found")
    return {"manifest": m}

@router.get("/agents/project/{project}")
def project_agents(project: str):
    return {"agents": R.resolve_project_agents(project)}
