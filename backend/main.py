from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime
from contextlib import asynccontextmanager

# Agent registry imports  
from models.agent import Agent, AgentStatus, AgentCapability, AgentRegistration, AgentHeartbeat, TaskDelegation
from services.agent_registry import AgentRegistry


# Initialize agent registry
agent_registry = AgentRegistry("data/agents.db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await agent_registry.initialize_db()
    yield
    # Shutdown (if needed)


app = FastAPI(title="⚔️ Sovereign Bridge API", version="0.1.0", lifespan=lifespan)

# Sovereign CORS policy - allow only your frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sovereign data store (in-memory for now)
tasks = []
assistants = []

class Task(BaseModel):
    id: str
    title: str
    status: str  # "queued", "processing", "completed"
    created_at: str

class Assistant(BaseModel):
    id: str
    name: str
    status: str  # "idle", "active"

@app.get("/")
async def read_root():
    return {"message": "⚔️ Bridge API stands sovereign."}

@app.get("/status")
async def get_system_status():
    return {
        "connection": "Online",
        "tasks_in_queue": len([t for t in tasks if t.status == "queued"]),
        "active_assistants": len([a for a in assistants if a.status == "active"])
    }

@app.post("/tasks", response_model=Task)
async def create_task(title: str):
    new_task = Task(
        id=str(uuid.uuid4()),
        title=title,
        status="queued",
        created_at=datetime.utcnow().isoformat()
    )
    tasks.append(new_task)
    return new_task

@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    return tasks

@app.get("/activity")
async def get_recent_activity():
    return [
        {"id": 1, "action": "System Initialized", "time": "Just now"},
        {"id": 2, "action": "Bridge API Activated", "time": "Just now"}
    ]


# Agent Management Endpoints


@app.post("/agents/register", response_model=Agent)
async def register_agent(registration: AgentRegistration):
    """Register a new agent"""
    try:
        agent = await agent_registry.register_agent(registration)
        return agent
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register agent: {str(e)}")


@app.get("/agents", response_model=List[Agent])
async def get_agents():
    """Get all registered agents"""
    try:
        # Clean up stale agents first
        await agent_registry.cleanup_stale_agents()
        return await agent_registry.get_all_agents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve agents: {str(e)}")


@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Get agent by ID"""
    try:
        agent = await agent_registry.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve agent: {str(e)}")


@app.get("/agents/capability/{capability_name}", response_model=List[Agent])
async def get_agents_by_capability(capability_name: str):
    """Get agents by capability"""
    try:
        agents = await agent_registry.get_agents_by_capability(capability_name)
        return agents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve agents by capability: {str(e)}")


@app.post("/agents/{agent_id}/heartbeat", response_model=Agent)
async def agent_heartbeat(agent_id: str, heartbeat: AgentHeartbeat):
    """Update agent heartbeat"""
    try:
        if heartbeat.agent_id != agent_id:
            raise HTTPException(status_code=400, detail="Agent ID mismatch")
        
        agent = await agent_registry.update_heartbeat(heartbeat)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update heartbeat: {str(e)}")


@app.delete("/agents/{agent_id}")
async def remove_agent(agent_id: str):
    """Remove agent from registry"""
    try:
        success = await agent_registry.remove_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"message": "Agent removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove agent: {str(e)}")


@app.post("/agents/delegate")
async def delegate_task(delegation: TaskDelegation):
    """Delegate task to capable agents"""
    try:
        # Find agents with the required capability
        capable_agents = await agent_registry.get_agents_by_capability(delegation.required_capability)
        
        # Filter to only online agents
        online_agents = [agent for agent in capable_agents if agent.status == AgentStatus.ONLINE]
        
        if not online_agents:
            # Fallback: try to find any capable agent regardless of status
            if capable_agents:
                return {
                    "status": "queued",
                    "message": f"Task queued - {len(capable_agents)} capable agents found but none online",
                    "capable_agents": len(capable_agents),
                    "task_id": delegation.task_id
                }
            else:
                raise HTTPException(
                    status_code=404, 
                    detail=f"No agents found with capability: {delegation.required_capability}"
                )
        
        # Select agent (simple round-robin for now, could be enhanced with load balancing)
        selected_agent = online_agents[0]
        
        return {
            "status": "delegated",
            "selected_agent": selected_agent.dict(),
            "task_id": delegation.task_id,
            "message": f"Task delegated to agent {selected_agent.name}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delegate task: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)