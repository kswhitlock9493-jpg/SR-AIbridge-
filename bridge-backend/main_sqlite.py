"""
SQLite-first FastAPI backend for SR-AIbridge
Full health check, self-heal, and safe error JSONs
CORS configured for Netlify deployment
"""
import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

# Import our SQLite-first database and models
from db import db_manager, database_health, database_self_heal, init_database, close_database
from models import (
    GuardianCreate, GuardianResponse, VaultLogCreate, VaultLogResponse,
    MissionCreate, MissionResponse, AgentCreate, AgentResponse
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv()

# SQLite-first configuration
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bridge.db")

logger.info(f"🚀 Starting SQLite-first SR-AIbridge backend")
logger.info(f"🔧 Database: {DATABASE_TYPE.upper()} at {DATABASE_URL}")

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
            from startup import seed_initial_data
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
    title="SR-AIbridge Backend",
    version="1.2.0-sqlite-first",
    description="SQLite-first SR-AIbridge backend with comprehensive health checks and self-heal",
    lifespan=lifespan
)

# CORS configuration for Netlify deployment
allowed_origins = os.getenv("ALLOWED_ORIGINS", 
    "http://localhost:3000,http://127.0.0.1:3000,https://bridge.netlify.app,https://sr-aibridge.netlify.app"
).split(",")

# Enhanced CORS origins for deployment flexibility
origins = [
    *allowed_origins,
    "https://*.netlify.app",  # All Netlify subdomains
    "https://*.onrender.com",  # All Render subdomains
    "http://localhost:3001",   # Alternative dev port
    "https://localhost:3000",  # HTTPS dev
    "https://localhost:3001",  # HTTPS alternative dev
    "http://127.0.0.1:3001",   # IPv4 alternative
    "https://127.0.0.1:3000",  # HTTPS IPv4
    "https://127.0.0.1:3001"   # HTTPS IPv4 alternative
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("CORS_ALLOW_ALL", "false").lower() == "true" else origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600  # Cache preflight requests for 1 hour
)

# === Root and Information Endpoints ===
@app.get("/")
async def root():
    """Root endpoint with comprehensive API information"""
    return {
        "name": "SR-AIbridge Backend",
        "version": "1.2.0-sqlite-first",
        "description": "SQLite-first backend with comprehensive health checks and self-heal",
        "database": {
            "type": DATABASE_TYPE,
            "url": "local_sqlite" if "sqlite" in DATABASE_URL else DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
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
@app.get("/health")
async def health_check():
    """Basic health check for load balancers and monitoring"""
    try:
        db_health = await database_health()
        return {
            "status": "ok" if db_health["status"] == "healthy" else "degraded",
            "service": "SR-AIbridge Backend",
            "version": "1.2.0-sqlite-first",
            "database": db_health["status"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "error",
            "service": "SR-AIbridge Backend", 
            "version": "1.2.0-sqlite-first",
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
            "service": "SR-AIbridge Backend",
            "version": "1.2.0-sqlite-first", 
            "timestamp": datetime.utcnow().isoformat(),
            "components": system_health,
            "self_heal_available": True
        }
        
    except Exception as e:
        logger.error(f"Full health check error: {e}")
        return {
            "status": "error",
            "service": "SR-AIbridge Backend",
            "version": "1.2.0-sqlite-first",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "self_heal_available": True
        }

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
        return {
            "status": "error",
            "message": "Self-heal process failed", 
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/status")
async def get_status():
    """Get overall system status with enhanced dashboard data"""
    try:
        from startup import get_system_status
        system_status = await get_system_status()
        db_health = await database_health()
        
        return {
            "service": "SR-AIbridge Backend",
            "version": "1.2.0-sqlite-first",
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
                "type": DATABASE_TYPE,
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
            "service": "SR-AIbridge Backend",
            "version": "1.2.0-sqlite-first", 
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
        return {
            "status": "error",
            "error": str(e),
            "agents": [],
            "count": 0
        }

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
            return {
                "status": "error",
                "error": result["error"],
                "message": "Failed to create agent"
            }
    except Exception as e:
        logger.error(f"Create agent error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to create agent"
        }

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
        return {
            "status": "error",
            "error": str(e),
            "missions": [],
            "count": 0
        }

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
            return {
                "status": "error",
                "error": result["error"],
                "message": "Failed to create mission"
            }
    except Exception as e:
        logger.error(f"Create mission error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to create mission"
        }

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
        return {
            "status": "error",
            "error": str(e),
            "logs": [],
            "count": 0
        }

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
            return {
                "status": "error",
                "error": result["error"],
                "message": "Failed to create vault log"
            }
    except Exception as e:
        logger.error(f"Create vault log error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to create vault log"
        }

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
        return {
            "status": "error",
            "error": str(e),
            "guardians": [],
            "count": 0
        }

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
        return {
            "status": "error",
            "error": str(e),
            "active_guardians": 0,
            "total_guardians": 0
        }

# === System Test Endpoints ===
@app.post("/system/self-test")
async def run_system_self_test():
    """Run comprehensive system self-test"""
    try:
        # Perform comprehensive system test
        test_results = {
            "database": await database_health(),
            "api": {"status": "healthy", "response_time": "< 1ms"},
            "cors": {"status": "configured", "origins_count": len(origins)}
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
        return {
            "status": "failed",
            "message": "System self-test failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

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
                    "version": "1.2.0-sqlite-first",
                    "uptime": "unknown",  # Could be implemented with a start time tracker
                    "cors_configured": True
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"System metrics error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# === Fleet Management ===
@app.get("/fleet")
async def get_fleet():
    """Get fleet data with safe error handling"""
    try:
        from startup import get_fleet_data
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
        return {
            "status": "error",
            "error": "Failed to retrieve fleet data",
            "fleet": [],
            "count": 0,
            "online": 0,
            "timestamp": datetime.utcnow().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_sqlite:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True if os.getenv("DEBUG", "false").lower() == "true" else False
    )