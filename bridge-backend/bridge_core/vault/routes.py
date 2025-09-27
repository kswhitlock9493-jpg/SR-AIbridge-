from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import json

router = APIRouter(prefix="/vault", tags=["vault"])

VAULT_LOGS_DIR = Path("vault") / "logs"
VAULT_LOGS_FILE = VAULT_LOGS_DIR / "events.jsonl"
VAULT_LOGS_DIR.mkdir(parents=True, exist_ok=True)

class VaultLogIn(BaseModel):
    source: str
    message: str
    details: dict | None = None

def _append_log(entry: dict):
    with VAULT_LOGS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def _read_logs(limit: int = 100) -> list[dict]:
    if not VAULT_LOGS_FILE.exists():
        return []
    with VAULT_LOGS_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]
    return [json.loads(l) for l in lines]

@router.get("/logs")
def get_logs(limit: int = 100):
    """Return last N vault log entries (default 100)."""
    return {"logs": _read_logs(limit)}

@router.post("/logs")
def add_log(item: VaultLogIn):
    """Append a new vault log entry."""
    stamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    entry = {
        "timestamp": stamp,
        "source": item.source,
        "message": item.message,
        "details": item.details or {},
    }
    _append_log(entry)
    return {"status": "logged", "entry": entry}