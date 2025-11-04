# SR-AIbridge System Blueprint
## Technical Architecture & Implementation Details

> **Purpose**: This document provides deep technical details about how SR-AIbridge is built. This is your "engineering schematic."

---

## 🏛️ Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 7: USER INTERFACE                                         │
│ • React Components • WebSocket Clients • Dashboard UI           │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 6: API GATEWAY                                            │
│ • FastAPI Routing • CORS • Request Validation • Auth           │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 5: BUSINESS LOGIC                                         │
│ • Agent Management • Mission Control • Fleet Coordination       │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 4: ENGINE ORCHESTRA (Genesis Linkage)                     │
│ • 20 Specialized Engines • Event Bus • Orchestration           │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 3: CORE SERVICES                                          │
│ • Health Monitoring • Guardian System • Vault Logging           │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 2: DATA ACCESS                                            │
│ • SQLAlchemy ORM • Database Session Management • Models         │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: DATA STORAGE                                           │
│ • SQLite (dev) • PostgreSQL (prod) • File System               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Technology Stack Details

### Backend Stack

**Core Framework**:
```python
FastAPI 0.100+          # Modern async web framework
├── Starlette          # ASGI framework (FastAPI built on this)
├── Pydantic 2.0+      # Data validation using Python type hints
└── Uvicorn 0.23+      # Lightning-fast ASGI server
```

**Database Layer**:
```python
SQLAlchemy 2.0+        # Async ORM with type hints
├── aiosqlite 0.19+    # Async SQLite driver
├── asyncpg           # Async PostgreSQL driver (production)
└── alembic           # Database migrations (optional)
```

**Additional Libraries**:
```python
aiohttp 3.9+          # Async HTTP client for external calls
sympy 1.13+           # Symbolic mathematics (CalculusCore)
numpy 1.26+           # Numerical computing (engines)
pynacl 1.5+           # Cryptography (AdmiralKeys)
stripe 5.0+           # Payment processing (optional)
python-dotenv 1.0+    # Environment variables
python-multipart      # File upload support
```

### Frontend Stack

**Core Framework**:
```javascript
React 18.3+           # UI library with concurrent features
├── React DOM         # DOM rendering
├── React Router 7+   # Client-side routing
└── Hooks             # State management
```

**Build Tools**:
```javascript
Vite 5.2+             # Next-gen build tool
├── ESBuild          # Ultra-fast bundler
├── Rollup           # Module bundler
└── Terser           # JavaScript minifier
```

**Development**:
```javascript
ESLint               # Code linting
Testing Library      # React component testing
Vitest              # Unit testing
```

---

## 🗄️ Database Schema (Complete)

### Core Tables

#### Guardians Table
```sql
CREATE TABLE guardians (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(50) DEFAULT 'active',
    last_heartbeat TIMESTAMP,
    capabilities JSONB,
    health_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Purpose: System monitors that ensure health
-- Key Field: health_score (0.0-1.0)
```

#### Agents Table
```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,  -- 'captain' or 'agent'
    captain VARCHAR(255),        -- Owner for agents
    status VARCHAR(50) DEFAULT 'offline',
    capabilities JSONB,
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Purpose: AI workers and human operators
-- Key Field: role (determines permissions)
```

#### Missions Table
```sql
CREATE TABLE missions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority VARCHAR(50) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'pending',
    captain VARCHAR(255) NOT NULL,  -- Mission owner
    role VARCHAR(50) NOT NULL,       -- Access control
    assigned_agents JSONB,           -- List of agent IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Purpose: High-level objectives
-- Key Field: status (pending/active/completed/failed)
```

#### Blueprints Table
```sql
CREATE TABLE blueprints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER REFERENCES missions(id) ON DELETE CASCADE,
    mission_brief TEXT NOT NULL,
    plan JSONB NOT NULL,            -- Structured plan
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Purpose: Structured mission plans
-- Key Field: plan (JSON with objectives/tasks/artifacts)
```

#### Agent_Jobs Table (Partitioned Monthly)
```sql
CREATE TABLE agent_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    blueprint_id INTEGER REFERENCES blueprints(id) ON DELETE CASCADE,
    task_id VARCHAR(255) NOT NULL,
    task_title VARCHAR(500) NOT NULL,
    assigned_agent VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    dependencies JSONB,             -- Task dependencies
    deliberation_log JSONB,         -- Agent reasoning
    output_data JSONB,              -- Results
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Purpose: Individual agent task assignments
-- Partitioned: By month (agent_jobs_YYYY_MM)
```

#### Vault_Logs Table
```sql
CREATE TABLE vault_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level VARCHAR(50) NOT NULL,     -- info/warning/error/critical
    message TEXT NOT NULL,
    source VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Purpose: Activity logging and audit trail
-- Indexed: created_at DESC for fast queries
```

#### Admiral_Keys Table
```sql
CREATE TABLE admiral_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_name VARCHAR(255) NOT NULL UNIQUE,
    public_key TEXT NOT NULL,
    private_key_encrypted TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP
);

-- Purpose: Cryptographic key management
-- Security: Private keys encrypted at rest
```

### Indexes (Critical for Performance)
```sql
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_role ON agents(role);
CREATE INDEX idx_missions_captain ON missions(captain);
CREATE INDEX idx_missions_status ON missions(status);
CREATE INDEX idx_vault_logs_created ON vault_logs(created_at DESC);
CREATE INDEX idx_vault_logs_level ON vault_logs(level);
CREATE INDEX idx_agent_jobs_blueprint ON agent_jobs(blueprint_id);
CREATE INDEX idx_agent_jobs_status ON agent_jobs(status);
```

---

## 🎮 API Architecture

### REST API Structure

```
FastAPI Application
├── /                    # Root info
├── /health              # Basic health check
├── /health/full         # Comprehensive health
├── /system/metrics      # System metrics
│
├── /agents              # Agent management
│   ├── GET              # List agents
│   ├── POST             # Create agent
│   ├── DELETE /{id}     # Remove agent
│   └── POST /{id}/heartbeat  # Update heartbeat
│
├── /missions            # Mission control
│   ├── GET              # List missions
│   ├── POST             # Create mission
│   ├── PUT /{id}        # Update mission
│   ├── DELETE /{id}     # Delete mission
│   └── POST /{id}/assign    # Assign agents
│
├── /blueprint           # Blueprint engine
│   ├── POST /draft      # Generate plan
│   ├── POST /commit     # Save blueprint
│   ├── GET              # List blueprints
│   └── DELETE /{id}     # Delete blueprint
│
├── /engines             # Engine endpoints
│   ├── /math/prove      # CalculusCore
│   ├── /quantum/collapse # QHelmSingularity
│   ├── /science/experiment # AuroraForge
│   ├── /history/weave   # ChronicleLoom
│   ├── /language/interpret # ScrollTongue
│   ├── /business/forge  # CommerceForge
│   └── /linked/...      # Genesis linkage
│
├── /guardians           # Guardian system
│   ├── GET              # List guardians
│   ├── GET /status      # Guardian status
│   └── POST /selftest   # Run self-test
│
├── /vault               # Logging
│   ├── GET /logs        # Query logs
│   └── POST /logs       # Add log entry
│
├── /fleet               # Fleet management
│   ├── GET              # Fleet status
│   └── GET /armada/status # Armada status
│
└── /custody             # Admiral keys
    ├── GET /admiral-keys    # List keys
    ├── POST /admiral-keys   # Create key
    ├── POST /dock-day-drop  # Create export
    └── POST /verify-drop    # Verify export
```

### WebSocket Endpoints

```
ws://localhost:8000/ws/stats      # Real-time system statistics
ws://localhost:8000/ws/chat       # Real-time chat updates
ws://localhost:8000/ws/deliberation/{blueprint_id}  # Agent deliberation
```

### Request/Response Flow

```
Client Request
    ↓
CORS Middleware (check origin)
    ↓
Request Validation (Pydantic schema)
    ↓
Route Handler (async function)
    ↓
Database Session (async context manager)
    ↓
SQLAlchemy Query (async execute)
    ↓
Result Serialization (Pydantic model)
    ↓
Response with Headers
    ↓
Client Response
```

---

## ⚙️ Engine Architecture (20 Engines)

### Genesis Linkage System

```
Blueprint Registry (Source of Truth)
    ↓
Event Bus (33 Topics)
    ├── blueprint.events
    ├── deploy.signals
    ├── deploy.facts
    ├── deploy.graph
    ├── deploy.actions
    ├── solver.tasks
    ├── solver.results
    ├── math.calculus
    ├── quantum.navigation
    ├── creative.assets
    └── ... (24 more topics)
    ↓
Engine Adapters (7 Adapter Modules)
    ├── tde_link.py
    ├── cascade_link.py
    ├── truth_link.py
    ├── autonomy_link.py
    ├── leviathan_link.py
    ├── super_engines_link.py
    └── utility_engines_link.py
```

### Core Engines (Infrastructure - 6)

**1. Blueprint Engine**
```python
Location: bridge_backend/bridge_core/engines/blueprint/
Purpose: Transform mission briefs into structured plans
API: POST /blueprint/draft

Input: mission_brief (text)
Output: {
    "objectives": [...],
    "tasks": [{
        "id": "task-1",
        "title": "...",
        "dependencies": ["task-0"],
        "success_criteria": "...",
        "agent_requirements": [...]
    }],
    "artifacts": [...]
}
```

**2. TDE-X (Tri-Domain Execution)**
```python
Location: bridge_backend/bridge_core/engines/tde_x/
Purpose: Three-shard execution (bootstrap, runtime, diagnostics)
Shards:
  - Bootstrap: Initialization phase
  - Runtime: Active execution
  - Diagnostics: Health monitoring
```

**3. Cascade Engine**
```python
Location: bridge_backend/bridge_core/engines/cascade/
Purpose: DAG (Directed Acyclic Graph) orchestration
Features:
  - Auto-rebuild on blueprint changes
  - Task dependency resolution
  - Parallel execution planning
```

**4. Truth Engine**
```python
Location: bridge_backend/bridge_core/engines/truth/
Purpose: Fact certification and validation
Features:
  - State validation against blueprint
  - Deploy fact verification
  - Rollback protection
```

**5. Autonomy Engine**
```python
Location: bridge_backend/bridge_core/engines/autonomy/
Purpose: Self-healing and auto-recovery
Features:
  - Blueprint-defined guardrails
  - Automatic issue detection
  - Recovery action execution
Integration: Triage, Federation, Parity systems
```

**6. Parser Engine**
```python
Location: bridge_backend/bridge_core/engines/parser/
Purpose: Content ingestion with lineage tracking
Features:
  - Document parsing
  - Metadata extraction
  - Provenance tracking
```

### Super Engines (Specialized AI - 6)

**1. CalculusCore (Math Engine)**
```python
Location: bridge_backend/bridge_core/engines/calculus_core/
API: POST /engines/math/prove
Library: SymPy (symbolic mathematics)
Capabilities:
  - Differentiation
  - Integration
  - Equation solving
  - Theorem proving

Example Request:
{
    "expression": "diff(sin(x^2), x)",
    "operation": "differentiate"
}

Example Response:
{
    "result": "2*x*cos(x^2)",
    "steps": ["Applied chain rule", "Simplified"],
    "confidence": 1.0
}
```

**2. QHelmSingularity (Quantum Engine)**
```python
Location: bridge_backend/bridge_core/engines/qhelm/
API: POST /engines/quantum/collapse
Capabilities:
  - Quantum state manipulation
  - Spacetime navigation algorithms
  - Singularity physics modeling
  - Quantum entanglement simulation
```

**3. AuroraForge (Science/Creative Engine)**
```python
Location: bridge_backend/bridge_core/engines/aurora/
API: POST /engines/science/experiment
Capabilities:
  - Visual content generation
  - Creative pattern synthesis
  - Scientific simulation
  - Experimental design
```

**4. ChronicleLoom (History Engine)**
```python
Location: bridge_backend/bridge_core/engines/chronicle/
API: POST /engines/history/weave
Capabilities:
  - Temporal narrative weaving
  - Chronicle data analysis
  - Pattern detection across time
  - Historical context generation
```

**5. ScrollTongue (Language Engine)**
```python
Location: bridge_backend/bridge_core/engines/scroll/
API: POST /engines/language/interpret
Capabilities:
  - Advanced linguistic analysis
  - Multi-language processing
  - Semantic interpretation
  - Natural language understanding
```

**6. CommerceForge (Business Engine)**
```python
Location: bridge_backend/bridge_core/engines/commerce/
API: POST /engines/business/forge
Capabilities:
  - Market simulation and analysis
  - Portfolio optimization
  - Economic modeling
  - Business intelligence
```

### Orchestrator (Coordination - 1)

**Leviathan Solver**
```python
Location: bridge_backend/bridge_core/engines/leviathan/
Purpose: Orchestrate all super engines
Features:
  - Task delegation to super engines
  - Result aggregation
  - Complex problem decomposition
  - Multi-engine workflows

Workflow:
1. Receive complex task
2. Decompose into sub-tasks
3. Route to appropriate super engines
4. Aggregate results
5. Return unified solution
```

### Utility Engines (Support - 7)

1. **Creativity Bay**: Creative asset management
2. **Indoctrination**: Agent onboarding & certification
3. **Screen Engine**: Screen sharing, WebRTC signaling
4. **Speech Engine**: TTS & STT processing
5. **Recovery Orchestrator**: Task dispatch + content ingestion
6. **Agents Foundry**: Agent creation with archetypes
7. **Filing Engine**: File management

---

## 🔐 Security Architecture

### Token Management (Forge Dominion)

```
Forge Dominion System
    ↓
Ephemeral Token Generation
    ├── GitHub Tokens (auto-expiring)
    ├── Netlify Tokens (auto-expiring)
    ├── Render Tokens (auto-expiring)
    └── Database Tokens (auto-expiring)
    ↓
Token Renewal Service (automatic)
    ↓
Zero Static Secrets ✅
```

**Key Principles**:
1. No static secrets in environment variables
2. All tokens expire within 24 hours
3. Automatic renewal before expiration
4. Secure token storage in encrypted vault

### Cryptographic Operations

**Admiral Keys (Ed25519)**:
```python
from nacl.signing import SigningKey

# Key generation
signing_key = SigningKey.generate()
public_key = signing_key.verify_key
private_key = signing_key  # Encrypted at rest

# Signature creation
signature = signing_key.sign(data)

# Signature verification
verify_key.verify(signature)
```

**Dock-Day Exports**:
```python
{
    "manifest": {
        "export_id": "...",
        "timestamp": "...",
        "files": [...],
        "checksums": {...}
    },
    "signature": "...",  # Ed25519 signature
    "public_key": "..."   # For verification
}
```

### CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://sr-aibridge.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

---

## 🔄 Real-Time Architecture (WebSocket)

### WebSocket Connection Flow

```
Client (React)
    ↓
new WebSocket('ws://localhost:8000/ws/stats')
    ↓
FastAPI WebSocket Handler
    ↓
await websocket.accept()
    ↓
Connection Manager (tracks active connections)
    ↓
Periodic Updates (async task)
    ↓
await websocket.send_json(data)
    ↓
Client receives update
    ↓
UI re-renders
```

### Connection Manager Pattern

```python
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
async def stats_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await get_system_stats()
            await websocket.send_json(data)
            await asyncio.sleep(5)  # Update every 5 seconds
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
```

---

## 🏥 Health Monitoring System

### Health Check Levels

**Level 1: Basic (`/health`)**
```python
{
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

**Level 2: Full (`/health/full`)**
```python
{
    "status": "healthy",
    "components": {
        "database": "connected",
        "guardians": "active",
        "engines": "operational",
        "forge_dominion": "secure"
    },
    "metrics": {
        "agents_count": 12,
        "missions_active": 8,
        "health_score": 0.98,
        "response_time_ms": 45
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

**Level 3: Self-Heal (`POST /health/self-heal`)**
```python
{
    "status": "healing",
    "actions_taken": [
        "database_reconnect",
        "guardian_restart",
        "orphan_cleanup"
    ],
    "result": "healthy",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### Self-Healing Triggers

```python
Trigger Conditions:
├── Database connection lost → Reconnect + recreate tables
├── Guardian missing → Create default guardian
├── Health score < 0.6 → Run full diagnostics
├── No agents registered → Alert (manual intervention)
└── Engine failure → Restart engine + notify
```

---

## 📊 State Management

### Backend State (Database)
- **Persistent**: SQLite/PostgreSQL
- **Transactional**: ACID compliance
- **Async**: Non-blocking operations

### Frontend State (React)
```javascript
// Component-level state
const [agents, setAgents] = useState([]);

// Global state (shared)
const [systemHealth, setSystemHealth] = useState({});

// WebSocket state (real-time)
useEffect(() => {
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (event) => {
        setSystemHealth(JSON.parse(event.data));
    };
}, []);
```

### Caching Strategy
```python
# In-memory cache for static data
from functools import lru_cache

@lru_cache(maxsize=128)
def get_engine_manifest(engine_name: str):
    return blueprint_registry[engine_name]

# Cache invalidation on updates
get_engine_manifest.cache_clear()
```

---

## 🚀 Deployment Architecture

### Production Stack

```
┌─────────────────────────────────────────────────────────────┐
│ Netlify (Frontend)                                          │
│ • CDN Distribution                                          │
│ • Auto SSL                                                  │
│ • Serverless Functions (health, telemetry)                 │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS + WebSocket
┌────────────────────────▼────────────────────────────────────┐
│ Render (Backend)                                            │
│ • Auto-scaling                                              │
│ • Health checks                                             │
│ • Environment variables (ephemeral)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│ PostgreSQL (Database)                                       │
│ • Managed service                                           │
│ • Auto-backups                                              │
│ • Connection pooling                                        │
└─────────────────────────────────────────────────────────────┘
```

### CI/CD Pipeline

```
Git Push to main
    ↓
GitHub Actions Trigger
    ↓
.github/workflows/bridge-deploy.yml
    ├── Lint & Test
    ├── Build Frontend (Vite)
    ├── Deploy to Netlify
    ├── Trigger Render Deploy
    └── Health Check Verification
    ↓
Auto-Deploy Every 6h (.github/workflows/bridge_autodeploy.yml)
    ├── Health Check Backend
    ├── Build Frontend
    ├── Deploy to Netlify
    └── Generate Sync Badge
```

---

## 📈 Performance Characteristics

### Backend Performance
- **Cold Start**: ~5 seconds
- **Request Latency**: <50ms (p95)
- **Throughput**: 5000+ req/s (with PostgreSQL)
- **Memory**: ~100MB baseline
- **Database Connections**: Pool of 20-40

### Frontend Performance
- **Initial Load**: ~1.5 seconds
- **Bundle Size**: ~500KB (gzipped)
- **Time to Interactive**: <2 seconds
- **WebSocket Latency**: <100ms

### Optimization Techniques
1. Database connection pooling
2. Query result caching
3. Async operations throughout
4. Frontend code splitting
5. CDN for static assets

---

## 🧪 Testing Architecture

### Backend Tests
```python
pytest bridge_backend/tests/
├── test_agents.py       # Agent management
├── test_missions.py     # Mission control
├── test_engines.py      # Engine functionality
├── test_health.py       # Health monitoring
└── test_api.py          # API endpoints
```

### Frontend Tests
```javascript
npm test
├── components/*.test.jsx  # Component tests
├── api/*.test.js          # API client tests
└── integration/*.test.js  # Integration tests
```

### Smoke Tests
```bash
./smoke_test_engines.sh     # Test all 6 super engines
python test_endpoints_full.py  # Test all API endpoints
```

---

**This blueprint provides the technical foundation for understanding and rebuilding SR-AIbridge.**

*Architecture crafted for resilience, scalability, and sovereignty.*
