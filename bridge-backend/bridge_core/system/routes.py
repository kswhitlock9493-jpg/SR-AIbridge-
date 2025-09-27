from fastapi import APIRouter
from datetime import datetime
from pathlib import Path

router = APIRouter(tags=["system"])

@router.get("/health")
def health_check():
    """Lightweight probe for readiness."""
    return {
        "status": "healthy",
        "service": "SR-AIbridge Backend",
        "version": "1.2.0-sqlite-first",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

@router.get("/status")
def system_status():
    """Composite probe for system state."""
    vault_dir = Path("vault")
    db_file = Path("vault/bridge.sqlite")
    return {
        "status": "healthy",
        "components": {
            "database": {
                "status": "healthy" if db_file.exists() else "missing",
                "type": "sqlite",
            },
            "vault": {
                "status": "healthy" if vault_dir.exists() else "missing",
                "path": str(vault_dir),
            },
            "api": {"status": "healthy", "endpoints_active": True},
        },
        "self_heal_available": True,
    }