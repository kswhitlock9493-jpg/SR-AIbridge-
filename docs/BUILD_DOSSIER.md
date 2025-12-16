# SR-AIbridge Build Dossier
## Step-by-Step Rebuild Guide from Scratch

> **Purpose**: This document provides a complete, step-by-step guide to rebuild SR-AIbridge from scratch. Follow these instructions exactly to recreate the entire system.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Python 3.12 or higher** (`python --version`)
- [ ] **Node.js 18 or higher** (`node --version`)
- [ ] **Git** (`git --version`)
- [ ] **Text Editor** (VS Code recommended)
- [ ] **Terminal/Command Line** access
- [ ] **Internet Connection** (for dependencies)
- [ ] **~2GB RAM** available
- [ ] **~500MB Disk Space** available

---

## 🎯 Phase 1: Environment Setup (5 minutes)

### Step 1.1: Create Project Directory

```bash
# Create and navigate to project directory
mkdir SR-AIbridge
cd SR-AIbridge

# Initialize git repository
git init
```

### Step 1.2: Create Directory Structure

```bash
# Create main directories
mkdir -p bridge_backend/bridge_core
mkdir -p bridge-frontend/src
mkdir -p docs
mkdir -p .github/workflows
mkdir -p tests
mkdir -p scripts
```

### Step 1.3: Create Environment Files

**Backend `.env`**:
```bash
cat > bridge_backend/.env << 'EOF'
# Database Configuration
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///bridge.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development

# Security
SECRET_KEY=dev-secret-key-change-in-production
CORS_ALLOW_ALL=false
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Features
ENABLE_ENGINES=true
ENABLE_PAYMENTS=false
ENABLE_WEBSOCKETS=true

# Logging
LOG_LEVEL=INFO
EOF
```

**Frontend `.env`**:
```bash
cat > bridge-frontend/.env << 'EOF'
VITE_API_BASE=http://localhost:8000
VITE_WS_BASE=ws://localhost:8000
VITE_ENABLE_DEBUG=false
EOF
```

---

## 🐍 Phase 2: Backend Foundation (15 minutes)

### Step 2.1: Install Python Dependencies

**Create `bridge_backend/requirements.txt`**:
```bash
cat > bridge_backend/requirements.txt << 'EOF'
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
sqlalchemy[asyncio]>=2.0.0
aiosqlite>=0.19.0
aiohttp>=3.9.0
sympy==1.13.1
numpy==1.26.4
pynacl>=1.5.0
python-dotenv>=1.0.0
python-multipart>=0.0.5
EOF
```

**Install dependencies**:
```bash
cd bridge_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### Step 2.2: Create Database Models

**Create `bridge_backend/models.py`**:
```python
from sqlalchemy import Column, Integer, String, Text, Float, TIMESTAMP, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Guardian(Base):
    __tablename__ = "guardians"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), default="active")
    last_heartbeat = Column(TIMESTAMP)
    capabilities = Column(JSON)
    health_score = Column(Float, default=1.0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    captain = Column(String(255))
    status = Column(String(50), default="offline")
    capabilities = Column(JSON)
    last_heartbeat = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Mission(Base):
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    priority = Column(String(50), default="medium")
    status = Column(String(50), default="pending")
    captain = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    assigned_agents = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    completed_at = Column(TIMESTAMP)

class VaultLog(Base):
    __tablename__ = "vault_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    source = Column(String(255))
    metadata = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
```

### Step 2.3: Create Database Connection

**Create `bridge_backend/db.py`**:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bridge.db")

engine = create_async_engine(
    DATABASE_URL,
    echo=True if os.getenv("ENVIRONMENT") == "development" else False,
    future=True
)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_database():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session_maker() as session:
        yield session
```

### Step 2.4: Create Pydantic Schemas

**Create `bridge_backend/schemas.py`**:
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Guardian Schemas
class GuardianBase(BaseModel):
    name: str
    status: Optional[str] = "active"
    capabilities: Optional[Dict[str, Any]] = None

class GuardianOut(GuardianBase):
    id: int
    health_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Agent Schemas
class AgentBase(BaseModel):
    name: str
    role: str
    captain: Optional[str] = None
    capabilities: Optional[List[str]] = None

class AgentCreate(AgentBase):
    pass

class AgentOut(AgentBase):
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Mission Schemas
class MissionBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    captain: str
    role: str

class MissionCreate(MissionBase):
    pass

class MissionOut(MissionBase):
    id: int
    status: str
    assigned_agents: Optional[List[int]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Health Response
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    components: Optional[Dict[str, str]] = None
    metrics: Optional[Dict[str, Any]] = None
```

### Step 2.5: Create Main Application

**Create `bridge_backend/main.py`**:
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
from datetime import datetime
from dotenv import load_dotenv

from db import get_session, init_database
from models import Guardian, Agent, Mission, VaultLog
from schemas import (
    AgentCreate, AgentOut, MissionCreate, MissionOut,
    GuardianOut, HealthResponse
)

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="SR-AIbridge",
    description="Sovereign Runtime AI Command & Control System",
    version="5.5.3"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup():
    await init_database()
    # Create default guardian
    async with get_session().__anext__() as session:
        result = await session.execute(select(Guardian))
        if not result.scalars().first():
            guardian = Guardian(
                name="Default Guardian",
                status="active",
                health_score=1.0,
                capabilities={"monitoring": True}
            )
            session.add(guardian)
            await session.commit()

# Health Endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/health/full", response_model=HealthResponse)
async def full_health(session: AsyncSession = Depends(get_session)):
    """Comprehensive health check"""
    # Count records
    agents_result = await session.execute(select(Agent))
    agents_count = len(agents_result.scalars().all())
    
    missions_result = await session.execute(select(Mission))
    missions_count = len(missions_result.scalars().all())
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        components={
            "database": "connected",
            "guardians": "active"
        },
        metrics={
            "agents_count": agents_count,
            "missions_count": missions_count,
            "health_score": 1.0
        }
    )

# Agent Endpoints
@app.get("/agents", response_model=List[AgentOut])
async def list_agents(session: AsyncSession = Depends(get_session)):
    """List all agents"""
    result = await session.execute(select(Agent))
    return result.scalars().all()

@app.post("/agents", response_model=AgentOut, status_code=201)
async def create_agent(
    agent: AgentCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create new agent"""
    db_agent = Agent(**agent.dict())
    session.add(db_agent)
    await session.commit()
    await session.refresh(db_agent)
    return db_agent

# Mission Endpoints
@app.get("/missions", response_model=List[MissionOut])
async def list_missions(session: AsyncSession = Depends(get_session)):
    """List all missions"""
    result = await session.execute(select(Mission))
    return result.scalars().all()

@app.post("/missions", response_model=MissionOut, status_code=201)
async def create_mission(
    mission: MissionCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create new mission"""
    db_mission = Mission(**mission.dict())
    session.add(db_mission)
    await session.commit()
    await session.refresh(db_mission)
    return db_mission

# Guardian Endpoints
@app.get("/guardians", response_model=List[GuardianOut])
async def list_guardians(session: AsyncSession = Depends(get_session)):
    """List all guardians"""
    result = await session.execute(select(Guardian))
    return result.scalars().all()

# Root endpoint
@app.get("/")
async def root():
    """API information"""
    return {
        "name": "SR-AIbridge",
        "version": "5.5.3",
        "status": "operational",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 2.6: Test Backend

```bash
# Start the backend
cd bridge_backend
python main.py

# In another terminal, test the API
curl http://localhost:8000/health
curl http://localhost:8000/health/full
curl http://localhost:8000/agents
```

---

## ⚛️ Phase 3: Frontend Foundation (15 minutes)

### Step 3.1: Initialize React Project

```bash
cd bridge-frontend
npm create vite@latest . -- --template react
npm install
```

### Step 3.2: Install Additional Dependencies

```bash
npm install react-router-dom
```

### Step 3.3: Create API Client

**Create `bridge-frontend/src/api/client.js`**:
```javascript
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function fetchAPI(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getHealth() {
  return fetchAPI('/health');
}

export async function getFullHealth() {
  return fetchAPI('/health/full');
}

export async function getAgents() {
  return fetchAPI('/agents');
}

export async function createAgent(agentData) {
  return fetchAPI('/agents', {
    method: 'POST',
    body: JSON.stringify(agentData),
  });
}

export async function getMissions() {
  return fetchAPI('/missions');
}

export async function createMission(missionData) {
  return fetchAPI('/missions', {
    method: 'POST',
    body: JSON.stringify(missionData),
  });
}
```

### Step 3.4: Create Main Dashboard Component

**Create `bridge-frontend/src/components/Dashboard.jsx`**:
```javascript
import React, { useState, useEffect } from 'react';
import { getFullHealth, getAgents, getMissions } from '../api/client';

function Dashboard() {
  const [health, setHealth] = useState(null);
  const [agents, setAgents] = useState([]);
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    try {
      const [healthData, agentsData, missionsData] = await Promise.all([
        getFullHealth(),
        getAgents(),
        getMissions(),
      ]);
      setHealth(healthData);
      setAgents(agentsData);
      setMissions(missionsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="dashboard">
      <h1>SR-AIbridge Command Deck</h1>
      
      <div className="health-panel">
        <h2>System Health</h2>
        <div className={`status status-${health?.status}`}>
          {health?.status || 'unknown'}
        </div>
        <div className="metrics">
          <div>Agents: {health?.metrics?.agents_count || 0}</div>
          <div>Missions: {health?.metrics?.missions_count || 0}</div>
          <div>Health Score: {(health?.metrics?.health_score * 100 || 0).toFixed(1)}%</div>
        </div>
      </div>

      <div className="agents-panel">
        <h2>Agents ({agents.length})</h2>
        <ul>
          {agents.map(agent => (
            <li key={agent.id}>
              <strong>{agent.name}</strong> - {agent.role} ({agent.status})
            </li>
          ))}
        </ul>
      </div>

      <div className="missions-panel">
        <h2>Missions ({missions.length})</h2>
        <ul>
          {missions.map(mission => (
            <li key={mission.id}>
              <strong>{mission.title}</strong> - {mission.status}
              <br />
              <small>Captain: {mission.captain}</small>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Dashboard;
```

### Step 3.5: Create App Component

**Create `bridge-frontend/src/App.jsx`**:
```javascript
import React from 'react';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 SR-AIbridge</h1>
        <p>Sovereign Runtime Command & Control</p>
      </header>
      <main>
        <Dashboard />
      </main>
    </div>
  );
}

export default App;
```

### Step 3.6: Add Basic Styling

**Create `bridge-frontend/src/App.css`**:
```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  background: #0a0a0a;
  color: #ffffff;
}

.App {
  min-height: 100vh;
}

.App-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  text-align: center;
}

.App-header h1 {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.dashboard {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.health-panel, .agents-panel, .missions-panel {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 1.5rem;
}

h2 {
  margin-bottom: 1rem;
  color: #667eea;
}

.status {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  text-align: center;
  font-weight: bold;
  text-transform: uppercase;
  margin-bottom: 1rem;
}

.status-healthy {
  background: #10b981;
  color: white;
}

.metrics {
  display: flex;
  justify-content: space-around;
  padding: 1rem 0;
}

ul {
  list-style: none;
}

li {
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: #2a2a2a;
  border-radius: 4px;
}

.loading {
  text-align: center;
  padding: 4rem;
  font-size: 1.5rem;
}
```

### Step 3.7: Test Frontend

```bash
# Start the frontend
cd bridge-frontend
npm run dev

# Open browser to http://localhost:5173
```

---

## 🔧 Phase 4: Add Core Features (30 minutes)

### Step 4.1: Add WebSocket Support (Backend)

**Update `bridge_backend/main.py`** to add WebSocket endpoint:
```python
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/stats")
async def websocket_stats(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send system stats every 5 seconds
            async with get_session().__anext__() as session:
                agents_result = await session.execute(select(Agent))
                agents_count = len(agents_result.scalars().all())
                
                missions_result = await session.execute(select(Mission))
                missions_count = len(missions_result.scalars().all())
                
                await websocket.send_json({
                    "timestamp": datetime.utcnow().isoformat(),
                    "agents": agents_count,
                    "missions": missions_count,
                    "status": "healthy"
                })
            
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
```

### Step 4.2: Add WebSocket Support (Frontend)

**Update `bridge-frontend/src/components/Dashboard.jsx`**:
```javascript
useEffect(() => {
  const wsUrl = import.meta.env.VITE_WS_BASE || 'ws://localhost:8000';
  const ws = new WebSocket(`${wsUrl}/ws/stats`);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('WebSocket update:', data);
    // Update UI with real-time data
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  return () => ws.close();
}, []);
```

### Step 4.3: Add Agent Creation Form

**Create `bridge-frontend/src/components/AgentForm.jsx`**:
```javascript
import React, { useState } from 'react';
import { createAgent } from '../api/client';

function AgentForm({ onAgentCreated }) {
  const [name, setName] = useState('');
  const [role, setRole] = useState('agent');

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await createAgent({ name, role, capabilities: [] });
      setName('');
      onAgentCreated();
    } catch (error) {
      alert('Failed to create agent: ' + error.message);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="agent-form">
      <h3>Create New Agent</h3>
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Agent name"
        required
      />
      <select value={role} onChange={(e) => setRole(e.target.value)}>
        <option value="agent">Agent</option>
        <option value="captain">Captain</option>
      </select>
      <button type="submit">Create Agent</button>
    </form>
  );
}

export default AgentForm;
```

---

## 🚀 Phase 5: Deployment Setup (20 minutes)

### Step 5.1: Create Netlify Configuration

**Create `bridge-frontend/netlify.toml`**:
```toml
[build]
  base = "bridge-frontend"
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
```

### Step 5.2: Create Render Configuration

**Create `infra/render.yaml`**:
```yaml
services:
  - type: web
    name: sr-aibridge-backend
    env: python
    buildCommand: "cd bridge_backend && pip install -r requirements.txt"
    startCommand: "cd bridge_backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: /health
    envVars:
      - key: DATABASE_TYPE
        value: sqlite
      - key: ENVIRONMENT
        value: production
      - key: ALLOWED_ORIGINS
        value: https://your-frontend.netlify.app
```

### Step 5.3: Create GitHub Actions Workflow

**Create `.github/workflows/bridge-deploy.yml`**:
```yaml
name: Deploy SR-AIbridge

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install and Build
        run: |
          cd bridge-frontend
          npm install
          npm run build
      
      - name: Deploy to Netlify
        uses: netlify/actions/cli@master
        with:
          args: deploy --prod --dir=bridge-frontend/dist
        env:
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
```

---

## ✅ Phase 6: Verification & Testing (10 minutes)

### Step 6.1: Backend Tests

```bash
# Test all endpoints
curl http://localhost:8000/health
curl http://localhost:8000/health/full
curl http://localhost:8000/agents
curl http://localhost:8000/missions

# Create test agent
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Agent", "role": "agent"}'

# Create test mission
curl -X POST http://localhost:8000/missions \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Mission", "captain": "Admiral", "role": "captain"}'
```

### Step 6.2: Frontend Tests

1. Open browser to `http://localhost:5173`
2. Verify dashboard loads
3. Check health status is green
4. Verify agents list
5. Verify missions list
6. Test agent creation form

### Step 6.3: System Integration Test

```bash
# Run both backend and frontend simultaneously
# Terminal 1:
cd bridge_backend && python main.py

# Terminal 2:
cd bridge-frontend && npm run dev

# Verify:
# - Frontend connects to backend
# - Health status displays
# - WebSocket updates work
# - Data flows correctly
```

---

## 📊 Verification Checklist

After completing all phases, verify:

- [ ] Backend starts without errors
- [ ] Database initializes successfully
- [ ] Frontend builds and runs
- [ ] API endpoints respond correctly
- [ ] Health checks pass
- [ ] Agents can be created
- [ ] Missions can be created
- [ ] WebSocket connection works
- [ ] Real-time updates function
- [ ] CORS is properly configured
- [ ] Environment variables are set
- [ ] All dependencies installed

---

## 🎓 Next Steps

You now have a working SR-AIbridge instance! To expand:

1. **Add More Engines**: Implement the 20 specialized engines
2. **Add Authentication**: Implement JWT or OAuth2
3. **Add More Features**: Blueprints, Autonomy, Forge Dominion
4. **Deploy to Production**: Use Netlify + Render
5. **Configure CI/CD**: Set up automated deployments
6. **Add Monitoring**: Implement health dashboards
7. **Scale Database**: Migrate to PostgreSQL

---

## 🚨 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (must be 3.12+)
- Verify dependencies: `pip install -r requirements.txt`
- Check database file permissions

### Frontend won't build
- Check Node version: `node --version` (must be 18+)
- Clear cache: `rm -rf node_modules && npm install`
- Check environment variables

### CORS errors
- Update `ALLOWED_ORIGINS` in backend `.env`
- Verify frontend URL matches allowed origin

### Database errors
- Delete and recreate: `rm bridge.db && python main.py`
- Check database URL in `.env`

---

## 📖 Reference

- **Main README**: Complete project overview
- **SYSTEM_BLUEPRINT**: Technical architecture
- **MASTER_ROADMAP**: Navigation guide
- **API Docs**: Visit `http://localhost:8000/docs`

---

**Build completed! You now have a working SR-AIbridge system.**

*From zero to sovereign in 60 minutes.*
