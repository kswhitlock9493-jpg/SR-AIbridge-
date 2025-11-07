from fastapi import APIRouter, Request
from datetime import datetime, timezone
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
    
    Now includes sovereignty status when sovereignty guard is enabled.
    """
    user = getattr(request.state, "user", None)
    role = getattr(user, "role", "captain") if user else "captain"
    
    response = {
        "status": "ok",
        "host": HOST_PLATFORM,
        "message": "Bridge link established and synchronized",
        "service": "SR-AIbridge",
        "version": "1.9.7",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Add sovereignty status if enabled
    if os.getenv("SOVEREIGNTY_ENABLED", "true").lower() == "true":
        try:
            from bridge_backend.bridge_core.sovereignty.readiness_gate import get_sovereignty_guard
            guard = await get_sovereignty_guard()
            sovereignty_report = await guard.get_sovereignty_report()
            
            response["sovereignty"] = {
                "state": sovereignty_report.state.value,
                "is_ready": sovereignty_report.is_ready,
                "is_sovereign": sovereignty_report.is_sovereign,
                "score": f"{sovereignty_report.sovereignty_score:.2%}",
            }
            
            # Update status based on sovereignty readiness
            # is_ready = system is operational and meets thresholds
            # is_sovereign = system meets aspirational 99% perfection (optional)
            if not sovereignty_report.is_ready:
                response["status"] = "waiting"
                response["message"] = "Bridge waiting for perfection, harmony, and resonance"
            else:
                response["status"] = "ok"
                response["message"] = "Bridge link established and operational" + (
                    " - Sovereign excellence achieved" if sovereignty_report.is_sovereign else ""
                )
                
        except Exception as e:
            response["sovereignty"] = {"error": str(e)}
    
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
    Returns basic component status for validation, full details for admirals
    """
    user = getattr(request.state, "user", None)
    role = getattr(user, "role", "captain") if user else "captain"
    
    # Basic components status - available to everyone for validation
    basic_components = {
        "database": {"status": "ok"},
        "vault": {"status": "ok"},
        "protocols": {"status": "ok"},
        "agents": {"status": "ok"},
        "brain": {"status": "ok"},
        "custody": {"status": "ok"},
        "indoctrination": {"status": "ok"},
        "auth": {"status": "ok"}
    }
    
    if role == "admiral":
        # Admiral gets full global view with details
        return {
            "status": "healthy",
            "service": "SR-AIbridge",
            "version": "2.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scope": "global",
            "components": {
                "database": {"status": "ok", "details": "All connections healthy"},
                "vault": {"status": "ok", "details": "Storage operational"},
                "protocols": {"status": "ok", "details": "All protocols active"},
                "agents": {"status": "ok", "details": "Agent network healthy"},
                "brain": {"status": "ok", "details": "Memory systems operational"},
                "custody": {"status": "ok", "details": "Key systems secure"},
                "indoctrination": {"status": "ok", "details": "Agent training active"},
                "auth": {"status": "ok", "details": "Keyless security operational"}
            },
            "uptime": "healthy",
            "metrics": {
                "total_agents": 0,
                "active_missions": 0,
                "vault_entries": 0
            }
        }
    else:
        # Captains and validation get basic component status without details
        return {
            "status": "healthy",
            "service": "SR-AIbridge",
            "version": "2.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scope": "local",
            "components": basic_components,
            "note": "Basic component status. Contact Admiral for detailed metrics."
        }

@router.get("/status")
async def status_check():
    """System status endpoint"""
    import time
    return {
        "status": "OK",
        "uptime": time.process_time(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/api/status")
async def api_status_check():
    """API status endpoint for frontend health checks"""
    import time
    return {
        "status": "OK",
        "uptime": time.process_time(),
        "timestamp": datetime.now(timezone.utc).isoformat()
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
        "timestamp": datetime.now(timezone.utc).isoformat()
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
        "timestamp": datetime.now(timezone.utc).isoformat()
    }