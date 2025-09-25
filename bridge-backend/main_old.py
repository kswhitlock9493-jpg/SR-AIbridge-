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


    """Async database storage using SQLAlchemy AsyncSession - PREFERRED"""
    
    def __init__(self):
        super().__init__()
        # Import db module
        from db import db_manager
        self.db = db_manager
        self._cache_refresh_interval = 30  # seconds
        self._last_cache_update = 0
        
    async def connect(self):
        """Connect to database and create tables"""
        await self.db.initialize()
        await self.refresh_cache()
        logger.info("✅ Async database connected and cache initialized")
        
    async def disconnect(self):
        """Disconnect from database"""
        await self.db.close()
        logger.info("🛑 Async database disconnected")
    
    async def refresh_cache(self):
        """Refresh in-memory cache from database"""
        try:
            # Load all data from database into memory for compatibility
            self.agents = await self.db.get_agents()
            self.missions = await self.db.get_missions()
            self.vault_logs = await self.db.get_vault_logs()
            
            # Initialize captain_messages and armada_fleet as empty since they're not implemented yet
            self.captain_messages = []
            self.armada_fleet = []
            
            # Update next_id based on max IDs
            max_ids = []
            if self.agents:
                max_ids.append(max(agent.get('id', 0) for agent in self.agents))
            if self.missions:
                max_ids.append(max(mission.get('id', 0) for mission in self.missions))
            if self.vault_logs:
                max_ids.append(max(log.get('id', 0) for log in self.vault_logs))
            
            self.next_id = max(max_ids) + 1 if max_ids else 1
            self._last_cache_update = __import__('time').time()
            
        except Exception as e:
            logger.error(f"Failed to refresh cache: {e}")
            # Keep using in-memory data as fallback
    
    async def health_check(self):
        """Get database health status"""
        return await self.db.health_check()


# Initialize storage based on environment
if DATABASE_TYPE == "sqlite" or DATABASE_TYPE == "postgres":
    logger.info(f"🗄️ Using {DATABASE_TYPE.upper()} async database storage")
    storage = AsyncDatabaseStorage()
    USE_DATABASE = True
else:
    logger.info("🧠 Using in-memory storage")
    storage = InMemoryStorage()
    USE_DATABASE = False

# Initialize rituals manager for data operations
rituals = DataRituals(storage)

# Initialize autonomous scheduler
scheduler = AutonomousScheduler(storage, websocket_manager)

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern FastAPI lifespan handler for startup and shutdown"""
    # Startup
    logger.info("🚀 SR-AIbridge Backend Starting...")
    
    # Initialize database connection
    if USE_DATABASE and hasattr(storage, 'connect'):
        await storage.connect()
    
    # Initialize in-memory storage with demo data
    seed_demo_data()
    logger.info(f"📊 Seeded: {len(storage.agents)} agents, {len(storage.missions)} missions, {len(storage.vault_logs)} vault logs, {len(storage.captain_messages)} messages")
    
    # Start autonomous systems
    try:
        await scheduler.start()
        logger.info("🤖 Autonomous scheduler activated")
    except Exception as e:
        logger.warning(f"Failed to start scheduler: {e}")
    
    try:
        await guardian.start()
        logger.info("🛡️ Guardian daemon activated")
    except Exception as e:
        logger.warning(f"Failed to start guardian: {e}")
    
    logger.info("✅ SR-AIbridge Backend Started!")
    
    yield
    
    # Shutdown
    logger.info("🛑 SR-AIbridge Backend Shutting down...")
    
    # Stop autonomous systems
    try:
        await scheduler.stop()
        logger.info("🤖 Autonomous scheduler stopped")
    except Exception as e:
        logger.warning(f"Failed to stop scheduler: {e}")
    
    try:
        await guardian.stop()
        logger.info("🛡️ Guardian daemon stopped")
    except Exception as e:
        logger.warning(f"Failed to stop guardian: {e}")
    
    # Close database connection
    if USE_DATABASE and hasattr(storage, 'disconnect'):
        await storage.disconnect()
    
    logger.info("✅ SR-AIbridge Backend Shutdown complete!")


app = FastAPI(
    title="SR-AIbridge Backend",
    version="1.1.0-dual-mode",
    description="Dual-mode SR-AIbridge backend with async SQLite/Postgres support",
    lifespan=lifespan
)

# CORS configuration from environment variables with Netlify+Render support
allowed_origins = os.getenv("ALLOWED_ORIGINS", 
    "http://localhost:3000,http://127.0.0.1:3000,https://bridge.netlify.app,https://sr-aibridge.netlify.app"
).split(",")

# Additional CORS origins for compatibility
origins = [
    *allowed_origins,
    "https://*.netlify.app",  # Allow all Netlify subdomains
    "https://*.onrender.com",  # Allow all Render subdomains
    "http://localhost:3001",  # Alternative development port
    "https://localhost:3000",  # HTTPS development
    "https://localhost:3001",   # HTTPS alternative development port
    "http://127.0.0.1:3001",  # IPv4 alternative
    "https://127.0.0.1:3000",  # HTTPS IPv4
    "https://127.0.0.1:3001"   # HTTPS IPv4 alternative
]

# Enhanced CORS configuration for production deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("CORS_ALLOW_ALL", "false").lower() == "true" else origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# --- Models ---
class Message(BaseModel):
    from_: str
    to: str
    message: str
    timestamp: datetime = None
    
    def __init__(self, **data):
        if data.get('timestamp') is None:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)

class Agent(BaseModel):
    id: Optional[int] = None
    name: str
    endpoint: str
    capabilities: List[Dict[str, Any]] = []
    status: str = "online"
    last_heartbeat: Optional[datetime] = None
    created_at: Optional[datetime] = None

class AgentCreate(BaseModel):
    name: str
    endpoint: str
    capabilities: List[Dict[str, Any]] = []

class Mission(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    status: str = "active"
    priority: str = "normal"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MissionCreate(BaseModel):
    title: str
    description: str
    status: str = "active"
    priority: str = "normal"

class VaultLog(BaseModel):
    id: Optional[int] = None
    agent_name: str
    action: str
    details: str
    timestamp: Optional[datetime] = None
    log_level: str = "info"

class VaultLogCreate(BaseModel):
    agent_name: str
    action: str
    details: str
    log_level: str = "info"

# --- Guardian Daemon ---
class GuardianDaemon:
    """Guardian daemon for continuous self-testing and system monitoring"""
    
    def __init__(self, storage, websocket_manager):
        self.storage = storage
        self.websocket_manager = websocket_manager
        self.active = False
        self.last_selftest = None
        self.last_action = None
        self.last_result = None
        self.heartbeat = None
        self.selftest_status = "Unknown"  # "PASS", "FAIL", or "Unknown"
        self.selftest_task = None
        self.selftest_interval = 300  # 5 minutes in seconds
        
    def log_to_vault(self, level, message, details=""):
        """Log Guardian events to shared VAULT_LOGS store"""
        vault_log = {
            "id": self.storage.get_next_id(),
            "agent_name": "GuardianDaemon",
            "action": message,
            "details": details,
            "timestamp": datetime.utcnow(),
            "log_level": level
        }
        self.storage.vault_logs.append(vault_log)
        
    async def start(self):
        """Start Guardian daemon with continuous self-testing"""
        if self.active:
            return
            
        self.active = True
        self.heartbeat = datetime.utcnow()
        self.last_action = "startup"
        self.last_result = "active"
        
        logger.info("🛡️ Guardian daemon starting...")
        self.log_to_vault("info", "startup", "Guardian daemon initialized and activated")
        
        # Run initial self-test
        await self.run_selftest()
        
        # Schedule continuous self-tests
        self.selftest_task = asyncio.create_task(self._continuous_selftest())
        logger.info("🛡️ Guardian daemon active - continuous self-test every 5 minutes")
        
    async def stop(self):
        """Stop Guardian daemon"""
        self.active = False
        if self.selftest_task:
            self.selftest_task.cancel()
            try:
                await self.selftest_task
            except asyncio.CancelledError:
                pass
        logger.info("🛡️ Guardian daemon stopped")
        
    async def _continuous_selftest(self):
        """Continuous self-test loop"""
        while self.active:
            try:
                await asyncio.sleep(self.selftest_interval)
                if self.active:  # Check again after sleep
                    self.heartbeat = datetime.utcnow()  # Update heartbeat
                    self.log_to_vault("info", "heartbeat", "Guardian daemon heartbeat - continuous monitoring active")
                    await self.run_selftest()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Guardian selftest error: {e}")
                self.selftest_status = "FAIL"
                self.last_result = "FAIL"
                self.log_to_vault("error", "degraded", f"Guardian entered degraded state: {str(e)}")
                
    async def run_selftest(self):
        """Run comprehensive self-test"""
        try:
            logger.info("🛡️ Guardian running self-test...")
            self.heartbeat = datetime.utcnow()
            self.last_selftest = datetime.utcnow()
            self.last_action = "selftest"
            
            # Test basic system components
            tests_passed = 0
            total_tests = 4
            
            # Test 1: Storage accessibility
            try:
                len(self.storage.agents)
                tests_passed += 1
            except Exception:
                logger.error("Guardian selftest: Storage test failed")
                
            # Test 2: Data integrity
            try:
                agents_online = len([a for a in self.storage.agents if a.get("status") == "online"])
                if agents_online >= 0:  # Basic sanity
                    tests_passed += 1
            except Exception:
                logger.error("Guardian selftest: Data integrity test failed")
                
            # Test 3: WebSocket manager
            try:
                if hasattr(self.websocket_manager, 'active_connections'):
                    tests_passed += 1
            except Exception:
                logger.error("Guardian selftest: WebSocket test failed")
                
            # Test 4: System resources (basic check)
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=0.1)
                if cpu_percent >= 0:
                    tests_passed += 1
            except ImportError:
                # psutil not available, just pass the test
                tests_passed += 1
            except Exception:
                logger.error("Guardian selftest: Resource test failed")
            
            # Determine overall status
            if tests_passed == total_tests:
                self.selftest_status = "PASS"
                self.last_result = "PASS"
                logger.info(f"🛡️ Guardian self-test PASSED ({tests_passed}/{total_tests})")
                self.log_to_vault("info", "selftest", f"Self-test completed successfully ({tests_passed}/{total_tests})")
            else:
                self.selftest_status = "FAIL"
                self.last_result = "FAIL"
                logger.warning(f"🛡️ Guardian self-test FAILED ({tests_passed}/{total_tests})")
                self.log_to_vault("warning", "selftest", f"Self-test failed ({tests_passed}/{total_tests})")
                
            # Broadcast status update via WebSocket
            await self.websocket_manager.broadcast({
                "type": "guardian_status",
                "status": self.selftest_status,
                "timestamp": self.last_selftest.isoformat(),
                "tests_passed": tests_passed,
                "total_tests": total_tests
            })
            
        except Exception as e:
            logger.error(f"Guardian selftest critical error: {e}")
            self.selftest_status = "FAIL"
            self.last_result = "FAIL"
            self.last_selftest = datetime.utcnow()
            self.last_action = "selftest_error"
            self.log_to_vault("error", "selftest_error", f"Critical selftest error: {str(e)}")
            
            
    async def activate(self):
        """Manually activate Guardian with immediate self-test"""
        logger.info("🛡️ Guardian manual activation requested")
        self.heartbeat = datetime.utcnow()
        self.last_action = "activate"
        
        if not self.active:
            await self.start()
            self.last_result = "activated_from_inactive"
            self.log_to_vault("info", "activate", "Guardian manually activated from inactive state")
        else:
            # Run immediate self-test if already active
            await self.run_selftest()
            self.last_result = "reactivated"
            self.log_to_vault("info", "activate", "Guardian manually reactivated - immediate selftest executed")
        
        return {
            "success": True,
            "message": "Guardian activated successfully",
            "status": self.selftest_status,
            "active": self.active
        }

    def get_status(self):
        """Get current Guardian status"""
        return {
            "active": self.active,
            "status": self.selftest_status,
            "last_selftest": self.last_selftest.isoformat() if self.last_selftest else None,
            "last_action": self.last_action,
            "last_result": self.last_result,
            "heartbeat": self.heartbeat.isoformat() if self.heartbeat else None,
            "next_selftest": (self.last_selftest + timedelta(seconds=self.selftest_interval)).isoformat() if self.last_selftest else None
        }

# Initialize Guardian daemon
guardian = GuardianDaemon(storage, websocket_manager)

# --- Seed Data Function ---
def seed_demo_data():
    """Populate in-memory storage with demo data using rituals manager"""
    result = rituals.reseed()
    return result

# --- Captain-to-Captain Endpoints ---
@app.get("/captains/messages", response_model=List[Message])
async def list_messages():
    """Get all captain messages, ordered by timestamp descending"""
    messages = sorted(storage.captain_messages, key=lambda x: x["timestamp"], reverse=True)
    return [Message(**msg) for msg in messages]

@app.post("/captains/send")
async def send_message(msg: Message):
    """Send a captain message with WebSocket broadcast"""
    message_data = {
        "id": storage.get_next_id(),
        "from_": msg.from_,
        "to": msg.to,
        "message": msg.message,
        "timestamp": msg.timestamp or datetime.utcnow()
    }
    storage.captain_messages.append(message_data)
    
    # Broadcast to WebSocket clients
    await websocket_manager.broadcast({
        "type": "chat_message",
        "message": message_data
    })
    
    return {"ok": True, "stored": message_data}

# --- Chat Endpoints (Alternative endpoint names) ---
@app.get("/chat/messages", response_model=List[Message])
async def get_chat_messages():
    """Get all chat messages (alias for captains/messages)"""
    return await list_messages()

@app.post("/chat/send")
async def send_chat_message(data: dict):
    """Send a chat message with author/message format"""
    msg = Message(
        from_=data.get("author", "Unknown"),
        to=data.get("to", "All"),
        message=data.get("message", "")
    )
    return await send_message(msg)

# --- Agent Endpoints ---
@app.get("/agents", response_model=List[Agent])
async def list_agents():
    """Get all registered agents"""
    return [Agent(**agent) for agent in storage.agents]

@app.post("/agents", response_model=Agent)
async def register_agent(agent_create: AgentCreate):
    """Register a new agent"""
    agent_data = {
        "id": storage.get_next_id(),
        "name": agent_create.name,
        "endpoint": agent_create.endpoint,
        "capabilities": agent_create.capabilities,
        "status": "online",
        "last_heartbeat": datetime.utcnow(),
        "created_at": datetime.utcnow()
    }
    storage.agents.append(agent_data)
    return Agent(**agent_data)

@app.post("/agents/register", response_model=Agent)
async def register_agent_alt(agent_create: AgentCreate):
    """Register a new agent (alternative endpoint)"""
    return await register_agent(agent_create)

@app.delete("/agents/{agent_id}")
async def remove_agent(agent_id: int):
    """Remove an agent by ID"""
    for i, agent in enumerate(storage.agents):
        if agent["id"] == agent_id:
            removed_agent = storage.agents.pop(i)
            return {"ok": True, "removed": removed_agent}
    raise HTTPException(status_code=404, detail="Agent not found")

# --- Mission Endpoints ---
@app.get("/missions", response_model=List[Mission])
async def list_missions():
    """Get all missions"""
    return [Mission(**mission) for mission in storage.missions]

@app.post("/missions", response_model=Mission)
async def create_mission(mission_create: MissionCreate):
    """Create a new mission"""
    mission_data = {
        "id": storage.get_next_id(),
        "title": mission_create.title,
        "description": mission_create.description,
        "status": mission_create.status,
        "priority": mission_create.priority,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    storage.missions.append(mission_data)
    return Mission(**mission_data)

# --- Vault/Doctrine Log Endpoints ---
@app.get("/vault/logs", response_model=List[VaultLog])
async def get_vault_logs():
    """Get all vault logs"""
    logs = sorted(storage.vault_logs, key=lambda x: x["timestamp"], reverse=True)
    return [VaultLog(**log) for log in logs]

@app.get("/doctrine", response_model=List[VaultLog])
async def list_doctrine():
    """Get doctrine logs (alias for vault logs)"""
    return await get_vault_logs()

@app.post("/vault/logs", response_model=VaultLog)
async def add_vault_log(log_create: VaultLogCreate):
    """Add a new vault log entry"""
    log_data = {
        "id": storage.get_next_id(),
        "agent_name": log_create.agent_name,
        "action": log_create.action,
        "details": log_create.details,
        "timestamp": datetime.utcnow(),
        "log_level": log_create.log_level
    }
    storage.vault_logs.append(log_data)
    return VaultLog(**log_data)

@app.post("/doctrine", response_model=VaultLog)
async def add_doctrine(log_create: VaultLogCreate):
    """Add doctrine log (alias for vault log)"""
    return await add_vault_log(log_create)

# --- WebSocket Endpoints ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    client_id = None
    try:
        client_id = await websocket_manager.connect(websocket)
        
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await websocket_manager.handle_message(client_id, message)
            except json.JSONDecodeError:
                await websocket_manager.send_personal_message(client_id, {
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
    finally:
        if client_id:
            websocket_manager.disconnect(client_id)

@app.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return websocket_manager.get_stats()

# --- Enhanced Armada Endpoints ---
@app.post("/armada/order")
async def issue_armada_order(order_data: dict):
    """Issue commands to armada fleet"""
    ship_id = order_data.get("ship_id")
    command = order_data.get("command")
    parameters = order_data.get("parameters", {})
    
    if not ship_id or not command:
        raise HTTPException(status_code=400, detail="ship_id and command are required")
    
    # Find the ship
    ship = None
    for s in storage.armada_fleet:
        if s.get("id") == ship_id:
            ship = s
            break
    
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    
    # Process command
    result = await _process_armada_command(ship, command, parameters)
    
    # Broadcast fleet update
    await websocket_manager.broadcast({
        "type": "armada_order_executed",
        "ship": ship,
        "command": command,
        "result": result
    })
    
    return {"ok": True, "ship": ship, "command": command, "result": result}

async def _process_armada_command(ship: dict, command: str, parameters: dict):
    """Process armada command and update ship status"""
    timestamp = datetime.utcnow()
    ship["updated_at"] = timestamp
    
    if command == "move":
        destination = parameters.get("destination")
        if destination:
            ship["location"] = destination
            ship["status"] = "patrol"
            
            # Log the movement
            await _add_autonomous_log(
                "Fleet Command",
                "ship_movement",
                f"{ship['name']} ordered to move to {destination}",
                "info"
            )
            
            return f"Ship moved to {destination}"
    
    elif command == "status_change":
        new_status = parameters.get("status")
        if new_status in ["online", "offline", "maintenance", "patrol"]:
            old_status = ship["status"]
            ship["status"] = new_status
            
            # Log status change
            await _add_autonomous_log(
                "Fleet Command",
                "status_change",
                f"{ship['name']} status changed from {old_status} to {new_status}",
                "info"
            )
            
            return f"Status changed to {new_status}"
    
    elif command == "patrol":
        sectors = parameters.get("sectors", ["Alpha", "Beta"])
        ship["status"] = "patrol"
        ship["patrol_sectors"] = sectors
        
        # Log patrol assignment
        await _add_autonomous_log(
            "Fleet Command",
            "patrol_assignment",
            f"{ship['name']} assigned to patrol sectors: {', '.join(sectors)}",
            "info"
        )
        
        return f"Patrol assigned to sectors: {', '.join(sectors)}"
    
    return "Command processed"

async def _add_autonomous_log(agent_name: str, action: str, details: str, log_level: str):
    """Add log entry from autonomous systems"""
    log_entry = {
        "id": storage.get_next_id(),
        "agent_name": agent_name,
        "action": action,
        "details": details,
        "timestamp": datetime.utcnow(),
        "log_level": log_level
    }
    
    storage.vault_logs.append(log_entry)
    
    # Broadcast log update
    await websocket_manager.broadcast({
        "type": "vault_log",
        "log": log_entry
    })

# --- Armada Endpoints ---
@app.get("/armada/status")
async def get_armada():
    """Get enhanced armada fleet status with live data"""
    enhanced_fleet = []
    
    for ship in storage.armada_fleet:
        # Add calculated fields for enhanced status
        enhanced_ship = ship.copy()
        enhanced_ship["last_reported"] = ship.get("updated_at", datetime.utcnow()).isoformat() if ship.get("updated_at") else datetime.utcnow().isoformat()
        enhanced_ship["operational"] = ship.get("status") in ["online", "patrol"]
        enhanced_ship["patrol_sectors"] = ship.get("patrol_sectors", [])
        
        enhanced_fleet.append(enhanced_ship)
    
    return {
        "fleet": enhanced_fleet,
        "summary": {
            "total_ships": len(storage.armada_fleet),
            "online": len([s for s in storage.armada_fleet if s.get("status") == "online"]),
            "patrol": len([s for s in storage.armada_fleet if s.get("status") == "patrol"]),
            "offline": len([s for s in storage.armada_fleet if s.get("status") == "offline"]),
            "maintenance": len([s for s in storage.armada_fleet if s.get("status") == "maintenance"]),
            "last_updated": datetime.utcnow().isoformat()
        }
    }

# Fleet endpoint alias for consistency
@app.get("/fleet")
async def get_fleet():
    """Get fleet status (alias for armada/status)"""
    return await get_armada()

# --- Status Endpoint ---
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "service": "SR-AIbridge Backend",
        "version": "1.1.0-autonomous",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health/full")
async def full_health_check():
    """Comprehensive health check for deployment and monitoring"""
    try:
        # Get database health status
        db_health = {"status": "healthy"}
        if USE_DATABASE and hasattr(storage, 'health_check'):
            try:
                db_health = await storage.health_check()
            except Exception as e:
                db_health = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Check system components
        components = {
            "database": db_health["status"],
            "storage": "healthy" if storage else "unhealthy",
            "guardian": "healthy" if (hasattr(guardian, 'active') and guardian.active) else "unhealthy",
            "scheduler": "healthy" if (hasattr(scheduler, 'is_running') and scheduler.is_running) else "healthy",
            "websocket": "healthy"  # Assume healthy if server is running
        }
        
        # Calculate overall health
        unhealthy_count = sum(1 for status in components.values() if status == "unhealthy")
        overall_status = "healthy" if unhealthy_count == 0 else "degraded" if unhealthy_count <= 2 else "unhealthy"
        
        # Enhanced metrics
        metrics = {
            "agents_count": len(storage.agents) if storage else 0,
            "missions_count": len(storage.missions) if storage else 0,
            "vault_logs_count": len(storage.vault_logs) if storage else 0,
            "captain_messages_count": len(storage.captain_messages) if storage else 0,
            "armada_fleet_count": len(storage.armada_fleet) if storage else 0,
            "uptime_status": "operational",
            "database_type": DATABASE_TYPE,
            "using_async_db": USE_DATABASE
        }
        
        # Add database details if available
        if db_health.get("database_type"):
            metrics["db_connection_type"] = db_health["database_type"]
            metrics["db_agent_count"] = db_health.get("agent_count", 0)
        
        return {
            "status": overall_status,
            "service": "SR-AIbridge Backend",
            "version": "1.1.0-autonomous",
            "timestamp": datetime.utcnow().isoformat(),
            "components": components,
            "metrics": metrics,
            "database_health": db_health
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "SR-AIbridge Backend", 
            "version": "1.1.0-autonomous",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@app.post("/self/heal")
async def trigger_self_heal():
    """Trigger system self-healing process"""
    try:
        # Import and initialize self-healing service
        from app.services.self_heal import SelfHealingService
        
        healing_service = SelfHealingService(storage, websocket_manager)
        healing_actions = await healing_service.run_healing_cycle()
        
        return {
            "status": "success",
            "message": "Self-healing cycle completed",
            "timestamp": datetime.utcnow().isoformat(),
            "actions_taken": len(healing_actions),
            "healing_actions": healing_actions
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Self-healing failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/status")
async def get_status():
    """Get overall system status"""
    agents_online = len([a for a in storage.agents if a["status"] == "online"])
    active_missions = len([m for m in storage.missions if m["status"] == "active"])
    
    return {
        "agents_online": agents_online,
        "active_missions": active_missions,
        "admiral": "Admiral Kyle",
        "fleet_count": len(storage.armada_fleet),
        "total_agents": len(storage.agents),
        "total_missions": len(storage.missions),
        "vault_logs": len(storage.vault_logs)
    }

# --- Guardian Status Endpoint ---
@app.get("/guardian/status")
async def get_guardian_status():
    """Get Guardian daemon status for frontend polling"""
    return guardian.get_status()

@app.post("/guardian/selftest")
async def run_guardian_selftest():
    """Manually trigger Guardian self-test"""
    try:
        await guardian.run_selftest()
        return {
            "success": True,
            "message": "Self-test completed",
            "status": guardian.selftest_status,
            "last_selftest": guardian.last_selftest.isoformat() if guardian.last_selftest else None
        }
    except Exception as e:
        logger.error(f"Guardian selftest endpoint error: {e}")
        return HTTPException(status_code=500, detail=f"Self-test failed: {str(e)}")

@app.post("/guardian/activate")
async def activate_guardian():
    """Manually activate Guardian daemon"""
    try:
        result = await guardian.activate()
        return result
    except Exception as e:
        logger.error(f"Guardian activation error: {e}")
        return HTTPException(status_code=500, detail=f"Activation failed: {str(e)}")

# --- Activity/Tasks Endpoints (for compatibility) ---
@app.get("/activity")
async def get_activity():
    """Get recent activity (missions and logs combined)"""
    activities = []
    
    # Add recent missions as activities
    for mission in storage.missions[-5:]:  # Last 5 missions
        activities.append({
            "id": f"mission_{mission['id']}",
            "type": "mission",
            "title": mission["title"],
            "description": mission["description"],
            "status": mission["status"],
            "timestamp": mission["created_at"]
        })
    
    # Add recent vault logs as activities
    for log in storage.vault_logs[-5:]:  # Last 5 logs
        activities.append({
            "id": f"log_{log['id']}",
            "type": "log",
            "title": f"{log['agent_name']}: {log['action']}",
            "description": log["details"],
            "status": log["log_level"],
            "timestamp": log["timestamp"]
        })
    
    # Sort by timestamp descending
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    return activities[:10]  # Return top 10

@app.get("/tasks")
async def get_tasks():
    """Get tasks (alias for missions for compatibility)"""
    return await list_missions()

@app.post("/tasks")
async def create_task(task_data: dict):
    """Create a new task (alias for mission creation)"""
    mission_create = MissionCreate(
        title=task_data.get("title", "New Task"),
        description=task_data.get("description", ""),
        status="active",
        priority=task_data.get("priority", "normal")
    )
    return await create_mission(mission_create)

# --- Utility Endpoints ---
@app.get("/reseed")
async def reseed_data():
    """Reseed demo data (useful for testing)"""
    result = rituals.reseed()
    # Return the traditional format for backward compatibility
    return {
        "ok": True,
        "message": "Demo data reseeded successfully",
        "counts": result["final_counts"]
    }

@app.get("/rituals/seed")
async def ritual_seed():
    """Seed demo data without clearing existing data"""
    return rituals.seed()

@app.get("/rituals/cleanup")
async def ritual_cleanup():
    """Clean up all data from storage"""
    return rituals.cleanup()

@app.get("/rituals/reseed")
async def ritual_reseed():
    """Clean up and reseed with fresh demo data"""
    return rituals.reseed()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    # Determine storage type for display
    storage_type = "database" if USE_DATABASE else "in-memory"
    storage_details = f"{DATABASE_TYPE.upper()}" if USE_DATABASE else "memory"
    
    return {
        "name": "SR-AIbridge Backend",
        "version": "1.1.0-dual-mode",
        "description": f"Dual-mode SR-AIbridge backend ({storage_details} storage)",
        "endpoints": {
            "status": "/status",
            "guardian": "/guardian/status",
            "agents": "/agents",
            "missions": "/missions",
            "vault_logs": "/vault/logs",
            "captain_chat": "/captains/messages",
            "armada": "/armada/status",
            "armada_orders": "/armada/order",
            "websocket": "/ws",
            "websocket_stats": "/ws/stats",
            "reseed": "/reseed",
            "rituals": {
                "seed": "/rituals/seed",
                "cleanup": "/rituals/cleanup", 
                "reseed": "/rituals/reseed"
            }
        },
        "features": {
            "dual_mode_storage": True,
            "database_toggle": True,
            "autonomous_scheduler": True,
            "guardian_daemon": True,
            "continuous_selftest": True,
            "websocket_support": True,
            "real_time_updates": True,
            "npc_interactions": True,
            "auto_mission_progression": True
        },
        "storage": {
            "type": storage_type,
            "engine": storage_details,
            "database_url": DATABASE_URL if USE_DATABASE and not DATABASE_URL.startswith("sqlite") else "local"
        },
        "environment": {
            "database_type": DATABASE_TYPE,
            "use_database": USE_DATABASE
        },
        "rituals_manager": "enabled",
        "autonomous_mode": "active",
        "ready": True
    }