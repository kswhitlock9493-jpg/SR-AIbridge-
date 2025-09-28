from fastapi import FastAPI

app = FastAPI(title="SR-Albridge Backend", version="2.0.0")

# Import and include all routers with full package path
from bridge_backend.bridge_core.protocols.routes import router as protocols_router
from bridge_backend.bridge_core.agents.routes import router as agents_router
from bridge_backend.bridge_core.brain.routes import router as brain_router
from bridge_backend.bridge_core.activity.routes import router as activity_router
from bridge_backend.bridge_core.guardians.routes import router as guardians_router
from bridge_backend.bridge_core.missions.routes import router as missions_router
from bridge_backend.bridge_core.vault.routes import router as vault_router
from bridge_backend.bridge_core.fleet.routes import router as fleet_router
from bridge_backend.bridge_core.health.routes import router as health_router
from bridge_backend.bridge_core.status.routes import router as status_router
from bridge_backend.bridge_core.admin.routes import router as admin_router
from bridge_backend.bridge_core.system.routes import router as system_router
from bridge_backend.bridge_core.chat.routes import router as chat_router

app.include_router(protocols_router)
app.include_router(agents_router)
app.include_router(brain_router)
app.include_router(activity_router)
app.include_router(guardians_router)
app.include_router(missions_router)
app.include_router(vault_router)
app.include_router(fleet_router)
app.include_router(health_router)
app.include_router(status_router)
app.include_router(admin_router)
app.include_router(system_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {"message": "SR-Albridge backend is running"}