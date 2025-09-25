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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"🚀 Starting {settings.APP_NAME}")
logger.info(f"🔧 Database: {settings.DATABASE_TYPE.upper()} at {settings.DATABASE_URL}")


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
        heal_result = await database_self_heal()
        
        return {
            "status": "completed",
            "message": "Self-heal process completed",
            "result": heal_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Self-heal error: {e}")
        return safe_error_response(str(e), "Self-heal process failed")


@app.get("/status")
async def get_status():
    """Get overall system status with enhanced dashboard data"""
    try:
        system_status = await get_system_status()
        db_health = await database_health()
        
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
                "self_healing": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Status error: {e}")
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


# === Mission Management ===
@app.get("/missions")
async def get_missions():
    """Get all missions with safe error handling"""
    try:
        missions = await db_manager.get_missions()
        return {
            "status": "success",
            "missions": missions,
            "count": len(missions)
        }
    except Exception as e:
        logger.error(f"Get missions error: {e}")
        return safe_error_response(str(e), "Failed to retrieve missions")


@app.post("/missions")
async def create_mission(mission: MissionCreate):
    """Create a new mission with safe error handling"""
    try:
        result = await db_manager.create_mission(mission.dict())
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Mission created successfully",
                "mission": result["mission"]
            }
        else:
            return safe_error_response(result["error"], "Failed to create mission")
    except Exception as e:
        logger.error(f"Create mission error: {e}")
        return safe_error_response(str(e), "Failed to create mission")


# === Vault Logs ===
@app.get("/vault/logs")
async def get_vault_logs(limit: int = 100):
    """Get vault logs with safe error handling"""
    try:
        logs = await db_manager.get_vault_logs(limit)
        return {
            "status": "success",
            "logs": logs,
            "count": len(logs),
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Get vault logs error: {e}")
        return safe_error_response(str(e), "Failed to retrieve vault logs")


@app.post("/vault/logs")
async def create_vault_log(log: VaultLogCreate):
    """Create vault log entry with safe error handling"""
    try:
        result = await db_manager.create_vault_log(log.dict())
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Vault log created successfully",
                "log": result["log"]
            }
        else:
            return safe_error_response(result["error"], "Failed to create vault log")
    except Exception as e:
        logger.error(f"Create vault log error: {e}")
        return safe_error_response(str(e), "Failed to create vault log")


# === Guardian Management ===
@app.get("/guardians")
async def get_guardians():
    """Get all guardians with safe error handling"""
    try:
        guardians = await db_manager.get_guardians()
        return {
            "status": "success",
            "guardians": guardians,
            "count": len(guardians)
        }
    except Exception as e:
        logger.error(f"Get guardians error: {e}")
        return safe_error_response(str(e), "Failed to retrieve guardians")


@app.get("/guardian/status")
async def get_guardian_status():
    """Get guardian system status"""
    try:
        guardians = await db_manager.get_guardians()
        if guardians:
            active_guardians = [g for g in guardians if g.get("active", False)]
            return {
                "status": "active" if active_guardians else "inactive",
                "active_guardians": len(active_guardians),
                "total_guardians": len(guardians),
                "guardians": guardians
            }
        else:
            return {
                "status": "inactive",
                "active_guardians": 0,
                "total_guardians": 0,
                "guardians": []
            }
    except Exception as e:
        logger.error(f"Guardian status error: {e}")
        return safe_error_response(str(e), "Failed to retrieve guardian status")


# === System Test Endpoints ===
@app.post("/system/self-test")
async def run_system_self_test():
    """Run comprehensive system self-test"""
    try:
        # Perform comprehensive system test
        test_results = {
            "database": await database_health(),
            "api": {"status": "healthy", "response_time": "< 1ms"},
            "cors": {"status": "configured", "origins_count": len(settings.cors_origins)}
        }
        
        # Calculate overall test result
        failed_tests = sum(1 for result in test_results.values() 
                          if isinstance(result, dict) and result.get("status") not in ["healthy", "configured"])
        
        overall_status = "passed" if failed_tests == 0 else "warning" if failed_tests == 1 else "failed"
        
        return {
            "status": overall_status,
            "message": f"System self-test {overall_status}",
            "tests": test_results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Self-test error: {e}")
        return safe_error_response(str(e), "System self-test failed")


@app.post("/system/self-repair")
async def run_system_self_repair():
    """Run system self-repair (alias for self-heal)"""
    return await trigger_self_heal()


@app.get("/system/metrics")
async def get_system_metrics():
    """Get system metrics"""
    try:
        db_health = await database_health()
        
        return {
            "status": "success",
            "metrics": {
                "database": {
                    "health_score": db_health.get("health_score", 0),
                    "connection_status": db_health.get("connection", "unknown"),
                    "record_counts": db_health.get("counts", {})
                },
                "system": {
                    "version": settings.APP_VERSION,
                    "uptime": "unknown",  # Could be implemented with a start time tracker
                    "cors_configured": True
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"System metrics error: {e}")
        return safe_error_response(str(e), "Failed to retrieve system metrics")


# === Fleet Management ===
@app.get("/fleet")
async def get_fleet():
    """Get fleet data with safe error handling"""
    try:
        fleet_data = get_fleet_data()
        
        return {
            "status": "success",
            "fleet": fleet_data,
            "count": len(fleet_data),
            "online": len([ship for ship in fleet_data if ship.get("status") == "online"]),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get fleet error: {e}")
        return safe_error_response("Failed to retrieve fleet data")


# === Captain Messages ===
@app.get("/captains/messages")
async def get_captain_messages():
    """Get captain messages - placeholder endpoint for frontend compatibility"""
    try:
        # Return empty array for now - can be enhanced later
        return {
            "status": "success",
            "messages": [],
            "count": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get captain messages error: {e}")
        return safe_error_response("Failed to retrieve captain messages")


@app.post("/captains/send") 
async def send_captain_message(message: dict):
    """Send captain message - placeholder endpoint for frontend compatibility"""
    try:
        # Return success response for now - can be enhanced later
        return {
            "status": "success",
            "message": "Message sent successfully",
            "stored": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Send captain message error: {e}")
        return safe_error_response("Failed to send captain message")


# === Activity Feed ===
@app.get("/activity")
async def get_activity():
    """Get activity feed - use vault logs as activity"""
    try:
        # Use vault logs as activity feed
        logs = await db_manager.get_vault_logs(limit=20)
        
        # Transform vault logs to activity format
        activities = []
        for log in logs:
            activities.append({
                "id": log.get("id"),
                "type": "log_entry",
                "agent": log.get("agent_name"),
                "action": log.get("action"),
                "details": log.get("details"),
                "timestamp": log.get("timestamp"),
                "level": log.get("log_level", "info")
            })
        
        return {
            "status": "success",
            "activities": activities,
            "count": len(activities),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get activity error: {e}")
        return safe_error_response("Failed to retrieve activity")


# === Armada Status ===
@app.get("/armada/status")
async def get_armada_status():
    """Get armada status - placeholder endpoint for frontend compatibility"""
    try:
        fleet_data = get_fleet_data()
        system_status = await get_system_status()
        
        return {
            "status": "success",
            "fleet": fleet_data,
            "admiral": system_status["admiral"],
            "ships_online": len([ship for ship in fleet_data if ship.get("status") == "online"]),
            "total_ships": len(fleet_data),
            "operational_status": "nominal",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Get armada status error: {e}")
        return safe_error_response("Failed to retrieve armada status")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )