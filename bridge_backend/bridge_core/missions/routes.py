from fastapi import APIRouter, HTTPException
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

def _read_missions() -> list[dict]:
    if not MISSIONS_FILE.exists():
        return []
    with MISSIONS_FILE.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def _write_mission(entry: dict):
    with MISSIONS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

@router.get("")
def list_missions():
    """Return all missions."""
    return {"missions": _read_missions()}

@router.post("")
def create_mission(m: MissionIn):
    """Create and append a new mission."""
    entry = {
        "id": str(uuid.uuid4()),
        "title": m.title,
        "description": m.description,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    _write_mission(entry)
    return {"status": "created", "mission": entry}