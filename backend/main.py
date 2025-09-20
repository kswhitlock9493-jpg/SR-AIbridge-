from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

app = FastAPI(title="⚔️ Sovereign Bridge API", version="0.1.0")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)