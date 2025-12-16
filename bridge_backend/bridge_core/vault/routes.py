from fastapi import APIRouter, HTTPException, Request
from pathlib import Path
import json
import os

router = APIRouter(prefix="/vault", tags=["vault"])

VAULT_ROOT = Path("vault")

@router.get("/secret")
def get_secret(key: str, request: Request = None):
    """
    Get a secret value by key for internal use (e.g., EnvSync token discovery)
    This endpoint is designed for backend-to-backend communication.
    For production, add authentication as needed.
    """
    # For now, this checks environment variables
    # You can extend this to read from secure vault storage
    value = os.getenv(key)
    if value:
        return {"value": value}
    
    # Optionally check vault files
    secrets_path = VAULT_ROOT / "secrets" / f"{key}.secret"
    if secrets_path.exists():
        try:
            return {"value": secrets_path.read_text().strip()}
        except Exception:
            pass
    
    raise HTTPException(status_code=404, detail="secret_not_found")

@router.get("")
def list_vault(request: Request):
    """
    List vault directories and files
    Captains: See only their own vault
    Admiral: See master vault with all captain vaults
    """
    if not VAULT_ROOT.exists():
        return {"vault": []}
    
    user = getattr(request.state, "user", None)
    role = getattr(user, "role", "captain") if user else "captain"
    user_id = getattr(user, "id", "unknown") if user else "unknown"
    
    items = []
    
    if role == "admiral":
        # Admiral sees everything (master vault)
        for p in VAULT_ROOT.iterdir():
            items.append({
                "name": p.name,
                "type": "dir" if p.is_dir() else "file",
                "scope": "master"
            })
    else:
        # Captains see only their own vault subdirectory
        captain_vault = VAULT_ROOT / f"captain_{user_id}"
        if captain_vault.exists():
            for p in captain_vault.iterdir():
                items.append({
                    "name": p.name,
                    "type": "dir" if p.is_dir() else "file",
                    "scope": "own"
                })
        # Also show shared logs
        logs_dir = VAULT_ROOT / "logs"
        if logs_dir.exists():
            items.append({
                "name": "logs",
                "type": "dir",
                "scope": "shared"
            })
    
    return {
        "vault": items,
        "role": role,
        "vault_scope": "master" if role == "admiral" else "own"
    }

@router.get("/logs")
def get_vault_logs(request: Request):
    """
    Get vault logs
    Role-based filtering: Captains see their own logs, Admiral sees all
    """
    logs_file = VAULT_ROOT / "logs" / "events.jsonl"
    if not logs_file.exists():
        return {"logs": []}
    
    user = getattr(request.state, "user", None)
    role = getattr(user, "role", "captain") if user else "captain"
    user_id = getattr(user, "id", "unknown") if user else "unknown"
    
    try:
        with logs_file.open("r", encoding="utf-8") as f:
            lines = f.readlines()[-50:]  # Get last 50 lines
        all_logs = [json.loads(line.strip()) for line in lines if line.strip()]
        
        # Filter logs by user role
        if role == "admiral":
            # Admiral sees all logs
            filtered_logs = all_logs
        else:
            # Captains see only their own logs
            filtered_logs = [
                log for log in all_logs
                if log.get("user_id") == user_id or log.get("captain_id") == user_id
            ]
        
        return {
            "logs": filtered_logs,
            "role": role,
            "total": len(filtered_logs)
        }
    except Exception:
        return {"logs": []}

@router.get("/{subpath:path}")
def browse_vault(subpath: str, request: Request):
    """
    Browse inside vault by path
    Role-based access: Captains restricted to own vault, Admiral has master access
    """
    user = getattr(request.state, "user", None)
    role = getattr(user, "role", "captain") if user else "captain"
    user_id = getattr(user, "id", "unknown") if user else "unknown"
    
    # Determine allowed base path
    if role == "admiral":
        # Admiral can browse anywhere
        target = VAULT_ROOT / subpath
    else:
        # Captains can only browse their own vault or shared logs
        if subpath.startswith("logs/") or subpath == "logs":
            # Allow access to shared logs
            target = VAULT_ROOT / subpath
        else:
            # Restrict to captain's own vault
            captain_vault = VAULT_ROOT / f"captain_{user_id}"
            target = captain_vault / subpath
    
    if not target.exists():
        raise HTTPException(status_code=404, detail="not_found")
    
    # Check if captain is trying to escape their vault (security check)
    if role != "admiral":
        captain_vault = VAULT_ROOT / f"captain_{user_id}"
        try:
            # Ensure target is within allowed paths
            target_resolved = target.resolve()
            logs_resolved = (VAULT_ROOT / "logs").resolve()
            captain_resolved = captain_vault.resolve()
            
            if not (str(target_resolved).startswith(str(captain_resolved)) or 
                    str(target_resolved).startswith(str(logs_resolved))):
                raise HTTPException(status_code=403, detail="access_denied_vault_isolation")
        except Exception:
            raise HTTPException(status_code=403, detail="access_denied")
    
    if target.is_dir():
        return {
            "path": str(subpath),
            "items": [
                {"name": p.name, "type": "dir" if p.is_dir() else "file"}
                for p in target.iterdir()
            ],
            "role": role
        }
    else:
        return {
            "path": str(subpath),
            "content": target.read_text(encoding="utf-8"),
            "role": role
        }
