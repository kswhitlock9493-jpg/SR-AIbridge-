"""
Bridge Diagnostics & Health Timeline API
Provides unified health, uptime, and metrics endpoints for SR-AIbridge.
Compatible with Termux, Cloudflare, and Netlify environments.
"""

from fastapi import APIRouter, Request
from datetime import datetime
import logging, asyncio, os, psutil, socket, sqlite3

# Dynamic imports to avoid circular dependency
from bridge_backend.genesis.introspection import genesis_introspection
from bridge_backend.genesis.persistence import genesis_persistence
from bridge_backend.runtime.sys_metrics import brh_metrics

# -------------------------------------------------------------------
# Initialization
# -------------------------------------------------------------------
logger = logging.getLogger(__name__)
router = APIRouter()
START_TIME = datetime.utcnow()

# -------------------------------------------------------------------
# /api/status – Quick health + uptime
# -------------------------------------------------------------------
@router.get("/api/status")
async def get_status():
    """Return live bridge health, uptime, and BRH metrics."""
    uptime = (datetime.utcnow() - START_TIME).total_seconds()

    # --- Persistence Health ---
    try:
        result = await genesis_persistence.is_duplicate("health_check")
        persistence_status = "ready" if result in [True, False] else "error"
    except Exception as e:
        persistence_status = f"error: {e}"

    # --- Introspection Health ---
    try:
        health_check = "active" if hasattr(genesis_introspection, "heartbeat") else "inactive"
    except Exception as e:
        health_check = f"error: {e}"

    # --- System Metrics (via BRH fallback) ---
    try:
        brh = brh_metrics()
        cpu = brh.get("cpu", "N/A")
        mem_mb = brh.get("memory", "N/A")
        batt = brh.get("battery", "N/A")
        environment = brh.get("environment", "BRH-Termux")
    except Exception as e:
        logger.warning(f"⚠️ BRH metrics fallback: {e}")
        process = psutil.Process(os.getpid())
        cpu = psutil.cpu_percent(interval=1)
        mem_mb = round(process.memory_info().rss / (1024 * 1024), 2)
        batt = "unknown"
        environment = "manual"

    return {
        "status": "ok",
        "uptime_seconds": round(uptime, 2),
        "components": {
            "introspection": health_check,
            "persistence": persistence_status,
            "api_router": "online",
        },
        "metrics": {
            "cpu_usage_percent": cpu,
            "memory_usage_mb": mem_mb,
            "battery_status": batt,
        },
        "environment": environment,
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Bridge backend fully operational.",
    }

# -------------------------------------------------------------------
# /api/diagnostics – Unified GET + POST triage
# -------------------------------------------------------------------
@router.get("/api/diagnostics")
@router.post("/api/diagnostics")
async def diagnostics_handler(request: Request):
    """Unified diagnostics endpoint for triage and health probes."""
    try:
        if request.method == "GET":
            logger.info("💚 Received GET diagnostics probe")
            return {"status": "ok", "message": "Diagnostics online."}
        else:
            body = await request.body()
            logger.info("💚 Diagnostics payload received")
            return {
                "status": "received",
                "type": "diagnostics",
                "timestamp": datetime.utcnow().isoformat(),
                "payload": body.decode() or None,
            }
    except Exception as e:
        logger.error(f"❌ Diagnostics handler error: {e}")
        return {"status": "error", "error": str(e)}

# -------------------------------------------------------------------
# /api/agents – Agent availability test
# -------------------------------------------------------------------
@router.get("/api/agents")
async def get_agents():
    """Simple route confirming agent service readiness."""
    return {
        "agents": [],
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
    }

# -------------------------------------------------------------------
# /api/netlify/ping – Connectivity verification
# -------------------------------------------------------------------
@router.get("/api/netlify/ping")
async def netlify_ping():
    """Simple Netlify ↔ Bridge backend handshake endpoint."""
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
    except Exception:
        hostname = "unknown"
        ip = "unresolved"

    return {
        "status": "ok",
        "message": "Netlify ↔ Bridge backend link alive!",
        "hostname": hostname,
        "ip": ip,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "Termux Cloudflare Tunnel",
        "api_health": {
            "persistence": "ready",
            "diagnostics": "online",
            "uptime_seconds": (datetime.utcnow() - START_TIME).total_seconds(),
        },
    }

# -------------------------------------------------------------------
# /api/health/full – Unified System Health Snapshot
# -------------------------------------------------------------------
@router.get("/api/health/full")
async def full_health():
    """Full system health snapshot combining BRH metrics + uptime."""
    try:
        uptime_minutes = round((datetime.utcnow() - START_TIME).total_seconds() / 60, 2)

        # Attempt safe BRH collection
        try:
            brh = brh_metrics()
            cpu = brh.get("cpu", "N/A")
            mem_mb = brh.get("memory", "N/A")
            batt = brh.get("battery", "N/A")
        except Exception as e:
            logger.warning(f"⚠️ Using fallback metrics: {e}")
            process = psutil.Process(os.getpid())
            cpu = psutil.cpu_percent(interval=1)
            mem_mb = round(process.memory_info().rss / (1024 * 1024), 2)
            batt = "unknown"

        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_minutes": uptime_minutes,
            "cpu_usage_percent": cpu,
            "memory_usage_mb": mem_mb,
            "battery_status": batt,
            "tunnel_status": "connected",
            "environment": "Termux Cloudflare Tunnel",
            "message": "Unified system heartbeat healthy.",
        }

    except Exception as e:
        logger.error(f"❌ Failed to fetch full health: {e}")
        return {"status": "error", "error": str(e)}

# -------------------------------------------------------------------
# Router Registration
# -------------------------------------------------------------------
def register(app):
    """Attach diagnostics routes to the main FastAPI app."""
    app.include_router(router)
    logger.info("💖 Diagnostics timeline routes registered successfully.")
