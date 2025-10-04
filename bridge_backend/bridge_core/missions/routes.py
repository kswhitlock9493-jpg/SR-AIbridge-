from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import json
import uuid

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