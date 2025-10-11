from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import os
import asyncio

router = APIRouter(prefix="/system", tags=["system"])


async def verify_seed_secret(secret: str):
    """Verify seed secret for bootstrap endpoint"""
    expected = os.environ.get("SEED_SECRET", "")
    if not expected or secret != expected:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True


@router.post("/seed/bootstrap")
async def seed_bootstrap(secret: str, _verified: bool = Depends(verify_seed_secret)):
    """Run seed bootstrap with secret validation"""
    try:
        # Import and run the seed bootstrap
        import sys
        from pathlib import Path
        
        # Import the seed bootstrap module
        scripts_dir = Path(__file__).parent.parent.parent.parent / "scripts"
        sys.path.insert(0, str(scripts_dir))
        
        from seed_bootstrap import main as seed_main
        success = await seed_main()
        
        if success:
            return {"status": "ok", "message": "Bootstrap complete"}
        else:
            raise HTTPException(status_code=500, detail="Bootstrap failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bootstrap error: {str(e)}")


@router.get("/metrics")
def system_metrics():
    """Return basic runtime metrics (stub until Prometheus integration)."""
    now = datetime.utcnow().isoformat() + "Z"
    return {
        "timestamp": now,
        "uptime": "mock-uptime",
        "requests": {"total": 0, "errors": 0},
    }

@router.post("/repair")
def system_repair():
    """Trigger a mock system repair operation."""
    return {"status": "repair_started", "time": datetime.utcnow().isoformat() + "Z"}

@router.get("/diagnostics")
def system_diagnostics():
    """Return static diagnostic info."""
    return {
        "checks": [
            {"name": "db", "status": "standby"},
            {"name": "vault", "status": "ok"},
            {"name": "agents", "status": "ok"},
        ]
    }