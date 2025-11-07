from fastapi import APIRouter, HTTPException, Query, Request, Depends
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Annotated
import json
import uuid

# Import dependencies with compatibility handling
try:
    from bridge_backend.bridge_core.db.db_manager import get_db_session
    from bridge_backend.models import AgentJob, Mission
    from bridge_backend.schemas import AgentJobOut
    DB_AVAILABLE = True
except ImportError:
    try:
        from ...db.db_manager import get_db_session
        from ....models import AgentJob, Mission
        from ....schemas import AgentJobOut
        DB_AVAILABLE = True
    except ImportError:
        # Fallback - will be None if not available
        get_db_session = None
        AgentJob = None
        Mission = None
        AgentJobOut = None
        DB_AVAILABLE = False

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
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z",
    }
    _write_mission(entry)
    return {"status": "created", "mission": entry}


@router.patch("/{mission_id}")
def update_mission(mission_id: str, updates: dict):
    """Update mission status, progress, or other fields."""
    missions = _read_missions()
    updated = False
    
    for i, mission in enumerate(missions):
        if mission.get("id") == mission_id:
            # Update allowed fields
            if "status" in updates:
                mission["status"] = updates["status"]
            if "progress" in updates:
                mission["progress"] = min(100, max(0, int(updates["progress"])))
            if "description" in updates:
                mission["description"] = updates["description"]
            
            mission["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"
            missions[i] = mission
            updated = True
            break
    
    if not updated:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    # Rewrite entire file
    MISSIONS_FILE.write_text("")
    for mission in missions:
        _write_mission(mission)
    
    return {"status": "updated", "mission": missions[i]}


if DB_AVAILABLE:
    @router.get("/{mission_id}/jobs", response_model=List[AgentJobOut])
    async def get_mission_jobs(
        mission_id: int,
        *,
        db: Annotated[AsyncSession, Depends(get_db_session)]
    ):
        """
        Get all agent jobs for a specific mission
        Returns blueprint-generated jobs with status, dependencies, and outputs
        
        The important part is how `db` is injected:
        - DO NOT annotate `db` as a pydantic field/type in the response.
        - DO NOT return AsyncSession.
        - Keep AsyncSession *only* inside Depends.
        """
        try:
            # Query all jobs for this mission
            result = await db.execute(
                select(AgentJob).where(AgentJob.mission_id == mission_id).order_by(AgentJob.task_key)
            )
            jobs = result.scalars().all()
            
            return jobs
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get mission jobs: {str(e)}")
else:
    @router.get("/{mission_id}/jobs", response_model=list)
    async def get_mission_jobs(mission_id: int):
        """
        Get all agent jobs for a specific mission
        Database backend not available - returns empty list
        """
        raise HTTPException(
            status_code=501,
            detail="Blueprint feature requires database backend (not available with JSONL storage)"
        )
