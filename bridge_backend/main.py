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

# Import and include all routers - using try/except for deployment compatibility
try:
    # Relative imports when running from bridge_backend directory
    from bridge_core.protocols.routes import router as protocols_router
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
except ImportError:
    # Absolute imports when running from parent directory (Render deployment)
    from bridge_backend.bridge_core.protocols.routes import router as protocols_router
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

app.include_router(protocols_router)
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

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {"message": "SR-Albridge backend is running"}