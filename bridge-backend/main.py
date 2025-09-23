import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import (
    Table, Column, Integer, String, DateTime, MetaData
)
from databases import Database
from dotenv import load_dotenv
import uuid

# Load env variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bridge.db")  # fallback to sqlite
ADMIRAL_NAME = os.getenv("ADMIRAL_NAME", "Admiral")

# Database setup
metadata = MetaData()

captain_messages = Table(
    "captain_messages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("from_", String, nullable=False),
    Column("to", String, nullable=False),
    Column("message", String, nullable=False),
    Column("timestamp", DateTime, default=datetime.utcnow),
)

armada_fleet = Table(
    "armada_fleet",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("status", String, nullable=False),
    Column("location", String, nullable=False),
)

# Agent registry table
agents = Table(
    "agents",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("endpoint", String, nullable=False),
    Column("capabilities", String, nullable=True),  # JSON string
    Column("status", String, nullable=False, default="offline"),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("last_heartbeat", DateTime, nullable=True),
)

# Missions table
missions = Table(
    "missions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("description", String, nullable=True),
    Column("status", String, nullable=False, default="pending"),
    Column("assigned_agent_id", String, nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("completed_at", DateTime, nullable=True),
)

database = Database(DATABASE_URL)

# In-memory agent registry for guaranteed-to-run experience
class AgentRegistry:
    def __init__(self):
        self.agents = {}

    def register_agent(self, name, endpoint, capabilities):
        agent_id = str(uuid.uuid4())
        self.agents[agent_id] = {
            "id": agent_id,
            "name": name,
            "endpoint": endpoint,
            "capabilities": capabilities or [],
            "status": "offline",
            "created_at": datetime.utcnow().isoformat(),
            "last_heartbeat": None,
        }
        return self.agents[agent_id]

    def list_agents(self):
        return list(self.agents.values())

    def get_agent(self, agent_id):
        return self.agents.get(agent_id)

    def update_status(self, agent_id, status, heartbeat=True):
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = status
            if heartbeat:
                self.agents[agent_id]["last_heartbeat"] = datetime.utcnow().isoformat()
            return self.agents[agent_id]
        return None

    def remove_agent(self, agent_id):
        return self.agents.pop(agent_id, None)

# Global agent registry instance
agent_registry = AgentRegistry()

app = FastAPI(title="SR-AIbridge Backend")

# --- Models ---
class Message(BaseModel):
    from_: str
    to: str
    message: str
    timestamp: datetime = datetime.utcnow()

class AgentCreate(BaseModel):
    name: str
    endpoint: str
    capabilities: Optional[List[dict]] = None

class AgentResponse(BaseModel):
    id: str
    name: str
    endpoint: str
    capabilities: List[dict]
    status: str
    created_at: str
    last_heartbeat: Optional[str] = None

# --- Startup / Shutdown ---
@app.on_event("startup")
async def startup():
    await database.connect()
    # Create tables if they do not exist (for SQLite quickstart)
    if DATABASE_URL.startswith("sqlite"):
        import sqlalchemy
        engine = sqlalchemy.create_engine(DATABASE_URL)
        metadata.create_all(engine)
        # Pre-seed armada_fleet if empty
        with engine.connect() as conn:
            result = conn.execute(armada_fleet.select())
            if result.rowcount == 0:
                conn.execute(armada_fleet.insert(), [
                    {"name": "Flagship Sovereign", "status": "online", "location": "Sector Alpha"},
                    {"name": "Frigate Horizon", "status": "offline", "location": "Sector Beta"},
                    {"name": "Scout Whisper", "status": "online", "location": "Sector Delta"},
                ])

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# --- Captain-to-Captain Endpoints ---
@app.get("/captains/messages", response_model=List[Message])
async def list_messages():
    query = captain_messages.select().order_by(captain_messages.c.timestamp.desc())
    results = await database.fetch_all(query)
    # Convert SQLAlchemy row objects to Message objects
    return [Message(**{**dict(r), "from_": r["from_"]}) for r in results]

@app.post("/captains/send")
async def send_message(msg: Message):
    query = captain_messages.insert().values(
        from_=msg.from_, to=msg.to, message=msg.message, timestamp=msg.timestamp
    )
    await database.execute(query)
    return {"ok": True, "stored": msg.dict()}

# --- Armada Endpoints ---
@app.get("/armada/status")
async def get_armada():
    query = armada_fleet.select()
    results = await database.fetch_all(query)
    return [dict(r) for r in results]

# --- Status Endpoint ---
@app.get("/status")
async def get_status():
    online_agents = len([a for a in agent_registry.list_agents() if a["status"] == "online"])
    return {
        "agents_online": online_agents,
        "active_missions": 1,  # Static for now
        "admiral": ADMIRAL_NAME
    }

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "SR-AIbridge Backend is running"}

# --- Agent Registry Endpoints ---
@app.get("/agents", response_model=List[AgentResponse])
async def list_agents():
    """List all registered agents"""
    return agent_registry.list_agents()

@app.post("/agents/register", response_model=AgentResponse)
async def register_agent(agent: AgentCreate):
    """Register a new agent"""
    registered_agent = agent_registry.register_agent(
        name=agent.name,
        endpoint=agent.endpoint,
        capabilities=agent.capabilities or []
    )
    return registered_agent

@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get a specific agent by ID"""
    agent = agent_registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.delete("/agents/{agent_id}")
async def remove_agent(agent_id: str):
    """Remove an agent from the registry"""
    removed_agent = agent_registry.remove_agent(agent_id)
    if not removed_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent removed successfully", "agent": removed_agent}