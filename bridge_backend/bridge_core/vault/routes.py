from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter(prefix="/vault", tags=["vault"])

VAULT_ROOT = Path("vault")

@router.get("")
def list_vault():
    """List top-level vault directories and files."""
    if not VAULT_ROOT.exists():
        return {"vault": []}
    items = []
    for p in VAULT_ROOT.iterdir():
        items.append({
            "name": p.name,
            "type": "dir" if p.is_dir() else "file"
        })
    return {"vault": items}

@router.get("/logs")
def get_vault_logs():
    """Get vault logs - specific endpoint for the /vault/logs route"""
    logs_file = VAULT_ROOT / "logs" / "events.jsonl"
    if not logs_file.exists():
        return {"logs": []}
    
    try:
        with logs_file.open("r", encoding="utf-8") as f:
            lines = f.readlines()[-50:]  # Get last 50 lines
        logs = [json.loads(line.strip()) for line in lines if line.strip()]
        return {"logs": logs}
    except Exception:
        return {"logs": []}

@router.get("/{subpath:path}")
def browse_vault(subpath: str):
    """Browse inside vault by path."""
    target = VAULT_ROOT / subpath
    if not target.exists():
        raise HTTPException(status_code=404, detail="not_found")
    if target.is_dir():
        return {
            "path": str(subpath),
            "items": [
                {"name": p.name, "type": "dir" if p.is_dir() else "file"}
                for p in target.iterdir()
            ]
        }
    else:
        return {
            "path": str(subpath),
            "content": target.read_text(encoding="utf-8")
        }
