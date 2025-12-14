# SR-AIbridge Master Roadmap
## Complete Project Overview & Navigation Guide

> **Purpose**: This document provides a complete overview of the SR-AIbridge project for someone with zero prior knowledge. Think of this as your "map to the territory."

---

## 🎯 What Is SR-AIbridge?

**SR-AIbridge** is a **Sovereign Runtime AI Command & Control System** - essentially a complete platform for:

1. **Managing AI Agents** - Register, coordinate, and monitor AI agents in real-time
2. **Mission Control** - Create, assign, and track complex missions
3. **Autonomous Operations** - Self-healing, self-deploying, self-documenting system
4. **Engine Orchestra** - 20 specialized AI engines for everything from math to quantum physics
5. **Federation Ready** - Distributed coordination across multiple nodes

**Think of it as**: Mission Control for AI agents + NASA's self-healing systems + A fleet of specialized AI engines all working together.

---

## 🏗️ System Architecture (10,000 Foot View)

```
┌─────────────────────────────────────────────────────────────────┐
│                     USERS / OPERATORS                            │
│              (Captains, Agents, Admins)                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                  FRONTEND (React Dashboard)                      │
│  • Mission Control • Agent Management • Health Monitoring        │
│  • Real-time WebSocket Updates • Command Console                │
└────────────────────────┬────────────────────────────────────────┘
                         │ (REST API + WebSocket)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI Python)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Core Systems                                            │   │
│  │  • Agents • Missions • Fleet • Vault Logging            │   │
│  │  • Health Monitoring • Guardian System                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  20 Specialized Engines (Genesis Linkage)               │   │
│  │  • 6 Core • 6 Super Engines • 7 Utility • 1 Orchestrator│   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Advanced Systems                                        │   │
│  │  • Forge Dominion (Token Management)                    │   │
│  │  • HXO Nexus (Harmonic Conductor)                       │   │
│  │  • BRH (Runtime Handler) • Autonomy Engine              │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │ (SQLAlchemy ORM)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                  DATABASE (SQLite/PostgreSQL)                    │
│  • Agents • Missions • Guardians • Vault Logs • Keys            │
│  • Blueprints • Agent Jobs • Federation State                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure (What Goes Where)

```
SR-AIbridge-/
│
├── 📄 README.md                    # Main project documentation (START HERE)
├── 📄 MASTER_ROADMAP.md           # This file - complete project map
├── 📄 SYSTEM_BLUEPRINT.md         # Technical architecture (reference)
├── 📄 BUILD_DOSSIER.md            # Step-by-step rebuild guide
├── 📄 QUICK_START_30MIN.md        # Fast track setup
│
├── 🔧 Configuration Files
│   ├── .env.example               # Environment variables template
│   ├── requirements.txt           # Python dependencies (root)
│   ├── netlify.toml              # Frontend deployment config
│   ├── bridge.runtime.yaml       # BRH runtime configuration
│   └── pytest.ini                # Testing configuration
│
├── 🐍 bridge_backend/            # Python FastAPI backend
│   ├── main.py                   # Main application entry point
│   ├── config.py                 # Configuration management
│   ├── db.py                     # Database connection/session
│   ├── models.py                 # SQLAlchemy database models
│   ├── schemas.py                # Pydantic validation schemas
│   ├── requirements.txt          # Backend dependencies
│   │
│   └── bridge_core/              # Core backend functionality
│       ├── agents/               # Agent management
│       ├── missions/             # Mission control
│       ├── fleet/                # Fleet coordination
│       ├── vault/                # Logging system
│       ├── health/               # Health monitoring
│       ├── guardians/            # Guardian system
│       ├── engines/              # 20 specialized engines
│       │   ├── blueprint/        # Blueprint engine (planning)
│       │   ├── leviathan/        # Orchestrator
│       │   ├── autonomy/         # Self-healing
│       │   ├── tde_x/            # Tri-domain execution
│       │   ├── cascade/          # DAG orchestration
│       │   └── ... (15 more)
│       ├── token_forge_dominion/ # Token management
│       └── runtime_handler.py    # BRH implementation
│
├── ⚛️ bridge-frontend/           # React frontend dashboard
│   ├── src/
│   │   ├── App.jsx              # Main application
│   │   ├── components/          # React components
│   │   │   ├── CommandDeck.jsx  # Main dashboard
│   │   │   ├── MissionLog.jsx   # Mission tracking
│   │   │   ├── ArmadaMap.jsx    # Fleet visualization
│   │   │   ├── SystemSelfTest.jsx # Health monitoring
│   │   │   └── ... (30+ more)
│   │   └── api/                 # API client functions
│   ├── package.json             # Node.js dependencies
│   ├── vite.config.js           # Build configuration
│   └── netlify.toml             # Deployment config
│
├── 📚 docs/                      # Additional documentation
│   ├── AUTONOMY_INTEGRATION.md  # Autonomy system guide
│   ├── HXO_ENGINE_MATRIX.md     # HXO Nexus details
│   ├── GITHUB_FORGE.md          # Forge Dominion guide
│   └── ... (40+ guides)
│
├── 🗄️ Database Files
│   ├── init.sql                 # PostgreSQL initialization
│   ├── maintenance.sql          # Monthly maintenance
│   └── blueprint_partition_patch.sql # Partitioning
│
├── 🔬 Testing & Validation
│   ├── tests/                   # Test suites
│   ├── test_endpoints_full.py   # Full endpoint testing
│   ├── smoke_test_engines.sh    # Engine validation
│   └── validate_genesis_unified.py # Genesis validation
│
├── 🚀 Deployment & CI/CD
│   ├── .github/workflows/       # GitHub Actions
│   │   ├── bridge_autodeploy.yml # Auto-deploy (every 6h)
│   │   ├── bridge-deploy.yml    # Main deployment
│   │   └── self-test.yml        # Health checks
│   └── infra/render.yaml        # Render.com config
│
├── 🧬 Advanced Systems
│   ├── brh/                     # Bridge Runtime Handler
│   ├── DOCTRINE/                # Agent archetypes & policies
│   ├── codex/                   # Knowledge management
│   └── scripts/                 # Utility scripts
│
└── 📖 Documentation (100+ files)
    ├── *_GUIDE.md               # Comprehensive guides
    ├── *_QUICK_REF.md           # Quick references
    ├── *_IMPLEMENTATION.md      # Implementation docs
    └── CHANGELOG.md             # Version history
```

---

## 🎓 Core Concepts You Need to Know

### 1. **Agents vs Captains vs Guardians**

- **Agents**: AI workers that execute tasks
- **Captains**: Human operators who manage agents and missions
- **Guardians**: Autonomous system monitors that ensure health

### 2. **Missions vs Jobs vs Tasks**

- **Mission**: High-level objective (e.g., "Analyze Q4 data")
- **Blueprint**: Structured plan derived from mission brief
- **Task**: Individual step in a blueprint
- **Agent Job**: Specific task assigned to an agent

### 3. **Engines (20 Total)**

The system has 20 specialized engines organized into 4 categories:

**Core Engines (6)**: System infrastructure
- Blueprint, TDE-X, Cascade, Truth, Autonomy, Parser

**Super Engines (6)**: Specialized AI capabilities
- CalculusCore (math), QHelmSingularity (quantum), AuroraForge (creative)
- ChronicleLoom (history), ScrollTongue (language), CommerceForge (business)

**Utility Engines (7)**: Support services
- Creativity, Indoctrination, Screen, Speech, Recovery, AgentsFoundry, Filing

**Orchestrator (1)**: Coordination
- Leviathan Solver (coordinates all super engines)

### 4. **Genesis Linkage**

Genesis Linkage is the "nervous system" that connects all 20 engines:
- Event bus with 33 topics
- Dependency graph tracking
- Unified coordination
- Think of it as: "The system that makes all engines work together"

### 5. **Forge Dominion**

Token management system that eliminates static secrets:
- Ephemeral tokens (auto-expiring)
- Zero static credentials
- Environment sovereignty
- Think of it as: "The security system that manages all credentials"

### 6. **HXO Nexus**

Central harmonic conductor implementing "1+1=∞" connectivity:
- Quantum-synchrony layer
- Connects all 10+ engines
- Emergent capabilities through resonance
- Think of it as: "The conductor of an orchestra where instruments create new sounds together"

### 7. **BRH (Bridge Runtime Handler)**

Sovereign runtime supervisor:
- Vendor-free deployment
- Self-healing containers
- Federation-ready
- Think of it as: "Your own private cloud infrastructure"

---

## 🗺️ Navigation Guide: Where to Look for What

### "I Want to Understand..."

**...the whole system**
→ Start with `README.md`, then this file (`MASTER_ROADMAP.md`)

**...how to set it up quickly**
→ `QUICK_START_30MIN.md`

**...technical architecture details**
→ `SYSTEM_BLUEPRINT.md`

**...how to rebuild from scratch**
→ `BUILD_DOSSIER.md`

**...deployment**
→ `DEPLOYMENT.md`, `BRIDGE_DEPLOY_GUIDE.md`

**...the 20 engines**
→ `ENGINE_CATALOG.md`, `GENESIS_ARCHITECTURE.md`

**...the frontend**
→ `bridge-frontend/README.md`, component files in `bridge-frontend/src/components/`

**...the backend API**
→ Visit `http://localhost:8000/docs` (interactive API docs)

**...database structure**
→ `init.sql`, `models.py`, `POSTGRES_MIGRATION.md`

**...security**
→ `SECURITY.md`, `FORGE_DOMINION_DEPLOYMENT_GUIDE.md`

**...CI/CD & automation**
→ `.github/workflows/`, `AUTONOMY_DEPLOYMENT_README.md`

**...specific features**
→ Use the feature-specific guides (e.g., `BRH_GUIDE.md`, `HXO_NEXUS_QUICK_REF.md`)

---

## 🚀 Development Workflow (The Journey)

### Phase 1: Setup (15 minutes)
1. Clone repository
2. Install dependencies (Python + Node.js)
3. Configure environment variables
4. Initialize database

### Phase 2: Run Locally (5 minutes)
1. Start backend (`python main.py`)
2. Start frontend (`npm start`)
3. Verify health endpoints
4. Load demo data

### Phase 3: Explore (30 minutes)
1. Use interactive API docs (`/docs`)
2. Explore frontend dashboard
3. Create test agents and missions
4. Monitor health dashboard

### Phase 4: Deploy (30 minutes)
1. Configure Netlify (frontend)
2. Configure Render (backend)
3. Set environment variables
4. Push to trigger auto-deploy
5. Verify production health

### Phase 5: Customize (ongoing)
1. Add custom engines
2. Create mission blueprints
3. Configure autonomy rules
4. Integrate with external systems

---

## 📊 Key Metrics & Stats

**Project Scale**:
- **Lines of Code**: ~50,000+ (backend) + ~15,000+ (frontend)
- **Total Files**: 500+ files
- **Documentation Files**: 100+ markdown guides
- **API Endpoints**: 150+ endpoints
- **React Components**: 40+ components
- **Database Tables**: 20+ tables
- **Engines**: 20 specialized engines
- **Event Topics**: 33 inter-engine communication channels

**Technology Stack**:
- **Backend**: Python 3.12+, FastAPI, SQLAlchemy, Uvicorn
- **Frontend**: React 18, Vite, WebSocket
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Deployment**: Netlify (frontend), Render (backend)
- **CI/CD**: GitHub Actions

---

## 🎯 Critical Files (Must-Read for Understanding)

### Top 10 Files to Understand the System

1. **README.md** - Complete project overview
2. **bridge_backend/main.py** - Backend entry point & API routes
3. **bridge_backend/models.py** - Database schema
4. **bridge-frontend/src/App.jsx** - Frontend entry point
5. **GENESIS_ARCHITECTURE.md** - Engine orchestration
6. **DEPLOYMENT.md** - Production deployment guide
7. **bridge_backend/bridge_core/engines/blueprint/registry.py** - All 20 engines defined
8. **init.sql** - Complete database schema
9. **FORGE_DOMINION_DEPLOYMENT_GUIDE.md** - Security & token management
10. **AUTONOMY_DEPLOYMENT_README.md** - Self-healing system

---

## 🔄 System States & Lifecycle

### System Startup Sequence
```
1. Load Configuration (.env)
   ↓
2. Initialize Database (create tables)
   ↓
3. Create Default Guardian
   ↓
4. Initialize Genesis Linkage (connect engines)
   ↓
5. Start Health Monitoring
   ↓
6. Start API Server
   ↓
7. Start WebSocket Server
   ↓
8. System Ready ✅
```

### Mission Lifecycle
```
1. Captain creates Mission Brief
   ↓
2. Blueprint Engine generates Plan
   ↓
3. Plan broken into Tasks with dependencies
   ↓
4. Tasks assigned to Agents as Jobs
   ↓
5. Agents execute Jobs
   ↓
6. Progress tracked in real-time
   ↓
7. Mission completed ✅
```

### Self-Healing Cycle
```
1. Health Monitor detects issue
   ↓
2. Guardian triggers alert
   ↓
3. Autonomy Engine analyzes
   ↓
4. Recovery action determined
   ↓
5. Fix applied automatically
   ↓
6. System verified healthy ✅
```

---

## 🌟 Unique Features (What Makes This Special)

1. **Self-Healing**: Automatically detects and fixes issues
2. **Self-Deploying**: Auto-redeploys every 6 hours
3. **Self-Documenting**: Generates docs from code
4. **Zero Static Secrets**: All credentials are ephemeral
5. **Sovereign Runtime**: No vendor lock-in
6. **20 Specialized Engines**: From math to quantum physics
7. **Real-time Everything**: WebSocket updates everywhere
8. **Production-Ready**: Full CI/CD, monitoring, testing

---

## 🎓 Learning Path (Recommended Order)

### For Complete Beginners
1. Read `README.md` (30 min)
2. Read this file (`MASTER_ROADMAP.md`) (20 min)
3. Follow `QUICK_START_30MIN.md` (30 min)
4. Explore the running system (1 hour)
5. Read `SYSTEM_BLUEPRINT.md` (1 hour)
6. Read specific feature guides as needed

### For Developers
1. Skim `README.md` (10 min)
2. Read `SYSTEM_BLUEPRINT.md` (30 min)
3. Read `BUILD_DOSSIER.md` (30 min)
4. Review `bridge_backend/main.py` (20 min)
5. Review API docs at `/docs` (20 min)
6. Start coding!

### For DevOps/Deployment
1. Read `DEPLOYMENT.md` (30 min)
2. Read `BRIDGE_DEPLOY_GUIDE.md` (20 min)
3. Review `.github/workflows/` (30 min)
4. Review `netlify.toml` and `infra/render.yaml` (15 min)
5. Deploy!

---

## 🚨 Common Pitfalls & How to Avoid Them

1. **Python Version**: Must be 3.12+
   - Check: `python --version`

2. **Node Version**: Must be 18+
   - Check: `node --version`

3. **Database Issues**: SQLite file permissions
   - Solution: Check file permissions, or delete and recreate

4. **CORS Errors**: Frontend can't connect to backend
   - Solution: Add frontend URL to `ALLOWED_ORIGINS`

5. **Missing Dependencies**: Modules not found
   - Solution: `pip install -r requirements.txt` and `npm install`

6. **Port Conflicts**: Port 8000 or 3000 already in use
   - Solution: Use different port or kill existing process

7. **Environment Variables**: Missing `.env` file
   - Solution: Copy `.env.example` to `.env`

---

## 📞 Getting Help

1. **Documentation**: Check relevant guide in `docs/`
2. **Health Dashboard**: Visit `/system-selftest` for diagnostics
3. **API Docs**: Visit `/docs` for interactive testing
4. **Logs**: Check backend console output
5. **Self-Heal**: Try `POST /health/self-heal`
6. **GitHub Issues**: Search or create issue

---

## 🎯 Next Steps

Now that you have the map, choose your path:

- **Want to understand the architecture?** → Read `SYSTEM_BLUEPRINT.md`
- **Want to build it yourself?** → Read `BUILD_DOSSIER.md`
- **Want to get started fast?** → Read `QUICK_START_30MIN.md`
- **Want to see the engines?** → Read `ENGINE_CATALOG.md`
- **Want to deploy?** → Read `DEPLOYMENT.md`

---

## 📜 Version & Status

- **Current Version**: v5.5.3 "Sovereign"
- **Status**: Production Ready ✅
- **Last Major Update**: v1.9.7s (Forge Dominion Sovereign)
- **Documentation Status**: Complete

---

**Built with ❤️ by Admiral Kyle S. Whitlock and Contributors**

*This is your bridge. Command it well.*
