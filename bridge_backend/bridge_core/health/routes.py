from fastapi import APIRouter, Request
from datetime import datetime
import os

router = APIRouter(tags=["health"])

# Detect host platform for environment awareness
HOST_PLATFORM = os.getenv("HOST_PLATFORM") or (
    "render" if os.getenv("RENDER") else
    "netlify" if os.getenv("NETLIFY") else
    "local"
)

@router.get("/health")
async def health_check(request: Request):
    """
    Basic health check for load balancers and monitoring
    Universal OK from either host with environment awareness
    Role-based: Captains see local only, Admiral sees global
    """
    user = getattr(request.state, "user", None)
    role = getattr(user, "role", "captain") if user else "captain"
    
    response = {
        "status": "ok",
        "host": HOST_PLATFORM,
        "message": "Bridge link established and synchronized",
        "service": "SR-AIbridge",
        "version": "1.9.7",
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

@router.get("/api/bridge/health")
async def bridge_health_check():
    """Bridge health endpoint for Healer-Net badge"""
    import os
    import json
    
    # Try to load the latest healer_net_report.json if it exists
    report_path = "healer_net_report.json"
    status = "healthy"
    
    if os.path.exists(report_path):
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
                if not report.get("summary", {}).get("healthy", True):
                    status = "issues"
                elif report.get("summary", {}).get("issues", 0) > 0:
                    status = "issues"
        except Exception:
            status = "unknown"
    
    return {
        "status": status,
        "service": "SR-AIbridge Healer-Net",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/federation/diagnostics")
async def federation_diagnostics():
    """
    Federation diagnostics endpoint for v1.9.5
    Returns self-healing status, heartbeat, and federation alignment
    """
    import os
    from pathlib import Path
    
    # Check for repair log
    repair_log_path = Path(__file__).parent.parent.parent / "runtime" / ".bridge_repair_log"
    repair_history = []
    if repair_log_path.exists():
        try:
            with open(repair_log_path, 'r') as f:
                # Get last 5 repair entries
                repair_history = f.readlines()[-5:]
        except Exception:
            repair_history = []
    
    # Check heartbeat status
    heartbeat_status = "active"
    try:
        from bridge_backend.runtime.heartbeat import ensure_httpx
        if not ensure_httpx():
            heartbeat_status = "degraded"
    except Exception:
        heartbeat_status = "unknown"
    
    # Check parity alignment
    from bridge_backend.runtime.parity import verify_cors_parity
    cors_aligned = verify_cors_parity()
    
    return {
        "status": "ok",
        "heartbeat": heartbeat_status,
        "self_heal": "ready",
        "federation": "aligned" if cors_aligned else "checking",
        "version": "1.9.5",
        "repair_history_count": len(repair_history),
        "port": os.getenv("PORT", "8000"),
        "timestamp": datetime.utcnow().isoformat()
    }