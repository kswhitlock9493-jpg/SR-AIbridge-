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

# === Environment Detection ===
# Detect runtime environment for platform-specific configuration
HOST_PLATFORM = os.getenv("HOST_PLATFORM") or (
    "brh" if os.getenv("BRH_ENABLED") else  # BRH sovereign deployment
    "netlify" if os.getenv("NETLIFY") else
    "local"
)
logger.info(f"[BOOT] Detected host environment: {HOST_PLATFORM}")

# === Runtime Path Safety Net ===
# Ensures the app finds local modules in various deployment contexts
# Add both the current directory and the parent directory to support different run contexts
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)  # Add parent to find bridge_backend package
sys.path.insert(0, current_dir)  # Add current for local imports

# === Sanctum Cascade Protocol v1.9.7q ===
# Ordered boot hardening: guards → reflex → umbra → integrity
from bridge_backend.bridge_core.guards.netlify_guard import validate_publish_path, require_netlify_token
from bridge_backend.bridge_core.integrity.deferred import delayed_integrity_check
from bridge_backend.bridge_core.engines.umbra.autoheal_link import safe_autoheal_init

# 1) Netlify publish path & token guard
validate_publish_path()

# Reflex Auth Forge token fallback for Netlify egress
# Only enforce token requirement in production/deployment environments, not during tests
# Skip if running in test/CI environment
if not (os.getenv("PYTEST_CURRENT_TEST") or os.getenv("CI")):
    try:
        from bridge_backend.bridge_core.engines.reflex.auth_forge import ensure_github_token
    except Exception:
        def ensure_github_token(): return os.getenv("GITHUB_TOKEN")  # safe no-op fallback
    require_netlify_token(ensure_github_token)

# 2) Umbra⇄Genesis link retry
def _link_bus():
    """Safe Genesis bus connectivity check"""
    try:
        from bridge_backend.genesis.bus import GenesisEventBus
        # Try to instantiate bus to verify connectivity
        bus = GenesisEventBus()
        logger.info("Genesis bus accessible")
    except Exception as e:
        raise RuntimeError(f"Genesis bus not accessible: {e}")

safe_autoheal_init(_link_bus)

# 3) Deferred integrity (after engines are steady)
from bridge_backend.bridge_core.integrity.core import run_integrity
delayed_integrity_check(run_integrity)
# === end Sanctum Cascade Protocol ===

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
    version="1.9.7q",
    description="v1.9.7q Sanctum Cascade Protocol: Self-Healing, Self-Learning, Self-Reflective Intelligence"
)

# === CORS ===
# Dynamic CORS handling for Netlify ↔ BRH coordination
CORS_ALLOW_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "https://sr-aibridge.netlify.app"
).split(",")

# Allow localhost in development
if os.getenv("ENVIRONMENT", "production") == "development":
    CORS_ALLOW_ORIGINS.extend(["http://localhost:3000", "http://localhost:5173"])

# Add your-netlify-domain as a placeholder for custom Netlify domains
if "your-netlify-domain.netlify.app" not in ",".join(CORS_ALLOW_ORIGINS):
    logger.info("[CORS] Add your custom Netlify domain to ALLOWED_ORIGINS if different from sr-aibridge.netlify.app")

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
safe_include_router("bridge_backend.bridge_core.auth.routes")  # Keyless security auth endpoints
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
safe_include_router("bridge_backend.bridge_core.engines.envsync.routes")

# EnvRecon Engine v2.0.2 - Genesis cross-platform reconciliation
safe_include_router("bridge_backend.engines.envrecon.routes")
safe_include_router("bridge_backend.engines.envrecon.ui", router_attr="ui_router")
logger.info("[ENVRECON] v2.0.2 routes enabled - cross-platform environment reconciliation active")

# EnvScribe Engine v1.9.6u - Unified Environment Intelligence System
if os.getenv("ENVSCRIBE_ENABLED", "true").lower() == "true":
    safe_include_router("bridge_backend.engines.envscribe.routes")
    logger.info("[ENVSCRIBE] v1.9.6u routes enabled - unified environment intelligence active")
else:
    logger.info("[ENVSCRIBE] Disabled (set ENVSCRIBE_ENABLED=true to enable)")

# Steward Engine v1.9.6l - Admiral-tier environment orchestration
if os.getenv("STEWARD_ENABLED", "true").lower() == "true":
    safe_include_router("bridge_backend.engines.steward.routes")
    logger.info("[STEWARD] v1.9.6l routes enabled - admiral-tier environment orchestration active")
else:
    logger.info("[STEWARD] Disabled (set STEWARD_ENABLED=true to enable)")

# ARIE Engine v1.9.6m - Autonomous Repository Integrity Engine
if os.getenv("ARIE_ENABLED", "true").lower() == "true":
    safe_include_router("bridge_backend.engines.arie.routes")
    logger.info("[ARIE] v1.9.6m routes enabled - autonomous repository integrity active")
else:
    logger.info("[ARIE] Disabled (set ARIE_ENABLED=true to enable)")

# Autonomy Decision Layer v1.9.6s - Self-healing CI/CD loop
if os.getenv("AUTONOMY_ENABLED", "true").lower() == "true":
    safe_include_router("bridge_backend.engines.autonomy.routes")
    logger.info("[AUTONOMY] v1.9.6s routes enabled - autonomous decision layer active")
else:
    logger.info("[AUTONOMY] Disabled (set AUTONOMY_ENABLED=true to enable)")

# HXO Nexus v1.9.6p - Central Harmonic Conductor
if os.getenv("HXO_NEXUS_ENABLED", "true").lower() == "true":
    safe_include_router("bridge_backend.bridge_core.engines.hxo.routes")
    logger.info("[HXO NEXUS] v1.9.6p routes enabled - central harmonic conductor active")
else:
    logger.info("[HXO NEXUS] Disabled (set HXO_NEXUS_ENABLED=true to enable)")

# Umbra Cognitive Stack v1.9.7g - Self-Healing, Self-Learning Intelligence + Lattice Memory
if os.getenv("UMBRA_ENABLED", "true").lower() == "true":
    safe_include_router("bridge_backend.bridge_core.engines.umbra.routes")
    logger.info("[UMBRA] v1.9.7g routes enabled - cognitive stack active (Core, Memory, Predictive, Echo, Lattice)")
else:
    logger.info("[UMBRA] Disabled (set UMBRA_ENABLED=true to enable)")

# HXO Engine v1.9.6n - Hypshard-X Orchestrator
if os.getenv("HXO_ENABLED", "true").lower() == "true":
    safe_include_router("bridge_backend.engines.hypshard_x.routes")
    logger.info("[HXO] v1.9.6n routes enabled - hypshard-x orchestrator active")
else:
    logger.info("[HXO] Disabled (set HXO_ENABLED=true to enable)")

# Genesis framework routes
if os.getenv("GENESIS_MODE", "enabled").lower() == "enabled":
    safe_include_router("bridge_backend.genesis.routes")
    logger.info("[GENESIS] API routes enabled")
    
    # Sanctum Cascade Protocol guard status routes (v1.9.7q)
    safe_include_router("bridge_backend.bridge_core.guards.routes")
    logger.info("[GUARDS] Sanctum Cascade Protocol status routes enabled")
else:
    logger.info("[GENESIS] API routes disabled (set GENESIS_MODE=enabled to enable)")

# Genesis Linkage: unified engine orchestration
if os.getenv("LINK_ENGINES", "true").lower() == "true":
    safe_include_router("bridge_backend.bridge_core.engines.routes_linked")
    logger.info("[LINKAGE] Engine linkage enabled")
else:
    logger.info("[LINKAGE] Engine linkage disabled (set LINK_ENGINES=true to enable)")

# Bridge Sovereignty: readiness gate system for perfection, harmony, resonance
if os.getenv("SOVEREIGNTY_ENABLED", "true").lower() == "true":
    safe_include_router("bridge_core.sovereignty.routes", prefix="/api/bridge")
    logger.info("[SOVEREIGNTY] Readiness gate enabled - bridge sovereignty active")

# Blueprint engine: enabled by default for production mode
# Part of core engine trio (Parser, Blueprint, Cascade) for full production readiness
if os.getenv("BLUEPRINTS_ENABLED", "true").lower() == "true":
    bp_mod = safe_import("bridge_backend.bridge_core.engines.blueprint.routes")
    if bp_mod and hasattr(bp_mod, "router"):
        try:
            app.include_router(bp_mod.router)
            logger.info("[BLUEPRINTS] ✅ Enabled and loaded successfully - production mode active")
        except Exception as e:
            logger.exception(f"[BLUEPRINTS] Failed to include router: {e}")
    else:
        logger.warning("[BLUEPRINTS] Enabled but routes not loadable; engine skipped.")
else:
    logger.info("[BLUEPRINTS] Disabled (set BLUEPRINTS_ENABLED=true to enable)")

safe_include_router("bridge_backend.bridge_core.registry.routes")
safe_include_router("bridge_backend.bridge_core.permissions.routes")
safe_include_router("bridge_backend.bridge_core.engines.push_notifications")
safe_include_router("bridge_backend.bridge_core.payments.stripe_webhooks")
safe_include_router("bridge_backend.bridge_core.heritage.routes")
safe_include_router("bridge_backend.bridge_core.scans.routes")
safe_include_router("bridge_backend.routes.control")
safe_include_router("bridge_backend.routes.diagnostics_timeline")  # Includes TDE-X deploy-parity
safe_include_router("bridge_backend.routes.health")  # NEW: /health/ports, /health/runtime

# Forge v1.9.7f - Cascade Synchrony routes
if os.getenv("FORGE_MODE", "disabled").lower() == "enabled":
    safe_include_router("bridge_backend.forge.routes")
    logger.info("[FORGE] v1.9.7f routes enabled - Cascade Synchrony protocol active")
else:
    logger.info("[FORGE] Disabled (set FORGE_MODE=enabled to enable)")

# Deployment webhook routes for autonomy engine integration
safe_include_router("bridge_backend.webhooks.deployment_webhooks")
logger.info("[WEBHOOKS] Deployment webhook routes enabled for autonomy integration")

# Umbra Triage Mesh webhook routes (v2.0.0 - BRH)
if os.getenv("UMBRA_ENABLED", "true").lower() == "true":
    # Legacy Render webhook removed - using BRH sovereign deployment
    # safe_include_router("bridge_backend.webhooks.render")
    safe_include_router("bridge_backend.webhooks.netlify")
    safe_include_router("bridge_backend.webhooks.github")
    logger.info("[WEBHOOKS] Umbra triage webhook routes enabled (Netlify, GitHub) - BRH mode")

# Umbra Triage Mesh routes (v1.9.7k)
if os.getenv("UMBRA_ENABLED", "true").lower() == "true":
    safe_include_router("bridge_backend.engines.umbra.routes")
    logger.info("[UMBRA TRIAGE] v1.9.7k routes enabled - unified triage mesh active")

# Sovereign Engines - MicroScribe, MicroLogician, Compliance Guard
if os.getenv("SOVEREIGN_ENGINES_ENABLED", "true").lower() == "true":
    safe_include_router("bridge_backend.routes.sovereign_engines")
    logger.info("[SOVEREIGN ENGINES] v1.0.0 routes enabled - quantum-resistant evaluation engines active")
else:
    logger.info("[SOVEREIGN ENGINES] Disabled (set SOVEREIGN_ENGINES_ENABLED=true to enable)")


@app.on_event("startup")
async def startup_event():
    from bridge_backend.runtime.ports import resolve_port
    from bridge_backend.runtime.startup_watchdog import watchdog
    from bridge_backend.runtime.port_guard import describe_port_env
    from bridge_backend.runtime.deploy_parity import deploy_parity_check
    from bridge_backend.runtime.temporal_deploy import tdb, TDB_ENABLED
    
    # === engines_enable_true: Permanent Full Activation Protocol ===
    # Check if engines_enable_true flag is set (default: true)
    if os.getenv("ENGINES_ENABLE_TRUE", "true").lower() == "true":
        try:
            from bridge_backend.genesis import activate_all_engines
            logger.info("🚀 [GENESIS] engines_enable_true flag detected - activating all engines")
            report = activate_all_engines()
            logger.info(f"✅ [GENESIS] Engine activation complete: {report.engines_activated}/{report.engines_total} engines active")
        except Exception as e:
            logger.warning(f"⚠️ [GENESIS] Engine activation check failed (continuing): {e}")
    
    # === Genesis Bootstrap ===
    # Initialize Genesis framework if enabled
    if os.getenv("GENESIS_MODE", "enabled").lower() == "enabled":
        try:
            from bridge_backend.genesis.orchestration import genesis_orchestrator
            from bridge_backend.bridge_core.engines.adapters.genesis_link import register_all_genesis_links
            
            # Register all engine linkages
            await register_all_genesis_links()
            
            # Start orchestration loop
            await genesis_orchestrator.start()
            
            logger.info("✅ Genesis framework initialized")
        except Exception as e:
            logger.warning(f"⚠️ Genesis initialization failed (continuing): {e}")
    
    # === Chimera Genesis Recovery ===
    # Safe initialization with retry and fallback for Chimera
    try:
        from bridge_backend.bridge_core.engines.hxo import safe_init as chimera_safe_init
        chimera_safe_init()
        logger.info("✅ Chimera safe initialization complete")
    except Exception as e:
        logger.warning(f"⚠️ Chimera safe init failed (continuing): {e}")
    
    # === Forge Integration Bootstrap ===
    # Initialize GitHub Forge introspection and engine integration
    if os.getenv("FORGE_MODE", "disabled").lower() == "enabled":
        try:
            from bridge_backend.forge import forge_integrate_engines
            
            logger.info("🔥 [Forge] Starting Cascade Synchrony integration")
            result = forge_integrate_engines()
            
            logger.info(f"✅ [Forge] Integration complete: {result.get('integration_count', 0)} engines integrated")
        except Exception as e:
            logger.warning(f"⚠️ [Forge] Integration failed (continuing): {e}")
    
    # === HXO Nexus Bootstrap ===
    # Initialize HXO Nexus if enabled
    if os.getenv("HXO_NEXUS_ENABLED", "true").lower() == "true":
        try:
            from bridge_backend.bridge_core.engines.hxo.startup import startup_hxo_nexus
            from bridge_backend.bridge_core.engines.adapters.hxo_nexus_integration import (
                initialize_hxo_connectivity
            )
            
            # Start the nexus
            await startup_hxo_nexus()
            
            # Initialize full connectivity
            await initialize_hxo_connectivity()
            
            logger.info("✅ HXO Nexus connectivity initialized")
        except Exception as e:
            logger.warning(f"⚠️ HXO Nexus initialization failed (continuing): {e}")
    
    # === TDE-X v2 Orchestrator ===
    # Initialize TDE-X v2 with resumable stages (runs in background)
    use_tde_v2 = os.getenv("TDE_V2_ENABLED", "true").lower() == "true"
    if use_tde_v2:
        try:
            from bridge_backend.runtime.tde_x.orchestrator_v2 import tde_orchestrator
            await tde_orchestrator.run()
            logger.info("✅ TDE-X v2 orchestrator initialized")
        except Exception as e:
            logger.warning(f"⚠️ TDE-X v2 initialization failed (continuing): {e}")
    
    # === Bridge Sovereignty Guard ===
    # Initialize sovereignty readiness gate if enabled
    if os.getenv("SOVEREIGNTY_ENABLED", "true").lower() == "true":
        try:
            from bridge_core.sovereignty.readiness_gate import get_sovereignty_guard
            
            logger.info("🛡️ [Sovereignty] Initializing Bridge Sovereignty Guard...")
            guard = await get_sovereignty_guard()
            
            # Wait for sovereignty to be achieved (gracefully)
            sovereignty_timeout = float(os.getenv("SOVEREIGNTY_TIMEOUT", "30.0"))
            if not guard.is_ready():
                logger.info(f"⏳ [Sovereignty] Gracefully waiting for perfection (timeout: {sovereignty_timeout}s)")
                achieved = await guard.wait_for_sovereignty(timeout=sovereignty_timeout)
                
                if achieved:
                    logger.info("👑 [Sovereignty] Bridge has achieved sovereignty - ready to serve")
                else:
                    logger.warning(
                        "⚠️ [Sovereignty] Timeout reached - bridge will serve in degraded mode\n"
                        "   Set SOVEREIGNTY_TIMEOUT to a higher value for slower systems"
                    )
            
        except Exception as e:
            logger.warning(f"⚠️ [Sovereignty] Initialization failed (continuing): {e}")
    
    # === STAGE 1: Minimal Health Check (Immediate Render Detection) ===
    if TDB_ENABLED:
        tdb.mark_stage_start(1)
    
    # Log PORT environment state
    describe_port_env()
    
    # Simple port resolution (no loops)
    target = resolve_port()
    watchdog.mark_port_resolved(target)
    
    logger.info("[BOOT] 🚀 Starting SR-AIbridge Runtime")
    logger.info(f"[BOOT] Port binding: {target}")
    
    if TDB_ENABLED:
        logger.info("[TDB] v1.9.6i Temporal Deploy Buffer activated")
    
    # Mark bind as confirmed for Stage 1
    watchdog.mark_bind_confirmed()
    if TDB_ENABLED:
        tdb.mark_stage_complete(1)
    
    # === STAGE 2 & 3: Background Initialization (if using legacy TDB) ===
    # If TDE-X v2 is disabled, fall back to legacy TDB initialization
    if not use_tde_v2 and TDB_ENABLED:
        asyncio.create_task(_run_background_stages(app, watchdog, tdb))
    elif not use_tde_v2:
        # Legacy synchronous startup (no TDB, no TDE-X v2)
        await _run_synchronous_startup(app, watchdog)

async def _run_synchronous_startup(app, watchdog):
    """Legacy synchronous startup (when TDB is disabled)"""
    from bridge_backend.runtime.deploy_parity import deploy_parity_check
    
    # Run deploy parity check
    await deploy_parity_check(app)
    
    # Initialize database schema
    try:
        from bridge_backend.db.bootstrap import auto_sync_schema
        await auto_sync_schema()
        logger.info("[DB] Auto schema sync complete")
        watchdog.mark_db_synced()
    except Exception as e:
        logger.error(f"[DB] Schema initialization failed: {e}")
    
    # Run release intelligence analysis
    try:
        from bridge_backend.runtime.release_intel import analyze_and_stabilize
        analyze_and_stabilize()
        logger.info("[INTEL] release analysis done")
    except Exception as e:
        logger.warning(f"[INTEL] release analysis failed: {e}")
    
    # Get startup metrics
    metrics = watchdog.get_metrics()
    if metrics['bind_time']:
        logger.info(f"[STABILIZER] Startup latency {metrics['bind_time']:.2f}s (tolerance: 6.0s)")
    
    # Deferred heartbeat
    try:
        from bridge_backend.runtime.heartbeat import heartbeat_loop
        asyncio.create_task(heartbeat_loop())
        logger.info("[HEARTBEAT] ✅ Initialized")
        watchdog.mark_heartbeat_initialized()
    except Exception as e:
        logger.warning(f"[HEARTBEAT] Failed to initialize: {e}")
    
    # EnvSync background scheduler
    try:
        from bridge_backend.bridge_core.engines.envsync.tasks import run_scheduled_sync
        from bridge_backend.bridge_core.engines.envsync.config import CONFIG as ENVSYNC_CONFIG
        
        if ENVSYNC_CONFIG.enabled and ENVSYNC_CONFIG.schedule in ("@hourly", "@daily"):
            async def _envsync_loop():
                import asyncio
                while True:
                    await run_scheduled_sync()
                    # naive schedule
                    interval = 3600 if ENVSYNC_CONFIG.schedule == "@hourly" else 86400
                    await asyncio.sleep(interval)
            asyncio.create_task(_envsync_loop())
            logger.info(f"[ENVSYNC] ✅ Scheduled sync enabled ({ENVSYNC_CONFIG.schedule})")
    except Exception as e:
        logger.warning(f"[ENVSYNC] Failed to initialize: {e}")

async def _run_background_stages(app, watchdog, tdb):
    """Run Stage 2 and Stage 3 in background for TDB deployment"""
    from bridge_backend.runtime.deploy_parity import deploy_parity_check
    
    # === STAGE 2: Core Bootstrap (Background) ===
    tdb.mark_stage_start(2)
    
    # Deploy parity check
    try:
        await deploy_parity_check(app)
    except Exception as e:
        tdb.add_error(2, f"Deploy parity check failed: {e}")
        logger.warning(f"[TDB] Deploy parity check failed (continuing): {e}")
    
    # Initialize database schema
    try:
        from bridge_backend.db.bootstrap import auto_sync_schema
        await auto_sync_schema()
        logger.info("[DB] Auto schema sync complete")
        watchdog.mark_db_synced()
    except Exception as e:
        tdb.add_error(2, f"Database sync failed: {e}")
        logger.warning(f"[TDB] Database sync failed (continuing): {e}")
    
    # Run release intelligence analysis
    try:
        from bridge_backend.runtime.release_intel import analyze_and_stabilize
        analyze_and_stabilize()
        logger.info("[INTEL] release analysis done")
    except Exception as e:
        tdb.add_error(2, f"Release intelligence failed: {e}")
        logger.warning(f"[TDB] Release intelligence failed (continuing): {e}")
    
    tdb.mark_stage_complete(2)
    
    # === STAGE 3: Federation & Diagnostics Warmup (Background) ===
    tdb.mark_stage_start(3)
    
    # Get startup metrics
    try:
        metrics = watchdog.get_metrics()
        if metrics['bind_time']:
            logger.info(f"[STABILIZER] Startup latency {metrics['bind_time']:.2f}s (tolerance: 6.0s)")
    except Exception as e:
        tdb.add_error(3, f"Watchdog metrics failed: {e}")
    
    # Deferred heartbeat
    try:
        from bridge_backend.runtime.heartbeat import heartbeat_loop
        asyncio.create_task(heartbeat_loop())
        logger.info("[HEARTBEAT] ✅ Initialized")
        watchdog.mark_heartbeat_initialized()
    except Exception as e:
        tdb.add_error(3, f"Heartbeat initialization failed: {e}")
        logger.warning(f"[TDB] Heartbeat initialization failed (continuing): {e}")
    
    # Predictive stabilizer warmup
    try:
        from bridge_backend.runtime.predictive_stabilizer import is_live
        is_live()
        logger.info("[STABILIZER] Predictive stabilizer initialized")
    except Exception as e:
        tdb.add_error(3, f"Predictive stabilizer failed: {e}")
        logger.warning(f"[TDB] Predictive stabilizer failed (continuing): {e}")
    
    # EnvSync background scheduler
    try:
        from bridge_backend.bridge_core.engines.envsync.tasks import run_scheduled_sync
        from bridge_backend.bridge_core.engines.envsync.config import CONFIG as ENVSYNC_CONFIG
        
        if ENVSYNC_CONFIG.enabled and ENVSYNC_CONFIG.schedule in ("@hourly", "@daily"):
            async def _envsync_loop():
                import asyncio
                while True:
                    await run_scheduled_sync()
                    # naive schedule
                    interval = 3600 if ENVSYNC_CONFIG.schedule == "@hourly" else 86400
                    await asyncio.sleep(interval)
            asyncio.create_task(_envsync_loop())
            logger.info(f"[ENVSYNC] ✅ Scheduled sync enabled ({ENVSYNC_CONFIG.schedule})")
    except Exception as e:
        tdb.add_error(3, f"EnvSync initialization failed: {e}")
        logger.warning(f"[TDB] EnvSync initialization failed (continuing): {e}")
    
    tdb.mark_stage_complete(3)
    
    # Save diagnostics
    try:
        tdb.save_diagnostics()
    except Exception as e:
        logger.warning(f"[TDB] Failed to save diagnostics: {e}")
    
    logger.info("[TDB] 🎉 All deployment stages complete - system fully ready")

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
    return {
        "ok": True,
        "status": "active",
        "version": app.version,
        "environment": os.getenv("ENVIRONMENT", "production")
    }

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
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("bridge_backend.main:app", host="0.0.0.0", port=port, reload=False)