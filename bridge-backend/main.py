import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
import json

# Load env variables
load_dotenv()

# In-memory storage
class InMemoryStorage:
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

# Global storage instance
storage = InMemoryStorage()

app = FastAPI(title="SR-AIbridge Backend")

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

# --- Seed Data Function ---
def seed_demo_data():
    """Populate in-memory storage with demo data"""
    # Clear existing data
    storage.captain_messages.clear()
    storage.armada_fleet.clear()
    storage.agents.clear()
    storage.missions.clear()
    storage.vault_logs.clear()
    storage.next_id = 1
    
    # Seed armada fleet
    fleet_data = [
        {"id": storage.get_next_id(), "name": "Flagship Sovereign", "status": "online", "location": "Sector Alpha"},
        {"id": storage.get_next_id(), "name": "Frigate Horizon", "status": "offline", "location": "Sector Beta"},
        {"id": storage.get_next_id(), "name": "Scout Whisper", "status": "online", "location": "Sector Delta"},
        {"id": storage.get_next_id(), "name": "SR-Vanguard", "status": "online", "location": "Outer Rim"},
        {"id": storage.get_next_id(), "name": "SR-Oracle", "status": "online", "location": "Deep Space Node"},
    ]
    storage.armada_fleet.extend(fleet_data)
    
    # Seed agents
    agents_data = [
        {
            "id": storage.get_next_id(),
            "name": "Agent Alpha",
            "endpoint": "http://agent-alpha:8001",
            "capabilities": [
                {"name": "reconnaissance", "version": "2.1", "description": "Advanced scouting operations"},
                {"name": "communication", "version": "1.5", "description": "Secure communications relay"}
            ],
            "status": "online",
            "last_heartbeat": datetime.utcnow(),
            "created_at": datetime.utcnow()
        },
        {
            "id": storage.get_next_id(),
            "name": "Agent Beta",
            "endpoint": "http://agent-beta:8002",
            "capabilities": [
                {"name": "analysis", "version": "3.0", "description": "Data analysis and pattern recognition"},
                {"name": "threat-detection", "version": "1.8", "description": "Security threat identification"}
            ],
            "status": "online",
            "last_heartbeat": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
    ]
    storage.agents.extend(agents_data)
    
    # Seed missions
    missions_data = [
        {
            "id": storage.get_next_id(),
            "title": "Deep Space Reconnaissance",
            "description": "Survey unknown sectors for potential threats and resources",
            "status": "active",
            "priority": "high",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": storage.get_next_id(),
            "title": "Communication Array Setup",
            "description": "Establish secure communication relays in outer rim",
            "status": "completed",
            "priority": "normal",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": storage.get_next_id(),
            "title": "Defensive Perimeter Analysis",
            "description": "Assess current defensive capabilities and recommend improvements",
            "status": "planning",
            "priority": "medium",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    storage.missions.extend(missions_data)
    
    # Seed vault logs
    vault_logs_data = [
        {
            "id": storage.get_next_id(),
            "agent_name": "Agent Alpha",
            "action": "mission_start",
            "details": "Initiated reconnaissance mission in Sector Gamma",
            "timestamp": datetime.utcnow(),
            "log_level": "info"
        },
        {
            "id": storage.get_next_id(),
            "agent_name": "Agent Beta",
            "action": "data_analysis",
            "details": "Completed threat assessment for outer rim sectors",
            "timestamp": datetime.utcnow(),
            "log_level": "info"
        },
        {
            "id": storage.get_next_id(),
            "agent_name": "System",
            "action": "alert",
            "details": "Unknown vessel detected at coordinates 127.45, 89.12",
            "timestamp": datetime.utcnow(),
            "log_level": "warning"
        }
    ]
    storage.vault_logs.extend(vault_logs_data)
    
    # Seed captain messages
    captain_messages_data = [
        {
            "id": storage.get_next_id(),
            "from_": "Admiral Kyle",
            "to": "Captain Torres",
            "message": "Status report on outer rim patrol?",
            "timestamp": datetime.utcnow()
        },
        {
            "id": storage.get_next_id(),
            "from_": "Captain Torres",
            "to": "Admiral Kyle",
            "message": "All clear in sectors 7-12. Proceeding to deep space checkpoint.",
            "timestamp": datetime.utcnow()
        }
    ]
    storage.captain_messages.extend(captain_messages_data)

# --- Startup / Shutdown ---
@app.on_event("startup")
async def startup():
    """Initialize in-memory storage with demo data"""
    seed_demo_data()
    print("✅ SR-AIbridge Backend started with in-memory storage")
    print(f"📊 Seeded: {len(storage.agents)} agents, {len(storage.missions)} missions, {len(storage.vault_logs)} vault logs, {len(storage.captain_messages)} messages")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    print("🔄 SR-AIbridge Backend shutting down...")

# --- Captain-to-Captain Endpoints ---
@app.get("/captains/messages", response_model=List[Message])
async def list_messages():
    """Get all captain messages, ordered by timestamp descending"""
    messages = sorted(storage.captain_messages, key=lambda x: x["timestamp"], reverse=True)
    return [Message(**msg) for msg in messages]

@app.post("/captains/send")
async def send_message(msg: Message):
    """Send a captain message"""
    message_data = {
        "id": storage.get_next_id(),
        "from_": msg.from_,
        "to": msg.to,
        "message": msg.message,
        "timestamp": msg.timestamp or datetime.utcnow()
    }
    storage.captain_messages.append(message_data)
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

# --- Armada Endpoints ---
@app.get("/armada/status")
async def get_armada():
    """Get armada fleet status"""
    return storage.armada_fleet

# --- Status Endpoint ---
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
    seed_demo_data()
    return {
        "ok": True,
        "message": "Demo data reseeded successfully",
        "counts": {
            "agents": len(storage.agents),
            "missions": len(storage.missions),
            "vault_logs": len(storage.vault_logs),
            "captain_messages": len(storage.captain_messages),
            "armada_fleet": len(storage.armada_fleet)
        }
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "SR-AIbridge Backend",
        "version": "1.0.0-inmemory",
        "description": "Drop-in in-memory backend for SR-AIbridge",
        "endpoints": {
            "status": "/status",
            "agents": "/agents",
            "missions": "/missions",
            "vault_logs": "/vault/logs",
            "captain_chat": "/captains/messages",
            "armada": "/armada/status",
            "reseed": "/reseed"
        },
        "storage": "in-memory",
        "ready": True
    }