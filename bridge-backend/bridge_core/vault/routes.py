from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import json
import uuid

router = APIRouter(prefix="/vault/logs", tags=["vault"])

LOGS_DIR = Path("vault") / "logs"
LOGS_FILE = LOGS_DIR / "events.jsonl"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

class VaultLogIn(BaseModel):
    source: str
    message: str
    details: dict = {}

def _read_logs(limit: int = 100) -> list[dict]:
    if not LOGS_FILE.exists():
        return []
    with LOGS_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]
    return [json.loads(line) for line in lines]

def _write_log(entry: dict):
    with LOGS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

@router.get("")
def list_logs(limit: int = 100):
    """Return the last N vault logs (default 100)."""
    return {"logs": _read_logs(limit)}

@router.post("")
def add_log(log: VaultLogIn):
    """Append a new vault log entry."""
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "source": log.source,
        "message": log.message,
        "details": log.details,
    }
    _write_log(entry)
    return {"status": "logged", "entry": entry}