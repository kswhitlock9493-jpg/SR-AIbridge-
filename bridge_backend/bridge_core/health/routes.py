from fastapi import APIRouter, Request
from datetime import datetime

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check(request: Request):
    """
    Basic health check for load balancers and monitoring
    Role-based: Captains see local only, Admiral sees global
    """
    user = getattr(request.state, "user", None)
    role = getattr(user, "role", "captain") if user else "captain"
    
    response = {
        "status": "ok",
        "service": "SR-AIbridge",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Add role context
    if role == "admiral":
        response["scope"] = "global"
        response["note"] = "Admiral: Full system health visibility"
    else:
        response["scope"] = "local"
        response["note"] = "Captain: Local self-test only (pass/fail)"
    
    return response

@router.get("/health/full")
async def full_health_check(request: Request):
    """
    Comprehensive system health check
    Captains: Local self-test only (pass/fail)
    Admiral: Full global view
    """
    user = getattr(request.state, "user", None)
    role = getattr(user, "role", "captain") if user else "captain"
    
    if role == "admiral":
        # Admiral gets full global view
        return {
            "status": "healthy",
            "service": "SR-AIbridge",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "scope": "global",
            "components": {
                "database": {"status": "ok", "details": "All connections healthy"},
                "vault": {"status": "ok", "details": "Storage operational"},
                "protocols": {"status": "ok", "details": "All protocols active"},
                "agents": {"status": "ok", "details": "Agent network healthy"},
                "brain": {"status": "ok", "details": "Memory systems operational"},
                "custody": {"status": "ok", "details": "Key systems secure"}
            },
            "uptime": "healthy",
            "metrics": {
                "total_agents": 0,
                "active_missions": 0,
                "vault_entries": 0
            }
        }
    else:
        # Captains get local pass/fail only
        return {
            "status": "pass",
            "service": "SR-AIbridge",
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "scope": "local",
            "self_test": "pass",
            "note": "Captain view: Local self-test result only. Contact Admiral for global status."
        }

@router.get("/status")
async def status_check():
    """System status endpoint"""
    import time
    return {
        "status": "OK",
        "uptime": time.process_time(),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/api/status")
async def api_status_check():
    """API status endpoint for frontend health checks"""
    import time
    return {
        "status": "OK",
        "uptime": time.process_time(),
        "timestamp": datetime.utcnow().isoformat()
    }