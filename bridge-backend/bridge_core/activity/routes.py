from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter(prefix="/activity", tags=["activity"])

VAULT_LOGS_FILE = Path("vault") / "logs" / "events.jsonl"

def _read_logs(limit: int = 50) -> list[dict]:
    if not VAULT_LOGS_FILE.exists():
        return []
    with VAULT_LOGS_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]
    logs = []
    for l in lines:
        try:
            logs.append(json.loads(l))
        except json.JSONDecodeError:
            # Optionally, log the error or skip the malformed line
            continue
    return logs

@router.get("")
def list_activity(limit: int = 50):
    """
    Transform vault logs into activity feed entries.
    """
    logs = _read_logs(limit)
    feed = []
    for e in logs:
        feed.append({
            "timestamp": e.get("timestamp"),
            "actor": e.get("source", "system"),
            "action": e.get("message", "event"),
            "details": e.get("details", {}),
        })
    # reverse for newest-first
    return {"activity": list(reversed(feed))}