import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SR-Albridge Backend", version="2.0.0")

# CORS middleware for all endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev/testing; use specific URLs for production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and add RBAC permission middleware
try:
    from bridge_core.middleware.permissions import PermissionMiddleware
except ImportError:
    from bridge_backend.bridge_core.middleware.permissions import PermissionMiddleware

app.add_middleware(PermissionMiddleware)

# Import and include all routers - using try/except for deployment compatibility
try:
    # Relative imports when running from bridge_backend directory
    from bridge_core.protocols.routes import router as protocols_router
    from bridge_core.protocols.complex_routes import router as complex_protocols_router
    from bridge_core.agents.routes import router as agents_router
    from bridge_core.routes_brain import router as brain_router
    from bridge_core.activity.routes import router as activity_router
    from bridge_core.missions.routes import router as missions_router
    from bridge_core.vault.routes import router as vault_router
    from bridge_core.fleet.routes import router as fleet_router
    from bridge_core.health.routes import router as health_router
    from bridge_core.system.routes import router as system_router
    from bridge_core.custody.routes import router as custody_router
    from bridge_core.console.routes import router as console_router
    from bridge_core.captains.routes import router as captains_router
    from bridge_core.guardians.routes import router as guardians_router, guardians_router
    from bridge_core.engines.autonomy.routes import router as autonomy_router
    from bridge_core.engines.parser.routes import router as parser_router
    from bridge_core.engines.recovery.routes import router as recovery_router
    from bridge_core.engines.routes_filing import router as filing_router
    from bridge_core.engines.truth.routes import router as truth_router
    from bridge_core.engines.indoctrination.routes import router as indoctrination_router
    from bridge_core.engines.agents_foundry.routes import router as agents_foundry_router
    from bridge_core.engines.speech.routes import router as speech_router
    from bridge_core.engines.screen.routes import router as screen_router
    from bridge_core.engines.leviathan.routes import router as leviathan_router
    from bridge_core.engines.leviathan.routes_solver import router as leviathan_solver_router
    from bridge_core.engines.creativity.routes import router as creativity_router
    from bridge_core.engines.cascade.routes import router as cascade_router
    from bridge_core.engines.blueprint.routes import router as blueprint_router
    from bridge_core.registry.routes import router as registry_router
    from bridge_core.protocols import storage as protocol_storage
    from bridge_core.permissions.routes import router as permissions_router
    from bridge_core.payments.stripe_webhooks import router as stripe_router
    from bridge_core.heritage.routes import router as heritage_router
    from bridge_core.scans.routes import router as scans_router
    from routes.control import router as control_router
    from routes.diagnostics_timeline import router as diagnostics_timeline_router
except ImportError:
    # Absolute imports when running from parent directory (Render deployment)
    from bridge_backend.bridge_core.protocols.routes import router as protocols_router
    from bridge_backend.bridge_core.protocols.complex_routes import router as complex_protocols_router
    from bridge_backend.bridge_core.agents.routes import router as agents_router
    from bridge_backend.bridge_core.routes_brain import router as brain_router
    from bridge_backend.bridge_core.activity.routes import router as activity_router
    from bridge_backend.bridge_core.missions.routes import router as missions_router
    from bridge_backend.bridge_core.vault.routes import router as vault_router
    from bridge_backend.bridge_core.fleet.routes import router as fleet_router
    from bridge_backend.bridge_core.health.routes import router as health_router
    from bridge_backend.bridge_core.system.routes import router as system_router
    from bridge_backend.bridge_core.custody.routes import router as custody_router
    from bridge_backend.bridge_core.console.routes import router as console_router
    from bridge_backend.bridge_core.captains.routes import router as captains_router
    from bridge_backend.bridge_core.guardians.routes import router as guardians_router, guardians_router
    from bridge_backend.bridge_core.engines.autonomy.routes import router as autonomy_router
    from bridge_backend.bridge_core.engines.parser.routes import router as parser_router
    from bridge_backend.bridge_core.engines.recovery.routes import router as recovery_router
    from bridge_backend.bridge_core.engines.routes_filing import router as filing_router
    from bridge_backend.bridge_core.engines.truth.routes import router as truth_router
    from bridge_backend.bridge_core.engines.indoctrination.routes import router as indoctrination_router
    from bridge_backend.bridge_core.engines.agents_foundry.routes import router as agents_foundry_router
    from bridge_backend.bridge_core.engines.speech.routes import router as speech_router
    from bridge_backend.bridge_core.engines.screen.routes import router as screen_router
    from bridge_backend.bridge_core.engines.leviathan.routes import router as leviathan_router
    from bridge_backend.bridge_core.engines.leviathan.routes_solver import router as leviathan_solver_router
    from bridge_backend.bridge_core.engines.creativity.routes import router as creativity_router
    from bridge_backend.bridge_core.engines.cascade.routes import router as cascade_router
    from bridge_backend.bridge_core.engines.blueprint.routes import router as blueprint_router
    from bridge_backend.bridge_core.registry.routes import router as registry_router
    from bridge_backend.bridge_core.protocols import storage as protocol_storage
    from bridge_backend.bridge_core.permissions.routes import router as permissions_router
    from bridge_backend.bridge_core.payments.stripe_webhooks import router as stripe_router
    from bridge_backend.bridge_core.heritage.routes import router as heritage_router
    from bridge_backend.bridge_core.scans.routes import router as scans_router
    from bridge_backend.routes.control import router as control_router
    from bridge_backend.routes.diagnostics_timeline import router as diagnostics_timeline_router

app.include_router(protocols_router)
app.include_router(complex_protocols_router)
app.include_router(agents_router)
app.include_router(brain_router)
app.include_router(activity_router)
app.include_router(missions_router)
app.include_router(vault_router)
app.include_router(fleet_router)
app.include_router(health_router)
app.include_router(system_router)
app.include_router(custody_router)
app.include_router(console_router)
app.include_router(captains_router)
app.include_router(guardians_router)
app.include_router(guardians_router)
app.include_router(autonomy_router)
app.include_router(parser_router)
app.include_router(recovery_router)
app.include_router(filing_router)
app.include_router(truth_router)
app.include_router(indoctrination_router)
app.include_router(agents_foundry_router)
app.include_router(speech_router)
app.include_router(screen_router)
app.include_router(leviathan_router)
app.include_router(leviathan_solver_router)
app.include_router(creativity_router)
app.include_router(cascade_router)
app.include_router(blueprint_router)
app.include_router(registry_router)
app.include_router(permissions_router)
app.include_router(stripe_router)
app.include_router(heritage_router)
app.include_router(scans_router)
app.include_router(control_router)
app.include_router(diagnostics_timeline_router)

# Load registry from vault at startup
protocol_storage.load_registry()

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
def root():
    return {"message": "SR-Albridge backend is running"}