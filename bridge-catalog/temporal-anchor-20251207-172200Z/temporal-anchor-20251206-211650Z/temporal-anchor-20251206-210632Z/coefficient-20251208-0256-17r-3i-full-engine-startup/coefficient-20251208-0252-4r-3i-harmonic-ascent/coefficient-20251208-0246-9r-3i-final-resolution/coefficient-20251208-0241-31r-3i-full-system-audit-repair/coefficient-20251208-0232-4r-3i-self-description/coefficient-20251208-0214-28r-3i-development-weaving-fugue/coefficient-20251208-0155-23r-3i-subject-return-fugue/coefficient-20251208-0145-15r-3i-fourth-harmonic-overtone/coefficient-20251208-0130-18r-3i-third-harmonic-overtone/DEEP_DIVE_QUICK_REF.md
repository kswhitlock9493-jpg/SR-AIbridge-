# SR-AIbridge Deep Dive Quick Reference

**Fast Navigation Guide for System Exploration**

---

## 🎯 Start Here

You're looking at a **sovereign AI orchestration platform** with:
- **21 specialized engines**
- **298+ API endpoints**
- **558 comprehensive tests**
- **100,000+ lines of documentation**

**Current Status**: ✅ OPERATIONAL (99% resonance)

---

## 📚 Essential Reading (Priority Order)

### 1. First 5 Minutes
- `README.md` (first 100 lines) - Overview
- `START_HERE.md` - Getting started
- **THIS FILE** - Quick navigation

### 2. Next 15 Minutes
- `DEEP_DIVE_COMPREHENSIVE_ANALYSIS.md` - Full system analysis
- `SYSTEM_ARCHITECTURE_MAP.md` - Visual architecture

### 3. Next 30 Minutes
- `DEEP_DIVE_AUDIT_REPORT.md` - Production readiness
- `ENGINE_CATALOG.md` - All 21 engines explained
- `NAVIGATION_GUIDE.md` - Complete navigation

### 4. Deep Exploration (1-2 hours)
- `SYSTEM_BLUEPRINT.md` - Technical architecture
- `MASTER_ROADMAP.md` - Complete project map
- `DOCUMENTATION_INDEX.md` - Master index of all docs

---

## 🧠 The 21 Engines - Quick Lookup

### Want to plan missions?
→ **Blueprint Engine** (`bridge_backend/bridge_core/engines/blueprint/`)

### Need self-healing?
→ **Autonomy Engine** (`bridge_backend/bridge_core/engines/autonomy/`)

### Communication between systems?
→ **Genesis Event Bus** (`bridge_backend/genesis/`)

### Intelligent predictions?
→ **Umbra Lattice** (`bridge_backend/bridge_core/engines/umbra/`)

### Infinite scaling?
→ **HXO Nexus + HypShard** (`bridge_backend/engines/hypshard_x/`)

### Math computations?
→ **CalculusCore** (`bridge_backend/bridge_core/engines/calculuscore.py`)

### Language processing?
→ **LinguaCore** (Super Engine)

### Validation/fact-checking?
→ **Truth Engine** (`bridge_backend/bridge_core/engines/truth/`)

### Code analysis?
→ **Parser Engine** (`bridge_backend/bridge_core/engines/parser/`)

### Agent training?
→ **Indoctrination Engine** (`bridge_backend/bridge_core/engines/indoctrination/`)

---

## 🔍 Find Things Fast

### Looking for API endpoints?
```bash
# Count all endpoints
grep -r "@router\.\(get\|post\|put\|delete\|patch\)" bridge_backend/ --include="*.py" | wc -l
# Result: 298+

# See specific engine routes
ls bridge_backend/bridge_core/engines/*/routes.py
ls bridge_backend/engines/*/routes.py
```

### Want to see tests?
```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_blueprint_engine.py -v

# Count tests
pytest --collect-only -q | tail -1
# Result: 558 tests
```

### Need documentation?
```bash
# List all markdown files
find . -name "*.md" -type f | wc -l
# Result: 395 files, 134,711 lines

# Master index
cat docs/DOCUMENTATION_INDEX.md

# Feature inventory
cat docs/archive/FEATURE_INVENTORY.md
```

### Check system status?
```python
# Import test
python3 -c "from bridge_backend.main import app; print('✅ OK')"

# Or run server
cd bridge_backend && python -m bridge_backend.main
# Server starts on http://localhost:8000
```

---

## 🏗️ Architecture Quick Map

```
Frontend (React 18)
    ↓
API Gateway (298+ endpoints)
    ↓
Genesis Event Bus (33 topics)
    ↓
21 Engines (specialized processing)
    ↓
Database (SQLite/PostgreSQL)
```

**Key Files**:
- **Main Backend**: `bridge_backend/main.py` (700 lines, 60+ routers)
- **Event Bus**: `bridge_backend/genesis/bus.py` (18,814 lines)
- **Frontend App**: `bridge-frontend/src/App.jsx` (8,206 lines)

---

## 🚀 Run the System

### Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
cd bridge_backend
python -m bridge_backend.main
# or
python main.py

# Access at: http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Frontend
```bash
# Install dependencies
cd bridge-frontend
npm install

# Run dev server
npm run dev

# Access at: http://localhost:5173
```

### Tests
```bash
# Backend tests
pytest tests/ -v

# Frontend tests
cd bridge-frontend
npm test

# Specific test file
pytest tests/test_blueprint_engine.py -v
```

---

## 🔒 Security Quick Check

### Keyless Security
- **Auth**: `POST /auth/session` (ephemeral sessions)
- **Status**: `GET /auth/status`
- **No static secrets** in repository

### Forge Dominion
- **Token Management**: Auto-renewing ephemeral tokens
- **Location**: `bridge_backend/engines/forge/`
- **Tests**: `tests/test_forge_dominion_v197s.py`

### Zero-Trust
- **Scanner**: `tests/test_zero_trust_validation.py`
- **Quantum-resistant**: Cryptographic algorithms
- **Sanctum Cascade**: Boot hardening protocol

---

## 📊 Key Metrics Dashboard

| Metric | Value |
|--------|-------|
| **Files** | 1,526 |
| **Lines of Code** | 354,643 |
| **API Endpoints** | 298+ |
| **Engines** | 21 |
| **Event Topics** | 33 |
| **Tests** | 558 |
| **Documentation Lines** | 134,711 |
| **Doc:Code Ratio** | 1.28:1 |
| **Bridge Resonance** | 0.99 (99%) |
| **Status** | ✅ OPERATIONAL |

---

## 🎓 Common Tasks

### Add a New Engine
1. Create directory: `bridge_backend/bridge_core/engines/myengine/`
2. Add files: `__init__.py`, `routes.py`, `service.py`
3. Register router in `bridge_backend/main.py`
4. Add tests: `tests/test_myengine.py`
5. Document: Update `ENGINE_CATALOG.md`

### Add an API Endpoint
1. Find/create router: `bridge_backend/.../routes.py`
2. Add endpoint:
   ```python
   @router.get("/my-endpoint")
   async def my_endpoint():
       return {"status": "ok"}
   ```
3. Add test: `tests/test_my_endpoint.py`
4. Document: Update relevant docs

### Debug a Failure
1. Check logs: `bridge_backend/logs/`
2. Review Genesis events: `bridge_backend/.genesis/events.db`
3. Run specific test: `pytest tests/test_X.py -v`
4. Check health: `GET /api/health/health/full`

### Add Documentation
1. Create file: `docs/MY_FEATURE.md`
2. Update index: `docs/DOCUMENTATION_INDEX.md`
3. Update inventory: `docs/archive/FEATURE_INVENTORY.md`
4. Link from README if major feature

---

## 🔗 Important Links

### API Documentation
- **Swagger UI**: http://localhost:8000/docs (when running)
- **ReDoc**: http://localhost:8000/redoc (when running)

### GitHub
- **Repository**: https://github.com/kswhitlock9493-jpg/SR-AIbridge-
- **Issues**: Track bugs and features
- **Actions**: 72 CI/CD workflows

### Deployment
- **Frontend**: Netlify (sr-aibridge.netlify.app)
- **Backend**: BRH (sovereign runtime)
- **Monitoring**: Health endpoints + telemetry

---

## 🆘 Troubleshooting

### Backend won't start?
```bash
# Check imports
python3 -c "from bridge_backend.main import app"

# Check dependencies
pip install -r requirements.txt

# Check environment
cat .env
```

### Frontend won't build?
```bash
# Clear cache
rm -rf node_modules
npm install

# Check Node version (needs 20-22)
node --version

# Run with verbose
npm run build --verbose
```

### Tests failing?
```bash
# Run one test at a time
pytest tests/test_blueprint_engine.py::test_derive_objectives_base -v

# Check test environment
pytest --version
python --version

# See full output
pytest tests/test_X.py -vv
```

### Can't find something?
```bash
# Use master index
cat docs/DOCUMENTATION_INDEX.md | grep -i "search term"

# Search all code
grep -r "search term" bridge_backend/ --include="*.py"

# Search all docs
grep -r "search term" . --include="*.md"
```

---

## 💡 Pro Tips

1. **Use the Genesis Event Bus**: All systems communicate through events
2. **Check BRIDGE_RESONANCE**: Monitor system harmony (target: 0.99)
3. **Leverage Autonomy Engine**: It auto-heals failures
4. **Read test files**: They're great documentation
5. **Follow event flows**: Understand Genesis topics
6. **Use HXO Nexus**: For coordinating multiple engines
7. **Check Heritage events**: For debugging and time-travel

---

## 🎯 Quick Wins

### Want to see the system in action?
```bash
# 1. Start backend
cd bridge_backend && python -m bridge_backend.main

# 2. In another terminal, start frontend
cd bridge-frontend && npm run dev

# 3. Open browser to http://localhost:5173
# 4. Explore Command Deck, Mission Logs, System Monitor
```

### Want to understand an engine?
```bash
# 1. Read its catalog entry
grep -A 50 "Blueprint Engine" docs/ENGINE_CATALOG.md

# 2. Check its routes
cat bridge_backend/bridge_core/engines/blueprint/routes.py

# 3. Run its tests
pytest tests/test_blueprint_engine.py -v

# 4. See it in action
curl http://localhost:8000/blueprint/status
```

### Want to add a feature?
1. Find similar feature in codebase
2. Copy and modify
3. Add tests (558 existing tests as examples)
4. Document it
5. Submit PR

---

## 📖 Documentation Structure

```
SR-AIbridge/
├── README.md                              # Start here
├── START_HERE.md                          # Getting started
├── DEEP_DIVE_COMPREHENSIVE_ANALYSIS.md    # ← Full system analysis
├── SYSTEM_ARCHITECTURE_MAP.md             # ← Visual architecture
├── DEEP_DIVE_QUICK_REF.md                 # ← YOU ARE HERE
├── docs/
│   ├── DOCUMENTATION_INDEX.md             # Master index
│   ├── NAVIGATION_GUIDE.md                # Navigation
│   ├── ENGINE_CATALOG.md                  # All 21 engines
│   ├── SYSTEM_BLUEPRINT.md                # Architecture
│   ├── MASTER_ROADMAP.md                  # Project map
│   └── quickrefs/                         # Quick references
└── tests/                                 # 558 tests
```

---

## 🚀 Next Steps

### New to SR-AIbridge?
1. Read README.md (15 min)
2. Read this file (10 min)
3. Read DEEP_DIVE_COMPREHENSIVE_ANALYSIS.md (30 min)
4. Run the system locally (30 min)
5. Explore engines via ENGINE_CATALOG.md (1 hour)

### Want to contribute?
1. Pick an undocumented feature from FEATURE_INVENTORY.md
2. Study similar code in codebase
3. Write documentation
4. Add tests if needed
5. Submit PR

### Want to deploy?
1. Read DEPLOYMENT_IMPLEMENTATION_SUMMARY.md
2. Read FORGE_DOMINION_DEPLOYMENT_GUIDE.md
3. Follow BRH_GUIDE.md for backend
4. Configure Netlify for frontend
5. Monitor with health endpoints

---

## 🎉 You're Ready!

You now have:
- ✅ Quick reference to all systems
- ✅ Fast lookup for engines
- ✅ Command examples
- ✅ Troubleshooting guide
- ✅ Navigation to detailed docs

**Go build something amazing with SR-AIbridge!** 🌉⚡

---

**Created**: 2025-11-07  
**Purpose**: Fast navigation and reference  
**Use**: Keep open while exploring the system  
**Next**: DEEP_DIVE_COMPREHENSIVE_ANALYSIS.md for full details  
