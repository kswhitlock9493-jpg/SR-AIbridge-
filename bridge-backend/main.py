"""
SQLite-first FastAPI backend for SR-AIbridge
Clean async architecture with comprehensive health checks and self-heal
CORS configured for Netlify deployment
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
from datetime import datetime

# Import configuration and database
from config import settings
from db import db_manager, database_health, database_self_heal, init_database, close_database
from schemas import (
    GuardianCreate, GuardianResponse, VaultLogCreate, VaultLogResponse,
    MissionCreate, MissionResponse, AgentCreate, AgentResponse,
    SystemStatusResponse, HealthCheckResponse, ErrorResponse
)
from seed import seed_initial_data, get_fleet_data, get_system_status

# Import bridge_core modules
from bridge_core.claude_watcher import ClaudeWatcher
from bridge_core.fault_injector import FaultInjector
from bridge_core.self_healing_adapter import SelfHealingMASAdapter
from bridge_core.federation_client import FederationClient
from bridge_core.registry_payloads import current_registry_payloads

# Import Sovereign Brain routes
from bridge_core.routes_brain import router as brain_router
from bridge_core.custody.routes import router as custody_router
# Import protocol lore/policy routes (PR 1A-2l)
from bridge_core.protocols import routes as protocols_routes
# Import agents routes (PR 1A-2o)
from bridge_core.agents.routes import router as agents_router
# Import vault routes (PR 1A-2r)
from bridge_core.vault.routes import router as vault_router
# Import activity routes (PR 1A-2s)
from bridge_core.activity.routes import router as activity_router
# Import guardians routes (PR 1A-2t)
from bridge_core.guardians.routes import router as guardians_router
# Import missions routes (PR 1A-2u)
from bridge_core.missions.routes import router as missions_router
# Import fleet routes (PR 1A-2w)
from bridge_core.fleet.routes import router as fleet_router
# Import system routes (PR 1A-2y)
from bridge_core.system.routes import router as system_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"🚀 Starting {settings.APP_NAME}")
logger.info(f"🔧 Database: {settings.DATABASE_TYPE.upper()} at {settings.DATABASE_URL}")

# Initialize bridge_core modules
claude_watcher = ClaudeWatcher(retention_hours=24)
fault_injector = FaultInjector(enabled=settings.FAULT_INJECTION_ENABLED if hasattr(settings, 'FAULT_INJECTION_ENABLED') else False)
self_healing_adapter = SelfHealingMASAdapter(max_retries=3, healing_timeout=300)
federation_client = FederationClient(
    node_id=f"sr-bridge-{settings.APP_NAME.lower().replace(' ', '-')}",
    node_name=settings.APP_NAME,
    endpoint=settings.BASE_URL if hasattr(settings, 'BASE_URL') else "http://localhost:8000"
)

logger.info("🔧 Bridge core modules initialized")
logger.info(f"📊 ClaudeWatcher: Event monitoring active")
logger.info(f"⚠️ FaultInjector: {'ENABLED' if fault_injector.enabled else 'DISABLED'}")
logger.info(f"🔄 SelfHealingAdapter: Recovery protocols loaded")
logger.info(f"🌐 FederationClient: Node {federation_client.node_id} ready")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan handler for startup and shutdown"""
    try:
        # Initialize database on startup
        logger.info("🔄 Initializing SQLite-first database...")
        init_result = await init_database()
        if init_result["status"] == "success":
            logger.info("✅ Database initialized successfully")
            
            # Seed initial demo data
            logger.info("🌱 Seeding initial demo data...")
            seed_result = await seed_initial_data()
            if seed_result["status"] == "success":
                if seed_result.get("skipped"):
                    logger.info("ℹ️ Demo data already exists, skipping seeding")
                else:
                    logger.info(f"✅ Successfully seeded: {', '.join(seed_result['seeded_items'])}")
                    logger.info(f"📊 Admiral: {seed_result.get('admiral', 'Unknown')}")
                    logger.info(f"🤖 Agents: {seed_result.get('agents_count', 0)}")
                    logger.info(f"🎯 Missions: {seed_result.get('missions_count', 0)}")
                    logger.info(f"🚢 Fleet Online: {seed_result.get('fleet_online', 0)}")
            else:
                logger.warning(f"⚠️ Seeding incomplete: {seed_result['message']}")
        else:
            logger.error(f"❌ Database initialization failed: {init_result['message']}")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        yield
    finally:
        # Clean shutdown
        logger.info("🛑 Shutting down database connection...")
        await close_database()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan
)

# CORS configuration for Netlify deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.CORS_ALLOW_ALL else settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600  # Cache preflight requests for 1 hour
)

# Include Sovereign Brain routers
app.include_router(brain_router)
app.include_router(custody_router)
# Include protocol lore/policy routes  
app.include_router(protocols_routes.router)
# Include agents routes
app.include_router(agents_router)
# Include vault routes
app.include_router(vault_router)
# Include activity routes
app.include_router(activity_router)
# Include guardians routes
app.include_router(guardians_router)
# Include missions routes
app.include_router(missions_router)
# Include fleet routes
app.include_router(fleet_router)
# Include system routes
app.include_router(system_router)

logger.info("🧠 Sovereign Brain routes included")
logger.info("🔑 Custody routes included")
logger.info("📜 Protocol lore/policy routes included")
logger.info("🤖 Agents routes included")
logger.info("🗃️ Vault routes included")
logger.info("📈 Activity routes included")
logger.info("🛡️ Guardians routes included")
logger.info("🎯 Missions routes included")
logger.info("🚢 Fleet routes included")
logger.info("⚡ System routes included")


def safe_error_response(error: str, message: str = None) -> Dict[str, Any]:
    """Create safe error response without exposing internals"""
    return {
        "status": "error",
        "error": error,
        "message": message or "An error occurred",
        "timestamp": datetime.utcnow().isoformat(),
        "self_heal_available": True
    }


# === Root and Information Endpoints ===
@app.get("/")
async def root():
    """Root endpoint with comprehensive API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "database": {
            "type": settings.DATABASE_TYPE,
            "url": "local_sqlite" if "sqlite" in settings.DATABASE_URL else settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL
        },
        "endpoints": {
            "health": "/health",
            "health_full": "/health/full",
            "self_heal": "/health/self-heal",
            "status": "/status",
            "agents": "/agents",
            "missions": "/missions",
            "fleet": "/fleet",
            "vault_logs": "/vault/logs",
            "guardians": "/guardians"
        },
        "features": {
            "sqlite_first": True,
            "health_monitoring": True,
            "self_healing": True,
            "safe_error_handling": True,
            "cors_netlify_ready": True
        },
        "ready": True
    }


# === Health Check Endpoints ===
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Basic health check for load balancers and monitoring"""
    try:
        db_health = await database_health()
        return {
            "status": "ok" if db_health["status"] == "healthy" else "degraded",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "database": db_health["status"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "error",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "error": "Health check failed",
            "timestamp": datetime.utcnow().isoformat()
        }


@app.get("/health/full")
async def full_health_check():
    """Comprehensive health check with system details"""
    try:
        db_health = await database_health()
        
        # System health assessment
        system_health = {
            "database": db_health,
            "api": {"status": "healthy", "endpoints_active": True},
            "cors": {"status": "configured", "netlify_ready": True}
        }
        
        # Calculate overall health
        unhealthy_components = sum(1 for comp in system_health.values() 
                                  if isinstance(comp, dict) and comp.get("status") not in ["healthy", "configured"])
        
        overall_status = "healthy" if unhealthy_components == 0 else "degraded" if unhealthy_components == 1 else "unhealthy"
        
        return {
            "status": overall_status,
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "timestamp": datetime.utcnow().isoformat(),
            "components": system_health,
            "self_heal_available": True
        }
        
    except Exception as e:
        logger.error(f"Full health check error: {e}")
        return safe_error_response(str(e), "Full health check failed")


@app.post("/health/self-heal")
async def trigger_self_heal():
    """Trigger system self-healing process"""
    try:
        logger.info("🔄 Triggering self-heal process...")
        
        # Log self-heal event
        from bridge_core.claude_watcher import EventType, Severity
        claude_watcher.log_event(
            EventType.SYSTEM_HEALTH,
            Severity.HIGH,
            "self_heal_api",
            "System self-heal process initiated",
            {"trigger": "manual_api_call"}
        )
        
        heal_result = await database_self_heal()
        
        # Log completion
        claude_watcher.log_event(
            EventType.SYSTEM_HEALTH,
            Severity.LOW,
            "self_heal_api",
            "System self-heal process completed successfully",
            {"result": heal_result}
        )
        
        return {
            "status": "completed",
            "message": "Self-heal process completed",
            "result": heal_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Self-heal error: {e}")
        # Log failure
        from bridge_core.claude_watcher import EventType, Severity
        claude_watcher.log_event(
            EventType.ERROR_DETECTED,
            Severity.CRITICAL,
            "self_heal_api",
            f"System self-heal process failed: {str(e)}",
            {"error": str(e)}
        )
        return safe_error_response(str(e), "Self-heal process failed")


@app.get("/status")
async def get_status():
    """Get overall system status with enhanced dashboard data"""
    try:
        system_status = await get_system_status()
        db_health = await database_health()
        
        # Get ClaudeWatcher analysis for enhanced metrics
        analysis = claude_watcher.get_system_analysis()
        
        return {
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": db_health["status"],
            # Enhanced status data matching frontend expectations
            "admiral": system_status["admiral"],
            "agents_online": system_status["agents_online"],
            "agentsOnline": system_status["agents_online"],  # Alternative naming for compatibility
            "active_missions": system_status["active_missions"],
            "activeMissions": system_status["active_missions"],  # Alternative naming for compatibility
            "total_agents": system_status["total_agents"],
            "total_missions": system_status["total_missions"],
            "fleet_count": system_status["fleet_count"],
            "vault_logs": system_status["vault_logs"],
            "system_health": system_status["system_health"],
            "database": {
                "type": settings.DATABASE_TYPE,
                "status": db_health["status"],
                "counts": db_health.get("counts", {}),
                "health_score": db_health.get("health_score", 0)
            },
            "features": {
                "sqlite_first": True,
                "health_monitoring": True,
                "self_healing": True,
                "claude_watcher": True,
                "fault_injection": fault_injector.enabled,
                "federation": federation_client.federation_enabled
            },
            # ClaudeWatcher integration
            "claude_watcher": {
                "health_score": analysis["health_score"],
                "recent_events": analysis["total_events_1h"],
                "event_trend": analysis["event_trend"],
                "recommendations": analysis["recommendations"][:3]  # Top 3 recommendations
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Status error: {e}")
        # Log error event
        from bridge_core.claude_watcher import EventType, Severity
        claude_watcher.log_event(
            EventType.ERROR_DETECTED,
            Severity.HIGH,
            "status_api",
            f"Status endpoint error: {str(e)}",
            {"error": str(e)}
        )
        return {
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "error",
            "admiral": "Unknown",
            "agents_online": 0,
            "agentsOnline": 0,
            "active_missions": 0,
            "activeMissions": 0,
            "total_agents": 0,
            "total_missions": 0,
            "fleet_count": 0,
            "vault_logs": 0,
            "system_health": "error",
            "error": "Failed to retrieve system status",
            "self_heal_available": True,
            "timestamp": datetime.utcnow().isoformat()
        }


# (Remaining endpoints unchanged below this point)
# ... KEEP THE REST OF ORIGINAL FILE CONTENT UNCHANGED ...

# === Agent Management ===
@app.get("/agents")
async def get_agents():
    """Get all agents with safe error handling"""
    try:
        agents = await db_manager.get_agents()
        return {
            "status": "success",
            "agents": agents,
            "count": len(agents)
        }
    except Exception as e:
        logger.error(f"Get agents error: {e}")
        return safe_error_response(str(e), "Failed to retrieve agents")

@app.post("/agents")
async def create_agent(agent: AgentCreate):
    """Create a new agent with safe error handling"""
    try:
        result = await db_manager.create_agent(agent.dict())
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Agent created successfully",
                "agent": result["agent"]
            }
        else:
            return safe_error_response(result["error"], "Failed to create agent")
    except Exception as e:
        logger.error(f"Create agent error: {e}")
        return safe_error_response(str(e), "Failed to create agent")



# === Vault Log Endpoints ===
@app.get("/vault/logs")
async def get_vault_logs(limit: int = 100):
    """Get vault logs with safe error handling"""
    try:
        logs = await db_manager.get_vault_logs(limit=limit)
        return logs
    except Exception as e:
        logger.error(f"Get vault logs error: {e}")
        return safe_error_response(str(e), "Failed to retrieve vault logs")


@app.post("/vault/logs")
async def create_vault_log(log: VaultLogCreate):
    """Create a new vault log entry with safe error handling"""
    try:
        result = await db_manager.create_vault_log(log.dict())
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Log entry created successfully", 
                "log": result["log"]
            }
        else:
            return safe_error_response(result["error"], "Failed to create log entry")
    except Exception as e:
        logger.error(f"Create vault log error: {e}")
        return safe_error_response(str(e), "Failed to create log entry")


# === Activity Feed Endpoint ===
# Activity routes now handled by bridge_core.activity.routes router
# Guardian routes now handled by bridge_core.guardians.routes router


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )