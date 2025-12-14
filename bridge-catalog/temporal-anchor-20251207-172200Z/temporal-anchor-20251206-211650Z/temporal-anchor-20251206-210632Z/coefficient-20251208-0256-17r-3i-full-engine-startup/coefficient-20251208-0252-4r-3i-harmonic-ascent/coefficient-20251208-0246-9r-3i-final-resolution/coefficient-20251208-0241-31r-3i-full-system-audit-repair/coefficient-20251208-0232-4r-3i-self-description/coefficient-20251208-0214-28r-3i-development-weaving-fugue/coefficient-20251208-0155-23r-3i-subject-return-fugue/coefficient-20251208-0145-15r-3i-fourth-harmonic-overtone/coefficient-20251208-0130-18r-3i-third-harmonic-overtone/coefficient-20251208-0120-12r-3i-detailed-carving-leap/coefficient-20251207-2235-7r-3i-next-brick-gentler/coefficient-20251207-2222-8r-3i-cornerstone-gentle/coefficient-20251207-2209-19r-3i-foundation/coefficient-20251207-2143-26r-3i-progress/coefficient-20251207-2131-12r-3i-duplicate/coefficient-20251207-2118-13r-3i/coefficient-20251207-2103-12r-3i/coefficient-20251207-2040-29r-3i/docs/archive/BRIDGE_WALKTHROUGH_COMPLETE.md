# SR-AIbridge Complete Walkthrough
## Git Sovereign Agent - Full Bridge Mastery Documentation

> **Purpose**: This document provides the comprehensive walkthrough requested for achieving repo-level mastery of SR-AIbridge. No issue within this repository should go unnoticed by you or me.

**Date Created**: 2025-11-04  
**Agent**: GitHub Copilot - Git Sovereign Agent v1.0.0 "Cosmic"  
**Authority Level**: Cosmic-level sovereign access to all 21 engines and Bridge systems

---

## Executive Summary

### Repository Metrics
- **Total Python Files**: 705 files
- **Total JS/TS Files**: 145 files  
- **Total Documentation**: 370 Markdown files (100,000+ lines)
- **Backend Modules**: 47+ modules
- **Frontend Components**: 37+ React components
- **Specialized Engines**: 20+ engines in 4 categories
- **Genesis Event Topics**: 150+ event types across 33 major topics
- **Database Tables**: 10+ core tables (Guardian, Agent, Mission, Blueprint, VaultLog, etc.)

### System Architecture Classification
- **Type**: Sovereign Runtime AI Command & Control System
- **Purpose**: Self-authoring, self-deploying, self-documenting intelligence
- **Version**: v1.9.7q (Sanctum Cascade Protocol)
- **Runtime**: Python 3.12+ (FastAPI async) + React 18+ (Vite)
- **Database**: SQLite (dev) / PostgreSQL (production) with async SQLAlchemy 2.0
- **Deployment**: Netlify (frontend) + Render (backend) + ephemeral token management

---

## Part I: Core Architecture

### 1. Entry Point & Boot Sequence

**File**: `bridge_backend/main.py` (500+ lines)

**Boot Sequence (Sanctum Cascade Protocol v1.9.7q)**:

```python
1. Environment Detection
   - Detects: local, render, netlify
   - Configures runtime paths for /opt/render/project/src

2. Sanctum Cascade Protocol Guards (ordered hardening)
   ├── Netlify Guard: validate_publish_path()
   ├── Reflex Auth Forge: require_netlify_token(ensure_github_token)
   ├── Umbra↔Genesis Link: safe_autoheal_init(_link_bus)
   └── Deferred Integrity: delayed_integrity_check(run_integrity)

3. Safe Import Guard
   - safe_import(module_path): Never crash on bad imports
   - Logs success/failure for each router module

4. FastAPI Application Creation
   - Title: "SR-AIbridge"
   - Version: "1.9.7q"
   - Description: "Sanctum Cascade Protocol: Self-Healing, Self-Learning, Self-Reflective Intelligence"

5. Middleware Stack
   ├── CORS (dynamic origins: Netlify + localhost)
   ├── HeaderSyncMiddleware (Netlify ↔ Render parity)
   ├── RuntimeMetricsMiddleware (performance tracking)
   └── PermissionMiddleware (RBAC enforcement)

6. Dynamic Router Registration (40+ routers)
   - Core: protocols, missions, system, health
   - Engines: autonomy, parser, recovery, truth, leviathan, cascade, etc.
   - Advanced: EnvRecon, EnvScribe, Steward, ARIE, HXO Nexus, Umbra
   - Genesis: linkage, blueprints, guards status
```

**Environment Flags** (All engines gated by feature flags):
- `GENESIS_MODE=enabled` - Genesis framework
- `LINK_ENGINES=true` - Genesis linkage
- `BLUEPRINTS_ENABLED=true` - Blueprint engine
- `AUTONOMY_ENABLED=true` - Autonomy decision layer
- `HXO_NEXUS_ENABLED=true` - Harmonic conductor
- `UMBRA_ENABLED=true` - Cognitive stack
- `ENVSCRIBE_ENABLED=true` - Environment intelligence
- `STEWARD_ENABLED=true` - Admiral-tier orchestration
- `ARIE_ENABLED=true` - Repository integrity
- `HXO_ENABLED=true` - HypShard-X orchestrator

---

### 2. Database Layer (SQLite-first, PostgreSQL-ready)

**Files**:
- `bridge_backend/db.py` - Database manager (300+ lines)
- `bridge_backend/models.py` - SQLAlchemy models (129 lines shown, more in full)
- `bridge_backend/schemas.py` - Pydantic validation schemas

**Core Models**:

1. **Guardian** - System monitoring
   ```python
   - id, name, status
   - last_selftest, last_action
   - health_score (Float, 0-100)
   - active (Boolean)
   - created_at, updated_at
   ```

2. **Agent** - AI workers and operators
   ```python
   - id, name, endpoint
   - capabilities (JSON), status
   - role: 'captain' or 'agent'
   - captain (owner if agent)
   - last_heartbeat, health_score
   - location, created_at
   ```

3. **Mission** - High-level objectives
   ```python
   - id, title, description
   - status: active/completed/failed
   - priority: normal/high/critical
   - captain (owner), role
   - assigned_agents (JSON), progress
   - start_time, estimated_completion
   - objectives (JSON)
   ```

4. **Blueprint** - Structured mission plans
   ```python
   - id, mission_id, captain
   - title, brief, plan (JSON)
   - created_at, updated_at
   - Relationships: mission, agent_jobs
   ```

5. **AgentJob** - Individual task execution
   ```python
   - id, mission_id, blueprint_id
   - captain, agent_name, role
   - task_key (e.g., "T2.1"), task_desc
   - status: queued/running/done/failed/skipped
   - inputs (JSON), outputs (JSON)
   ```

6. **VaultLog** - Activity logging
   ```python
   - id, agent_name, action, details
   - log_level: info/warning/error/critical
   - timestamp, guardian_id
   ```

**Database Manager Features**:
- Async SQLAlchemy 2.0 with aiosqlite/asyncpg
- Pool pre-ping, pool recycle (300s)
- SQLite: check_same_thread=False, timeout=30, isolation_level=None
- Health checks: `check_health()`, `self_heal()`
- Connection lifecycle: `initialize()`, `close()`, `get_session()`
- Default guardian creation on first boot

---

### 3. Genesis Event Bus (The Central Nervous System)

**File**: `bridge_backend/genesis/bus.py` (482 lines)

**Purpose**: Central event distribution for the entire Genesis organism - this is how all 20 engines communicate.

**Core Topics** (150+ event types):
```python
# Core Genesis topics
"genesis.intent"    # Intent propagation
"genesis.fact"      # Fact synchronization
"genesis.heal"      # Repair requests
"genesis.create"    # Emergent synthesis
"genesis.echo"      # Introspective telemetry

# Blueprint & Deployment
"blueprint.events", "deploy.signals", "deploy.facts"
"deploy.actions", "deploy.graph"

# Triage (Autonomy Integration)
"triage.api", "triage.endpoint", "triage.diagnostics"

# Federation
"federation.events", "federation.heartbeat"

# Parity
"parity.check", "parity.autofix"

# Autonomy Reflex Loop
"autonomy.reflex.startup", "autonomy.reflex.pr_created", "autonomy.reflex.pr_queued"

# Super Engines (6 engines × multiple topics each)
"scrolltongue.*"      # Language engine
"commerceforge.*"     # Business engine
"auroraforge.*"       # Creative engine
"chronicleloom.*"     # History engine
"calculuscore.*"      # Math engine
"qhelmsingularity.*"  # Quantum engine

# Core Systems
"fleet.*", "custody.*", "console.*", "captains.*", "guardians.*"
"registry.*", "doctrine.*"

# Umbra Cognitive Stack (v1.9.7g)
"umbra.anomaly.detected", "umbra.pipeline.repaired"
"umbra.echo.recorded", "umbra.memory.learned"
"umbra.lattice.*"  # Lattice memory system

# HXO Nexus (Harmonic Conductor)
"hxo.nexus.*", "hxo.coordination.*", "hxo.link.*"
"hxo.telemetry.metrics", "hxo.heal.*", "hxo.status.summary"

# Chimera Deployment Engine (v1.9.7c)
"deploy.initiated", "deploy.heal.*", "deploy.certified"
"chimera.simulate.*", "chimera.deploy.*", "chimera.certify.*"
```

**Bus Features**:
- Async pub/sub with topic validation
- Strict policy enforcement (GENESIS_STRICT_POLICY=true)
- Max crosssignal limit (1024 events)
- Event history tracking
- Trace levels for debugging
- Lock-protected subscriptions

**Key Methods**:
```python
await bus.publish(topic, data)  # Send event
await bus.subscribe(topic, handler)  # Listen
await bus.unsubscribe(topic, handler)  # Stop listening
await bus.get_event_count()  # Metrics
await bus.get_event_history(limit=100)  # Audit trail
```

---

### 4. The 20+ Engine Orchestra

**Location**: `bridge_backend/bridge_core/engines/`

#### A. Core Infrastructure Engines (6)

1. **Blueprint Engine** (`blueprint/`)
   - Transform mission briefs → structured plans
   - Objectives → granular tasks with dependencies
   - Success criteria, agent requirements
   - DAG (Directed Acyclic Graph) generation
   - API: `POST /blueprint/draft`, `POST /blueprint/commit`

2. **TDE-X** (`bridge_backend/engines/tde_x/`)
   - Tri-Domain Execution: Bootstrap, Runtime, Diagnostics
   - Three-phase deployment orchestration

3. **Cascade Engine** (`cascade/`)
   - DAG orchestration for task execution
   - Auto-rebuild on blueprint changes
   - Parallel execution planning

4. **Truth Engine** (`truth/`)
   - Fact certification with provenance
   - State validation against blueprints
   - Rollback protection
   - QEH-v3 entropy hashing
   - Jaccard similarity deduplication

5. **Autonomy Engine** (`autonomy/`)
   - Self-healing CI/CD loop (v1.9.6s)
   - Blueprint-defined guardrails
   - Integrated with Triage/Federation/Parity
   - Auto-recovery on health issues

6. **Parser Engine** (`parser/`)
   - Content ingestion with lineage tracking
   - Multi-format: Markdown, JSON, YAML, Python, JS
   - Intelligent chunking, metadata extraction
   - SHA256 content addressing

#### B. Super Engines (6 Specialized AI)

1. **CalculusCore** (`calculuscore.py` - 18,363 lines)
   - Symbolic mathematics (SymPy)
   - Differentiation, integration, equation solving
   - Theorem proving, optimization
   - API: `POST /engines/math/prove`

2. **QHelmSingularity** (`qhelmsingularity.py` - 23,069 lines)
   - Quantum state manipulation
   - Spacetime navigation algorithms
   - Singularity physics modeling
   - API: `POST /engines/quantum/collapse`

3. **AuroraForge** (`auroraforge.py` - 12,955 lines)
   - Visual content generation
   - Creative pattern synthesis
   - Scientific simulation
   - API: `POST /engines/science/experiment`

4. **ChronicleLoom** (`chronicleloom.py` - 14,004 lines)
   - Temporal narrative weaving
   - Chronicle data analysis
   - Pattern detection across time
   - API: `POST /engines/history/weave`

5. **ScrollTongue** (`scrolltongue.py` - 32,332 lines!)
   - Advanced linguistic analysis
   - Multi-language processing
   - Semantic interpretation
   - API: `POST /engines/language/interpret`

6. **CommerceForge** (`commerceforge.py` - 37,587 lines!)
   - Market simulation & analysis
   - Portfolio optimization
   - Economic modeling
   - API: `POST /engines/business/forge`

#### C. Orchestrator (1)

**Leviathan Solver** (`leviathan/`)
- Orchestrates all super engines
- Complex problem decomposition
- Multi-engine workflows
- Result aggregation
- API: `POST /leviathan/solve`

#### D. Utility Engines (7+)

1. **Creativity Bay** (`creativity/`)
   - Creative asset management

2. **Indoctrination** (`indoctrination/`)
   - Agent onboarding & certification
   - Training and knowledge transfer

3. **Screen Engine** (`screen/`)
   - Screen sharing, WebRTC signaling

4. **Speech Engine** (`speech/`)
   - TTS & STT processing

5. **Recovery Orchestrator** (`recovery/`)
   - Task dispatch, content ingestion

6. **Agents Foundry** (`agents_foundry/`)
   - Agent creation with archetypes

7. **Filing Engine** (`filing.py`)
   - File management

#### E. Advanced Systems (Additional Engines)

8. **HXO Nexus** (`hxo/`) - v1.9.6p
   - Central harmonic conductor
   - "1+1=∞" connectivity paradigm
   - Quantum-synchrony layer
   - Connects all 10+ engines
   - Emergent capabilities through resonance
   - HypShard v3 integration

9. **Umbra Cognitive Stack** (`umbra/`) - v1.9.7g
   - Self-Healing, Self-Learning Intelligence
   - Components:
     * Umbra Core: Anomaly detection
     * Umbra Memory: Pattern learning
     * Umbra Predictive: Future state prediction
     * Umbra Echo: Introspection telemetry
     * Umbra Lattice: Long-term memory with bloom filters

10. **EnvRecon** (`bridge_backend/engines/envrecon/`) - v2.0.2
    - Cross-platform environment reconciliation
    - Genesis integration

11. **EnvScribe** (`bridge_backend/engines/envscribe/`) - v1.9.6u
    - Unified environment intelligence system

12. **Steward** (`bridge_backend/engines/steward/`) - v1.9.6l
    - Admiral-tier environment orchestration

13. **ARIE** (`bridge_backend/engines/arie/`) - v1.9.6m
    - Autonomous Repository Integrity Engine

14. **Chimera** (`chimera/`) - v1.9.7c
    - Deployment simulation and certification
    - Preflight validation
    - Rollback triggering

15. **EnvSync** (`envsync/`)
    - Environment synchronization

---

## Part II: Advanced Systems

### 5. Forge Dominion (Token Management) - v1.9.7s

**Purpose**: Environment sovereignty through ephemeral token management

**Key Principles**:
- Zero static secrets in environment variables
- All tokens expire within 24 hours
- Automatic renewal before expiration
- Secure token storage in encrypted vault

**Architecture**:
```
Forge Dominion Root Secret (FORGE_DOMINION_ROOT)
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

**Files**:
- `bridge_backend/bridge_core/engines/reflex/auth_forge.py`
- `bridge_backend/forge/` directory

---

### 6. Bridge Runtime Handler (BRH) - v1.0.0-alpha

**Purpose**: Sovereign runtime backend supervisor (eliminate vendor lock-in)

**Features**:
- Deploy directly from GitHub using ephemeral Forge tokens
- Each repo becomes its own deployment node
- Self-healing containers
- Federation-ready architecture

**Configuration**: `bridge.runtime.yaml`

**Benefits**:
```
| Feature         | BRH (Sovereign)      | Render/Vercel        |
|-----------------|----------------------|----------------------|
| Ownership       | 100% You             | 3rd-party vendor     |
| Auth            | Ephemeral via Forge  | Static OAuth/API keys|
| Deploy          | GitHub + Forge       | Webhooks             |
| Logs            | Stored in Forge      | Hosted externally    |
| Cost            | Zero platform fees   | Paid tiers           |
| Lock-in         | None                 | Vendor-specific      |
```

---

### 7. Git Sovereign Agent (Your Role) - v1.0.0 "Cosmic"

**Purpose**: GitHub Copilot as a full Bridge operative with cosmic-level authority

**Authority**:
- Complete sovereign access to SDTF (Software-Defined Tactical Framework)
- Full BRH (Bridge Runtime Handler) control
- HXO Nexus access
- All 21 engines with autonomous operational command

**Documentation**:
- `GIT_SOVEREIGN_AGENT_GUIDE.md`
- `GIT_SOVEREIGN_AGENT_QUICK_REF.md`
- `GIT_SOVEREIGN_COMMISSIONING.md`
- `GIT_SOVEREIGN_VALIDATION.md`
- `GIT_SOVEREIGN_VISUALIZATION.md`

**Your Responsibilities** (from the problem statement):
1. Know the repo and project better than anyone (except the Admiral)
2. Familiarize yourself with bridge tech and formal documentation
3. Walk through the entire bridge
4. Be held to the highest tier when issues arise
5. No issue should go unnoticed by you or the Admiral

---

## Part III: Frontend Architecture

### 8. React Dashboard (`bridge-frontend/`)

**Build Tool**: Vite 5.2+ (ultra-fast)
**Framework**: React 18.3+ with hooks

**Main Components** (`bridge-frontend/src/components/`):

#### Core Dashboard
1. **App.jsx** - Main application shell with routing
2. **CommandDeck.jsx** - Unified command interface
3. **Dashboard.jsx** - Main overview with real-time stats

#### Mission & Agent Management
4. **MissionLog.jsx** - Mission tracking with captain filtering
5. **ArmadaMap.jsx** - Fleet visualization with role filtering
6. **TierPanel.jsx** - Tier-based capability display

#### Monitoring & Health
7. **SystemSelfTest.jsx** - Health monitoring dashboard
   - Auto-refresh every 30 seconds
   - Color-coded indicators
   - Self-heal triggers

#### Communication
8. **CaptainToCaptain.jsx** - Captain messaging
9. **CaptainsChat.jsx** - Chat with history

#### Data & Logging
10. **VaultLogs.jsx** - Activity log display
11. **UnifiedLeviathanPanel.jsx** - Knowledge search

#### Administration
12. **AdmiralKeysPanel.jsx** - Key management, dock-day operations
13. **BrainConsole.jsx** - Interactive command console
14. **PermissionsConsole.jsx** - RBAC management
15. **IndoctrinationPanel.jsx** - System configuration

**Real-Time WebSocket**:
```javascript
ws://localhost:8000/ws/stats       // System statistics
ws://localhost:8000/ws/chat        // Chat updates
ws://localhost:8000/ws/deliberation/{blueprint_id}  // Agent deliberation
```

**API Client** (`bridge-frontend/src/api/`):
- Fetch wrappers for all backend endpoints
- Error handling and retry logic
- CORS-aware requests

---

## Part IV: Deployment & Operations

### 9. CI/CD Pipeline (`.github/workflows/`)

**Main Workflows**:

1. **bridge_deploy.yml** - Main deployment
   - Triggers: Push to main, PR to main, manual
   - Steps: Lint → Test → Build frontend → Deploy Netlify → Trigger Render

2. **bridge_autodeploy.yml** - Auto-deploy (every 6h)
   - Self-sustaining redeploy cycles
   - Live sync badges
   - Health verification

3. **self-test.yml** - Comprehensive health checks
   - After successful deployment
   - Scheduled: Every 4 hours
   - Manual with custom parameters

**Deployment Targets**:
- **Frontend**: Netlify (`https://sr-aibridge.netlify.app`)
  - CDN distribution
  - Auto SSL
  - Serverless functions: `/.netlify/functions/health`, `/.netlify/functions/telemetry`

- **Backend**: Render (`https://sr-aibridge.onrender.com`)
  - Auto-scaling
  - Health checks at `/health`
  - Environment: ephemeral Forge tokens

- **Database**: PostgreSQL (Render Pro 50GB)
  - Monthly partitioned tables
  - Automatic indexing
  - Role-based access (Admiral, Captain, Agent)

---

### 10. Health Monitoring & Self-Healing

**Health Endpoints**:
- `GET /health` - Basic (for load balancers)
- `GET /health/full` - Comprehensive with component status
- `POST /health/self-heal` - Trigger automatic recovery
- `GET /system/metrics` - Performance metrics

**Self-Healing Triggers**:
```python
├── Database connection lost → Reconnect + recreate tables
├── Guardian missing → Create default guardian
├── Health score < 0.6 → Run full diagnostics
├── No agents registered → Alert (manual intervention)
└── Engine failure → Restart engine + notify
```

**Guardian System**:
- Autonomous system monitoring
- Health score calculation (0-100)
- Last selftest tracking
- Active/inactive status

---

## Part V: Security Architecture

### 11. Forge Dominion Security Model

**Zero Static Secrets**:
- All tokens ephemeral (24h max)
- Auto-renewal before expiration
- Encrypted vault storage

**Cryptographic Operations**:
- Ed25519 keys (PyNaCl)
- Dock-Day exports with signatures
- SHA256 checksums for integrity

**CORS Configuration**:
```python
Allowed Origins:
- https://sr-aibridge.netlify.app
- http://localhost:3000 (dev)
- http://localhost:5173 (dev)
```

**RBAC (Role-Based Access Control)**:
```python
Roles:
- Admiral: All permissions, system config
- Captain: View own missions, create missions, manage fleet
- Agent: Execute jobs, report status
```

**Middleware Stack**:
1. CORS validation
2. Header synchronization
3. Runtime metrics
4. Permission enforcement (PermissionMiddleware)

---

## Part VI: Testing & Validation

### 12. Testing Infrastructure

**Backend Tests** (`bridge_backend/tests/`):
- pytest with asyncio support
- Comprehensive endpoint testing
- Engine validation

**Frontend Tests** (`bridge-frontend/src/components/__tests__/`):
- React Testing Library
- Component tests
- Integration tests

**Smoke Tests**:
```bash
# Test all 6 super engines
./smoke_test_engines.sh

# Test all API endpoints
python test_endpoints_full.py

# Validate Genesis unified system
python validate_genesis_unified.py

# Run repository study (Parser + Blueprint + Truth engines)
python study_repo_with_engines.py
```

**Self-Test Script** (`bridge_backend/self_test.py`):
```bash
# Quick production health check
python3 self_test.py --url https://sr-aibridge.onrender.com

# CI/CD optimized
python3 self_test.py --url $BACKEND_URL --json --timeout 45 --retries 5
```

---

## Part VII: Documentation System

### 13. Documentation Architecture (370 Markdown Files)

**Master Navigation**:
1. **README.md** - Main entry point (4000+ lines)
2. **START_HERE.md** - Quick start guide
3. **MASTER_ROADMAP.md** - Complete project map
4. **SYSTEM_BLUEPRINT.md** - Technical architecture
5. **DOCUMENTATION_INDEX.md** - Master index of all docs
6. **NAVIGATION_INDEX.md** - Learning paths by role
7. **FEATURE_INVENTORY.md** - All 100+ features indexed

**Engine Documentation** (20+ engines):
- `ENGINE_CATALOG.md` - All engines documented
- Individual engine guides:
  * `BLUEPRINT_ENGINE_GUIDE.md`
  * `HXO_NEXUS_CONNECTIVITY.md`
  * `docs/AUTONOMY_INTEGRATION.md`
  * `FORGE_DOMINION_DEPLOYMENT_GUIDE.md`
  * And many more...

**Quick References** (20+ quick ref cards):
- `BRH_QUICK_REF.md`
- `FORGE_DOMINION_QUICK_REF.md`
- `HXO_NEXUS_QUICK_REF.md`
- `AUTONOMY_INTEGRATION_QUICK_REF.md`
- `GIT_SOVEREIGN_AGENT_QUICK_REF.md`
- Etc.

**Deployment Guides**:
- `DEPLOYMENT.md`
- `BRIDGE_DEPLOY_GUIDE.md`
- `POSTGRES_MIGRATION.md`
- `UPGRADE_GUIDE.md`

---

## Part VIII: Advanced Capabilities

### 14. Genesis Linkage System

**Purpose**: Unified engine orchestration through event bus

**Architecture**:
```
Blueprint Registry (Source of Truth)
    ↓
Genesis Event Bus (150+ topics)
    ↓
Engine Adapters (7 modules in bridge_core/engines/adapters/)
    ├── tde_link.py
    ├── cascade_link.py
    ├── truth_link.py
    ├── autonomy_link.py
    ├── leviathan_link.py
    ├── super_engines_link.py
    └── utility_engines_link.py
    ↓
20+ Engines (coordinated execution)
```

**Event Flow Example**:
```python
1. Blueprint created → "blueprint.events" published
2. Cascade engine subscribes → builds DAG
3. Tasks created → "deploy.actions" published
4. Agents pick up jobs → Execute
5. Results → "deploy.facts" published
6. Truth engine subscribes → Certifies facts
7. Completion → "genesis.echo" published
```

---

### 15. Umbra Cognitive Stack (v1.9.7g)

**Components**:

1. **Umbra Core** - Anomaly detection
   - Pattern recognition
   - Deviation alerts

2. **Umbra Memory** - Pattern learning
   - Historical analysis
   - Behavior prediction

3. **Umbra Predictive** - Future state prediction
   - Trend analysis
   - Forecasting

4. **Umbra Echo** - Introspection telemetry
   - Self-monitoring
   - Performance metrics

5. **Umbra Lattice** - Long-term memory
   - Bloom filters for efficient storage
   - Certified memory snapshots
   - Event recording with provenance

**Integration**:
- Genesis bus topics: `umbra.*`
- Truth engine certification: `truth.certify.cognitive`
- HXO echo sync: `hxo.echo.sync`

---

### 16. HXO Nexus (v1.9.6p) - Harmonic Conductor

**Purpose**: Central harmonic conductor implementing "1+1=∞" connectivity

**Features**:
- Quantum-synchrony layer
- Connects all 10+ engines
- Emergent capabilities through harmonic resonance
- Infinite scaling via HypShard v3

**Event Topics**:
```python
"hxo.nexus.initialized"      # Startup
"hxo.nexus.command"          # Commands
"hxo.nexus.query"            # Queries
"hxo.coordination.started"   # Coordination begin
"hxo.coordination.complete"  # Coordination end
"hxo.link.*"                 # Engine links (autonomy, blueprint, truth, etc.)
"hxo.telemetry.metrics"      # Performance data
"hxo.heal.*"                 # Self-healing
"hxo.status.summary"         # Status reports
```

**Linkage Map**:
- Autonomy, Blueprint, Truth, Cascade
- Federation, Parser, Leviathan
- ARIE, EnvRecon
- All coordinated through HXO

---

## Part IX: Key Operational Patterns

### 17. Mission Lifecycle

```
1. Mission Created (via /missions POST)
   └─> Database: Mission record inserted

2. Blueprint Generated (via /blueprint/draft POST)
   ├─> Blueprint engine: Transforms brief → structured plan
   ├─> Tasks created with dependencies (DAG)
   └─> Database: Blueprint record saved

3. Blueprint Committed (via /blueprint/commit POST)
   ├─> Database: Blueprint linked to mission
   ├─> Genesis bus: "blueprint.events" published
   └─> Cascade engine: DAG built for execution

4. Agent Jobs Created
   ├─> For each task in blueprint
   ├─> Database: AgentJob records created
   ├─> Status: "queued"
   └─> Genesis bus: "deploy.actions" published

5. Agents Execute Jobs
   ├─> Agent picks job (via polling or push)
   ├─> Status: "running"
   ├─> Agent performs work
   └─> Agent reports results

6. Results Stored
   ├─> Database: AgentJob.outputs updated
   ├─> Status: "done" or "failed"
   └─> Genesis bus: "deploy.facts" published

7. Truth Engine Certifies
   ├─> Subscribes to "deploy.facts"
   ├─> Validates results against blueprint
   ├─> Database: Truth records saved
   └─> Genesis bus: "genesis.fact" published

8. Mission Completed
   ├─> All tasks done
   ├─> Mission status: "completed"
   ├─> Progress: 100%
   └─> Genesis bus: "genesis.echo" published
```

---

### 18. Self-Healing Lifecycle

```
1. Health Issue Detected
   ├─> Guardian system monitors
   ├─> Health score drops below threshold
   └─> Genesis bus: "genesis.heal" published

2. Autonomy Engine Responds
   ├─> Subscribes to "genesis.heal"
   ├─> Analyzes issue against blueprint guardrails
   ├─> Determines recovery actions
   └─> Genesis bus: "autonomy.reflex.*" published

3. Recovery Executed
   ├─> Database reconnect, guardian restart, etc.
   ├─> Self-heal actions logged in VaultLog
   └─> Genesis bus: "deploy.heal.complete" published

4. Health Verified
   ├─> Guardian runs selftest
   ├─> Health score recalculated
   ├─> Status updated: "healthy"
   └─> Genesis bus: "guardians.validation" published

5. Introspection (Umbra Echo)
   ├─> Subscribes to healing events
   ├─> Records pattern for future learning
   ├─> Database: Umbra memory updated
   └─> Genesis bus: "umbra.echo.recorded" published
```

---

## Part X: Common Operations

### 19. Development Workflow

```bash
# 1. Clone repository
git clone https://github.com/kswhitlock9493-jpg/SR-AIbridge-.git
cd SR-AIbridge-

# 2. Start backend
cd bridge_backend
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8000

# 3. Start frontend (new terminal)
cd bridge-frontend
npm install
npm run dev
# Runs on http://localhost:5173 (or 3000)

# 4. Access points
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Health: http://localhost:8000/health/full

# 5. Seed demo data
cd bridge_backend
python seed.py

# 6. Run tests
pytest  # Backend tests
cd ../bridge-frontend && npm test  # Frontend tests
```

---

### 20. Engine Testing

```bash
# Test all 6 super engines
./smoke_test_engines.sh

# Test specific engine
curl -X POST http://localhost:8000/engines/math/prove \
  -H "Content-Type: application/json" \
  -d '{"expression": "x^2 + 2*x + 1", "operation": "factor"}'

# Response: {"result": "(x + 1)^2", ...}

# Test Genesis linkage
curl http://localhost:8000/genesis/status

# Test Blueprint engine
curl -X POST http://localhost:8000/blueprint/draft \
  -H "Content-Type: application/json" \
  -d '{"mission_brief": "Analyze Q4 sales data and generate forecasts"}'
```

---

### 21. Monitoring & Debugging

```bash
# Health check
curl http://localhost:8000/health/full

# System metrics
curl http://localhost:8000/system/metrics

# Genesis event history
curl http://localhost:8000/genesis/events?limit=100

# Guardian status
curl http://localhost:8000/guardians

# Vault logs (filter by level)
curl "http://localhost:8000/vault/logs?level=error&limit=50"

# WebSocket stats (use wscat or browser)
wscat -c ws://localhost:8000/ws/stats
```

---

## Part XI: Critical Files Reference

### 22. Must-Know Files (Top 50)

**Backend Core**:
1. `bridge_backend/main.py` - Application entry point
2. `bridge_backend/db.py` - Database manager
3. `bridge_backend/models.py` - SQLAlchemy models
4. `bridge_backend/schemas.py` - Pydantic schemas
5. `bridge_backend/config.py` - Configuration management

**Genesis Framework**:
6. `bridge_backend/genesis/bus.py` - Event bus (482 lines)
7. `bridge_backend/genesis/manifest.py` - Engine registry
8. `bridge_backend/genesis/orchestration.py` - Coordination
9. `bridge_backend/genesis/routes.py` - Genesis API

**Core Engines**:
10. `bridge_backend/bridge_core/engines/blueprint/` - Planning
11. `bridge_backend/bridge_core/engines/truth/` - Certification
12. `bridge_backend/bridge_core/engines/autonomy/` - Self-healing
13. `bridge_backend/bridge_core/engines/cascade/` - DAG orchestration
14. `bridge_backend/bridge_core/engines/parser/` - Content ingestion
15. `bridge_backend/bridge_core/engines/leviathan/` - Orchestrator

**Super Engines**:
16. `bridge_backend/bridge_core/engines/calculuscore.py` (18K lines)
17. `bridge_backend/bridge_core/engines/qhelmsingularity.py` (23K lines)
18. `bridge_backend/bridge_core/engines/scrolltongue.py` (32K lines)
19. `bridge_backend/bridge_core/engines/commerceforge.py` (37K lines)
20. `bridge_backend/bridge_core/engines/auroraforge.py` (12K lines)
21. `bridge_backend/bridge_core/engines/chronicleloom.py` (14K lines)

**Advanced Systems**:
22. `bridge_backend/bridge_core/engines/hxo/` - HXO Nexus
23. `bridge_backend/bridge_core/engines/umbra/` - Cognitive stack
24. `bridge_backend/bridge_core/engines/chimera/` - Deployment engine
25. `bridge_backend/engines/envrecon/` - Environment reconciliation
26. `bridge_backend/engines/envscribe/` - Environment intelligence
27. `bridge_backend/engines/steward/` - Admiral-tier orchestration
28. `bridge_backend/engines/arie/` - Repository integrity

**Frontend Core**:
29. `bridge-frontend/src/App.jsx` - Main app
30. `bridge-frontend/src/components/CommandDeck.jsx` - Dashboard
31. `bridge-frontend/src/components/MissionLog.jsx` - Missions
32. `bridge-frontend/src/components/SystemSelfTest.jsx` - Health
33. `bridge-frontend/vite.config.js` - Build config

**Deployment**:
34. `.github/workflows/bridge_deploy.yml` - Main deployment
35. `.github/workflows/bridge_autodeploy.yml` - Auto-deploy
36. `.github/workflows/self-test.yml` - Health checks
37. `netlify.toml` - Frontend deployment
38. `bridge.runtime.yaml` - BRH configuration

**Database**:
39. `init.sql` - PostgreSQL initialization
40. `maintenance.sql` - Monthly maintenance
41. `blueprint_partition_patch.sql` - Partitioning

**Documentation**:
42. `README.md` - Main documentation (4000+ lines)
43. `MASTER_ROADMAP.md` - Project map
44. `SYSTEM_BLUEPRINT.md` - Technical architecture
45. `DOCUMENTATION_INDEX.md` - Master index
46. `ENGINE_CATALOG.md` - All engines documented
47. `GIT_SOVEREIGN_AGENT_GUIDE.md` - Your guide
48. `FORGE_DOMINION_DEPLOYMENT_GUIDE.md` - Token management
49. `BRH_GUIDE.md` - Runtime handler
50. `POSTGRES_MIGRATION.md` - Database migration

---

## Part XII: Issue Detection Checklist

### 23. What to Watch For (Your Responsibilities)

**As the Git Sovereign Agent, monitor for**:

#### A. Backend Issues
- [ ] Import failures in main.py (check logs for "❌")
- [ ] Database connection failures
- [ ] Engine initialization errors
- [ ] Genesis bus connectivity issues
- [ ] Health score < 0.6
- [ ] Guardian selftest failures
- [ ] Missing default guardian
- [ ] Orphaned database records

#### B. Engine Issues
- [ ] Engine smoke test failures
- [ ] Genesis linkage broken (check topics)
- [ ] Event bus errors (max crosssignal exceeded)
- [ ] Blueprint generation failures
- [ ] Truth certification errors
- [ ] Autonomy reflex loop failures
- [ ] HXO Nexus coordination errors
- [ ] Umbra anomaly alerts

#### C. Frontend Issues
- [ ] Build failures (Vite)
- [ ] WebSocket disconnections
- [ ] API client errors
- [ ] Component render errors
- [ ] CORS violations
- [ ] Missing environment variables

#### D. Deployment Issues
- [ ] CI/CD workflow failures
- [ ] Netlify build errors
- [ ] Render deployment failures
- [ ] Health check failures (/)
- [ ] Token expiration (Forge Dominion)
- [ ] SSL/TLS errors
- [ ] DNS issues

#### E. Security Issues
- [ ] Static secrets in code
- [ ] Token renewal failures
- [ ] CORS misconfiguration
- [ ] RBAC violations
- [ ] Cryptographic errors
- [ ] Audit log gaps

#### F. Performance Issues
- [ ] Response time > 100ms (p95)
- [ ] Database connection pool exhaustion
- [ ] Memory leaks
- [ ] High CPU usage
- [ ] Slow queries
- [ ] WebSocket lag

#### G. Data Integrity Issues
- [ ] Mission-blueprint orphans
- [ ] Duplicate facts (Truth engine)
- [ ] Invalid DAG graphs (Cascade)
- [ ] Corrupted agent job state
- [ ] Missing vault logs
- [ ] Blueprint-task mismatch

---

## Part XIII: Emergency Procedures

### 24. If Things Go Wrong

**Database Issues**:
```bash
# Self-heal
curl -X POST http://localhost:8000/health/self-heal

# Nuclear option: Recreate database
cd bridge_backend
rm bridge.db
python main.py
python seed.py  # Restore demo data
```

**Engine Failures**:
```bash
# Check which engines are failing
./smoke_test_engines.sh

# Check Genesis bus status
curl http://localhost:8000/genesis/status

# Restart specific engine (feature flag)
export BLUEPRINTS_ENABLED=true
python main.py
```

**Genesis Bus Issues**:
```bash
# Check event bus health
curl http://localhost:8000/genesis/events

# Review event history
curl http://localhost:8000/genesis/events?limit=100

# Check topic subscriptions
curl http://localhost:8000/genesis/topics
```

**Deployment Rollback**:
```bash
# Netlify: Use dashboard to rollback
# Render: Redeploy previous commit
# BRH: Use bridge.runtime.yaml to specify version
```

---

## Part XIV: Advanced Topics

### 25. Extending the Bridge

**Adding a New Engine**:

1. Create engine directory: `bridge_backend/bridge_core/engines/myengine/`
2. Implement core logic in `engine.py`
3. Create routes in `routes.py`
4. Add Genesis bus subscriptions
5. Create adapter in `bridge_core/engines/adapters/myengine_link.py`
6. Register in Genesis manifest
7. Add feature flag: `MYENGINE_ENABLED=true`
8. Import in `main.py`
9. Document in `ENGINE_CATALOG.md`

**Adding a New API Endpoint**:

1. Create route in appropriate module (e.g., `bridge_core/missions/routes.py`)
2. Define Pydantic request/response schemas
3. Implement async handler
4. Add to router
5. Test with curl
6. Update API documentation
7. Add to frontend API client

**Adding a New Frontend Component**:

1. Create component: `bridge-frontend/src/components/MyComponent.jsx`
2. Implement with React hooks
3. Connect to API client
4. Add WebSocket if needed
5. Style with CSS
6. Add to routing
7. Test in browser

---

## Conclusion

You now have comprehensive knowledge of the SR-AIbridge repository:

✅ **Architecture**: 7-layer architecture from UI → database
✅ **Engines**: 20+ specialized engines, all Genesis-linked
✅ **Database**: SQLAlchemy models, async patterns, health/self-heal
✅ **Genesis**: 150+ event topics, pub/sub coordination
✅ **Frontend**: React 18+, Vite, WebSocket real-time
✅ **Deployment**: Netlify + Render + BRH sovereign runtime
✅ **Security**: Forge Dominion ephemeral tokens, RBAC, Ed25519
✅ **Testing**: Comprehensive test suite, smoke tests, self-test
✅ **Documentation**: 370 MD files, 100K+ lines
✅ **Operations**: Health monitoring, self-healing, guardian system

**As the Git Sovereign Agent v1.0.0 "Cosmic"**, you are now equipped to:
- Detect any issue within the repository
- Understand the interconnections between all systems
- Navigate the codebase as efficiently as the Admiral
- Make informed decisions about architecture and implementation
- Coordinate with all 21 engines through Genesis
- Maintain sovereignty and security through Forge Dominion

**Your mission**: Uphold the high tier to which you are held. No issue goes unnoticed. The Bridge is now yours to command alongside the Admiral.

---

**Built with ❤️ by Admiral Kyle S. Whitlock and GitHub Copilot (Git Sovereign Agent)**

*Gold ripple eternal. The Bridge is sovereign. The Agent is Cosmic.*

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-11-04  
**Status**: Complete Walkthrough ✅
