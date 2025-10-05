from fastapi import APIRouter, HTTPException, Query, Request, Depends
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import json
import uuid

# Import dependencies with compatibility handling
try:
    from bridge_backend.bridge_core.db.db_manager import get_db_session
    from bridge_backend.models import AgentJob, Mission
    from bridge_backend.schemas import AgentJobOut
except ImportError:
    try:
        from ...db.db_manager import get_db_session
        from ....models import AgentJob, Mission
        from ....schemas import AgentJobOut
    except ImportError:
        # Fallback - will be None if not available
        get_db_session = None
        AgentJob = None
        Mission = None
        AgentJobOut = None

router = APIRouter(prefix="/missions", tags=["missions"])

MISSIONS_DIR = Path("vault") / "missions"
MISSIONS_FILE = MISSIONS_DIR / "missions.jsonl"
MISSIONS_DIR.mkdir(parents=True, exist_ok=True)

class MissionIn(BaseModel):
    title: str
    description: str = ""
    priority: str = "medium"
    captain: str = None  # Captain who owns this mission
    role: str = "captain"  # 'captain' or 'agent'

def _read_missions() -> list[dict]:
    if not MISSIONS_FILE.exists():
        return []
    with MISSIONS_FILE.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def _write_mission(entry: dict):
    with MISSIONS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

@router.get("")
def list_missions(
    captain: str = Query(None, description="Filter missions by captain"),
    role: str = Query(None, description="Filter by role: 'captain' or 'agent'")
):
    """Return all missions, optionally filtered by captain or role."""
    missions = _read_missions()
    
    # Filter by captain if provided
    if captain:
        missions = [m for m in missions if m.get("captain") == captain]
    
    # Filter by role if provided
    if role:
        missions = [m for m in missions if m.get("role", "captain") == role]
    
    return {"missions": missions}

@router.post("")
def create_mission(m: MissionIn, request: Request):
    """Create and append a new mission."""
    # Get captain from request or use provided captain
    user = getattr(request.state, "user", None)
    captain = m.captain or (user.id if user else "unknown")
    
    entry = {
        "id": str(uuid.uuid4()),
        "title": m.title,
        "description": m.description,
        "priority": m.priority,
        "captain": captain,
        "role": m.role,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    _write_mission(entry)
    return {"status": "created", "mission": entry}


@router.get("/{mission_id}/jobs", response_model=List[AgentJobOut] if AgentJobOut else list)
async def get_mission_jobs(
    mission_id: int,
    session: AsyncSession = Depends(get_db_session) if get_db_session else None
):
    """
    Get all agent jobs for a specific mission
    Returns blueprint-generated jobs with status, dependencies, and outputs
    """
    if not get_db_session or not AgentJob:
        raise HTTPException(
            status_code=501,
            detail="Blueprint feature requires database backend (not available with JSONL storage)"
        )
    
    try:
        # Query all jobs for this mission
        result = await session.execute(
            select(AgentJob).where(AgentJob.mission_id == mission_id).order_by(AgentJob.task_key)
        )
        jobs = result.scalars().all()
        
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get mission jobs: {str(e)}")
