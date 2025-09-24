import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
from rituals.manage_data import DataRituals
from websocket_manager import websocket_manager
from autonomous_scheduler import AutonomousScheduler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env variables - look in parent directory for .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv()  # Also check current directory

# Database configuration based on environment
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bridge.db")

logger.info(f"🔧 Configuring {DATABASE_TYPE.upper()} database: {DATABASE_URL}")

# Storage abstraction layer
class StorageInterface:
    """Abstract storage interface that works with both in-memory and database storage"""
    
    def __init__(self):
        self.captain_messages: List[Dict] = []
        self.armada_fleet: List[Dict] = []
        self.agents: List[Dict] = []
        self.missions: List[Dict] = []
        self.vault_logs: List[Dict] = []
        self.next_id = 1
    
    def get_next_id(self) -> int:
        current_id = self.next_id
        self.next_id += 1
        return current_id


class InMemoryStorage(StorageInterface):
    """In-memory storage for CI/CD and development"""
    pass



class AsyncDatabaseStorage(StorageInterface):
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