"""
Vault/Doctrine log endpoints for SR-AIbridge
Handles vault logs and doctrine entries
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(tags=["logs"])

# Models (these should eventually be moved to a models module)
class VaultLog(BaseModel):
    id: Optional[int] = None
    agent_name: str
    action: str
    details: str
    timestamp: Optional[datetime] = None
    log_level: str = "info"

class VaultLogCreate(BaseModel):
    agent_name: str
    action: str
    details: str
    log_level: str = "info"

@router.get("/vault/logs", response_model=List[VaultLog])
async def get_vault_logs():
    """Get all vault logs"""
    from ..main import storage
    
    logs = sorted(storage.vault_logs, key=lambda x: x["timestamp"], reverse=True)
    return [VaultLog(**log) for log in logs]

@router.post("/vault/logs", response_model=VaultLog)
async def add_vault_log(log_create: VaultLogCreate):
    """Add a new vault log entry"""
    from ..main import storage
    
    log_data = {
        "id": storage.get_next_id(),
        "agent_name": log_create.agent_name,
        "action": log_create.action,
        "details": log_create.details,
        "timestamp": datetime.utcnow(),
        "log_level": log_create.log_level
    }
    storage.vault_logs.append(log_data)
    return VaultLog(**log_data)

# Doctrine aliases
@router.get("/doctrine", response_model=List[VaultLog])
async def list_doctrine():
    """Get doctrine logs (alias for vault logs)"""
    return await get_vault_logs()

@router.post("/doctrine", response_model=VaultLog)
async def add_doctrine(log_create: VaultLogCreate):
    """Add doctrine log (alias for vault log)"""
    return await add_vault_log(log_create)