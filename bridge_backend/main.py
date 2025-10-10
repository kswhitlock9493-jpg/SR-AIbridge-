import sys
import os
import asyncio
import time
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from importlib import import_module

load_dotenv()

logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO").upper())
logger = logging.getLogger(__name__)

# === Runtime Path Safety Net ===
# Ensures the app finds local modules even under Render's /opt/render/project/src environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# === Safe Import Guard ===
def safe_import(module_path: str, alias: str = None):
    """
    Import a module and never crash the app at boot.
    If a router module fails to import (e.g., bad response_model typing),
    we log and skip it so the rest of the app stays up.
    """
    try:
        mod = import_module(module_path)
        logger.info(f"[IMPORT] {module_path}: ✅")
        return mod
    except Exception as e:
        logger.exception(f"[IMPORT] {module_path}: ❌ {e}")
        return None

app = FastAPI(
    title="SR-AIbridge",
    version=os.getenv("APP_VERSION","v1.9.6c"),
    description="Render-safe Port Binding + Response Model Fix + Blueprint Engine Hardening + Self-Healing"
)

# === CORS ===
CORS_ALLOW_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "https://sr-aibridge.netlify.app,https://sr-aibridge.onrender.com"
).split(",")

# Allow localhost in development
if os.getenv("ENVIRONMENT", "production") == "development":
    CORS_ALLOW_ORIGINS.extend(["http://localhost:3000", "http://localhost:5173"])

origins = CORS_ALLOW_ORIGINS if os.getenv("CORS_ALLOW_ALL", "false").lower() != "true" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Header synchronization middleware for Netlify ↔ Render parity
try:
    from bridge_backend.middleware.headers import HeaderSyncMiddleware
    app.add_middleware(HeaderSyncMiddleware)
    logger.info("[MIDDLEWARE] Header sync enabled")
except ImportError as e:
    logger.warning(f"[MIDDLEWARE] Header sync not available: {e}")

# Runtime metrics middleware
try:
    from bridge_backend.runtime.metrics_middleware import metrics_middleware
    app.middleware("http")(metrics_middleware)
except ImportError:
    try:
        from runtime.metrics_middleware import metrics_middleware
        app.middleware("http")(metrics_middleware)
    except ImportError:
        pass  # Metrics middleware not available

# Import and add RBAC permission middleware
try:
    from bridge_core.middleware.permissions import PermissionMiddleware
except ImportError:
    from bridge_backend.bridge_core.middleware.permissions import PermissionMiddleware

app.add_middleware(PermissionMiddleware)

# === Dynamic Router Imports ===
routers = {
    "protocols": safe_import("bridge_backend.bridge_core.protocols.routes"),
    "missions": safe_import("bridge_backend.bridge_core.missions.routes"),
    "system": safe_import("bridge_backend.bridge_core.system.routes"),
    "health": safe_import("bridge_backend.bridge_core.health.routes"),
}
for name, module in routers.items():
    if module and hasattr(module, "router"):
        app.include_router(module.router, prefix=f"/api/{name}", tags=[name.capitalize()])
    else:
        logger.warning(f"[ROUTER] Skipping '{name}' (module missing or no 'router').")

# Helper function to safely import and include a router
def safe_include_router(module_path: str, router_attr: str = "router", **kwargs):
    """Safely import a module and include its router, with fallback on failure."""
    module = safe_import(module_path)
    if module and hasattr(module, router_attr):
        try:
            router = getattr(module, router_attr)
            app.include_router(router, **kwargs)
            logger.info(f"[ROUTER] Included {module_path}:{router_attr}")
        except Exception as e:
            logger.exception(f"[ROUTER] Failed to include {module_path}:{router_attr}: {e}")
    else:
        logger.warning(f"[ROUTER] Skipping {module_path}:{router_attr} (not found)")

# Import protocol storage separately (not a router)
protocol_storage = safe_import("bridge_backend.bridge_core.protocols.storage")
if protocol_storage:
    try:
        protocol_storage.load_registry()
        logger.info("[REGISTRY] Protocol registry loaded")
    except Exception as e:
        logger.warning(f"[REGISTRY] Failed to load protocol registry: {e}")

# Import and include all routers individually with safe_import
safe_include_router("bridge_backend.bridge_core.protocols.complex_routes")
safe_include_router("bridge_backend.bridge_core.agents.routes")
safe_include_router("bridge_backend.bridge_core.routes_brain")
safe_include_router("bridge_backend.bridge_core.activity.routes")
safe_include_router("bridge_backend.bridge_core.vault.routes")
safe_include_router("bridge_backend.bridge_core.fleet.routes")
safe_include_router("bridge_backend.bridge_core.custody.routes")
safe_include_router("bridge_backend.bridge_core.console.routes")
safe_include_router("bridge_backend.bridge_core.captains.routes")
safe_include_router("bridge_backend.bridge_core.guardians.routes")
safe_include_router("bridge_backend.bridge_core.guardians.routes", "guardians_router")  # duplicate in original
safe_include_router("bridge_backend.bridge_core.engines.autonomy.routes")
safe_include_router("bridge_backend.bridge_core.engines.parser.routes")
safe_include_router("bridge_backend.bridge_core.engines.recovery.routes")
safe_include_router("bridge_backend.bridge_core.engines.routes_filing")
safe_include_router("bridge_backend.bridge_core.engines.truth.routes")
safe_include_router("bridge_backend.bridge_core.engines.indoctrination.routes")
safe_include_router("bridge_backend.bridge_core.engines.agents_foundry.routes")
safe_include_router("bridge_backend.bridge_core.engines.speech.routes")
safe_include_router("bridge_backend.bridge_core.engines.screen.routes")
safe_include_router("bridge_backend.bridge_core.engines.leviathan.routes")
safe_include_router("bridge_backend.bridge_core.engines.leviathan.routes_solver")
safe_include_router("bridge_backend.bridge_core.engines.creativity.routes")
safe_include_router("bridge_backend.bridge_core.engines.cascade.routes")

# Blueprint engine: gated and import-safe
if os.getenv("BLUEPRINTS_ENABLED", "false").lower() == "true":
    bp_mod = safe_import("bridge_backend.bridge_core.engines.blueprint.routes")
    if bp_mod and hasattr(bp_mod, "router"):
        try:
            app.include_router(bp_mod.router)
            logger.info("[BLUEPRINTS] Enabled and loaded successfully")
        except Exception as e:
            logger.exception(f"[BLUEPRINTS] Failed to include router: {e}")
    else:
        logger.warning("[BLUEPRINTS] Enabled but routes not loadable; engine skipped.")
else:
    logger.info("[BLUEPRINTS] Disabled by default (set BLUEPRINTS_ENABLED=true to enable).")

safe_include_router("bridge_backend.bridge_core.registry.routes")
safe_include_router("bridge_backend.bridge_core.permissions.routes")
safe_include_router("bridge_backend.bridge_core.payments.stripe_webhooks")
safe_include_router("bridge_backend.bridge_core.heritage.routes")
safe_include_router("bridge_backend.bridge_core.scans.routes")
safe_include_router("bridge_backend.routes.control")
safe_include_router("bridge_backend.routes.diagnostics_timeline")
safe_include_router("bridge_backend.routes.health")  # NEW: /health/ports, /health/runtime

@app.on_event("startup")
async def startup_event():
    from bridge_backend.runtime.ports import resolve_port
    target = resolve_port()
    logger.info("[BOOT] 🚀 Starting SR-AIbridge Runtime")
    logger.info(f"[BOOT] Target PORT={target} (Render sets $PORT automatically)")
    
    # Initialize database schema
    try:
        from bridge_backend.db.bootstrap import auto_sync_schema
        await auto_sync_schema()
        logger.info("[DB] Auto schema sync complete")
    except Exception as e:
        logger.error(f"[DB] Schema initialization failed: {e}")
    
    # Run release intelligence analysis
    try:
        from bridge_backend.runtime.release_intel import analyze_and_stabilize
        analyze_and_stabilize()
        logger.info("[INTEL] release analysis done")
    except Exception as e:
        logger.warning(f"[INTEL] release analysis failed: {e}")
    
    # Start heartbeat system
    try:
        from bridge_backend.runtime import heartbeat
        asyncio.create_task(heartbeat.run())
        logger.info("[HEART] heartbeat started")
    except Exception as e:
        logger.warning(f"[HEART] heartbeat failed: {e}")

# Startup event handler for endpoint triage
@app.on_event("startup")
async def startup_triage():
    """Run endpoint triage on startup"""
    import asyncio
    import subprocess
    import os
    
    # Run triage in background to not block startup
    async def run_triage():
        await asyncio.sleep(5)  # Wait for server to be ready
        try:
            # Run triage pre-seed first
            preseed_script = os.path.join(os.path.dirname(__file__), "scripts", "triage_preseed.py")
            if os.path.exists(preseed_script):
                print("🌱 Running triage pre-seed...")
                subprocess.run([sys.executable, preseed_script], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
            
            # Run endpoint triage
            endpoint_script = os.path.join(os.path.dirname(__file__), "scripts", "endpoint_triage.py")
            if os.path.exists(endpoint_script):
                print("🚑 Running initial endpoint triage...")
                subprocess.Popen([sys.executable, endpoint_script], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            
            # Run API triage
            api_script = os.path.join(os.path.dirname(__file__), "scripts", "api_triage.py")
            if os.path.exists(api_script):
                print("🧬 Running API triage...")
                subprocess.Popen([sys.executable, api_script], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            
            # Run Hooks triage
            hooks_script = os.path.join(os.path.dirname(__file__), "scripts", "hooks_triage.py")
            if os.path.exists(hooks_script):
                print("🪝 Running Hooks triage...")
                subprocess.Popen([sys.executable, hooks_script], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"⚠️ Failed to run triage: {e}")
    
    asyncio.create_task(run_triage())

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"ok": True, "version": app.version}

@app.get("/api/version")
def get_version():
    """Return API version and build information"""
    return {
        "version": os.getenv("BRIDGE_VERSION", "1.9.4a+"),
        "protocol": "Anchorhold",
        "service": "SR-AIbridge Backend",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "commit": os.getenv("GIT_COMMIT", os.getenv("RENDER_GIT_COMMIT", "unknown"))[:8] if os.getenv("GIT_COMMIT", os.getenv("RENDER_GIT_COMMIT", "unknown")) != "unknown" else "unknown",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

@app.get("/api/routes")
def list_routes():
    """Return list of available routes for parity checks"""
    r = []
    for route in app.router.routes:
        if hasattr(route, "path") and route.path.startswith("/"):
            methods = sorted(getattr(route, "methods", []))
            r.append({"path": route.path, "methods": methods})
    
    return {
        "count": len(r),
        "routes": sorted(r, key=lambda x: x["path"])
    }

@app.get("/api/telemetry")
def telemetry_snapshot():
    """Return runtime telemetry snapshot"""
    try:
        from bridge_backend.runtime.telemetry import TELEMETRY
    except ImportError:
        try:
            from runtime.telemetry import TELEMETRY
        except ImportError:
            return {"error": "Telemetry not available"}
    return TELEMETRY.snapshot()

if __name__ == "__main__":
    import uvicorn
    from bridge_backend.runtime.ports import resolve_port
    port = resolve_port()
    uvicorn.run("bridge_backend.main:app", host="0.0.0.0", port=port)