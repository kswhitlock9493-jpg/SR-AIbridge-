# SR-AIbridge Complete Navigation Guide

**Generated:** 2025-11-05 (Sovereign Git Mode Active)  
**Analysis Tools:** ARIE, ALIK, Truth Engine, Parser Engine, Blueprint Engine

## 🎯 Quick Start

**New to SR-AIbridge?** Start here:
1. Read [START_HERE.md](START_HERE.md) (5 min)
2. Review [README.md](README.md) (15 min)
3. Follow the path below based on your role

**Looking for something specific?** Use the Index below or Ctrl+F to search.

---

## 📊 Repository Overview

### Key Stats
- **Total Files:** 1,526
- **Lines of Code:** 354,643
- **Documentation Files:** 352+ markdown files
- **Engines:** 33+ specialized engines
- **Backend Modules:** 32+ subdirectories
- **Frontend Components:** 40+ React components

### Repository Health
✅ **Excellent** - Comprehensive documentation, rich engine ecosystem, active development

---

## 🗂️ Repository Structure Map

### Root Level (Essential Files Only)

```
SR-AIbridge/
├── README.md                          # Main documentation (START HERE!)
├── START_HERE.md                      # Quick orientation guide
├── REPO_MAP.md                        # Comprehensive repository map
├── DIAGNOSTIC_REPORT.md               # Full diagnostic & incident report
├── NAVIGATION_GUIDE.md                # This file - complete navigation
├── CHANGELOG.md                       # Version history
├── IMPLEMENTATION_SUMMARY.md          # Implementation details
├── SECURITY.md                        # Security policies
├── SECURITY_AUDIT_SUMMARY.md          # Security audit results
├── SOVEREIGN_*.md                     # Sovereign deployment guides
│
├── .env.example                       # Environment template
├── requirements.txt                   # Python dependencies
├── package.json                       # (in bridge-frontend)
├── netlify.toml                       # Netlify config
├── bridge.runtime.yaml                # Runtime configuration
│
├── activate_autonomy.py               # Autonomy activation script
├── start.sh                           # Quick start script
│
├── bridge_backend/                    # Backend application (FastAPI/Python)
├── bridge-frontend/                   # Frontend application (React)
├── bridge_core/                       # Core bridge functionality
├── docs/                              # Documentation (352+ files!)
├── vault/                             # Archival & reference materials
├── codex/                             # Truth & Parser engines
├── DOCTRINE/                          # Agent doctrine and archetypes
├── scripts/                           # Utility scripts
├── tests/                             # Test suites
└── tools/                             # Development tools
```

---

## 🏗️ Core Components

### 1. Backend (`bridge_backend/`)
**Purpose:** FastAPI-based backend server with 100+ endpoints

**Key Directories:**
- `bridge_core/` - Core functionality and engines
  - `engines/` - 17+ core engines (see Engine Inventory below)
- `engines/` - 16+ specialized backend engines
- `routes/` - API route handlers
- `models/` - Data models
- `db.py` - Database layer
- `main.py` - Application entry point

**Starting Point:** `bridge_backend/main.py`  
**Documentation:** `docs/backend/` (multiple guides)

### 2. Frontend (`bridge-frontend/`)
**Purpose:** React-based command center UI

**Key Features:**
- Command Deck - Main dashboard
- Vault Logs - `/vault-logs` tab (already implemented!)
- Mission Log - Mission tracking
- Captain's Chat - Communication
- System Health - Diagnostics
- And 8+ more views!

**Starting Point:** `bridge-frontend/src/App.jsx`  
**Components:** `bridge-frontend/src/components/`  
**Documentation:** `docs/frontend/`

### 3. Documentation (`docs/`)
**352+ markdown files covering:**
- Engine guides and references
- API documentation
- Deployment guides
- Quick reference cards
- Integration guides
- System architecture

**Key Docs:**
- `docs/ENGINE_*.md` - Individual engine guides
- `docs/*_QUICK_REF.md` - Quick reference cards
- `docs/versions/` - Version-specific docs

### 4. Vault (`vault/`)
**Purpose:** Archival and reference materials

**Structure:**
```
vault/
├── archived_scripts/     # Test, validation, study scripts
├── reference_sql/        # SQL patches and migrations
├── old_configs/          # Archived configurations
├── documentation/        # Historical documentation
└── README.md            # Vault usage guide
```

**Contents:**
- Test scripts: `smoke_test_engines.py`, `validate_genesis_unified.py`, etc.
- SQL references: `init.sql`, `maintenance.sql`, `blueprint_partition_patch.sql`
- Old configs: `.env.v197*.example`, `.env.template`, etc.
- Historical reports: `REPO_STUDY_REPORT.json`

**Note:** Vault UI tab at `/vault-logs` is separate (runtime feature)

---

## 🔧 Engine Inventory

SR-AIbridge has 33+ specialized engines organized in two locations:

### Core Engines (`bridge_backend/bridge_core/engines/`)
1. **adapters** - Engine interconnection adapters
2. **agents_foundry** - Agent creation and management
3. **autonomy** - Self-healing and autonomous operations
4. **blueprint** - Mission planning and orchestration
5. **cascade** - Cascading operations
6. **chimera** - Multi-mode operations
7. **creativity** - Creative AI capabilities
8. **envsync** - Environment synchronization
9. **hxo** - HXO Nexus harmonic conductor
10. **indoctrination** - Agent indoctrination system
11. **leviathan** - Advanced solver engine
12. **parser** - Documentation parsing (see codex/parser_engine.py)
13. **recovery** - System recovery orchestration
14. **screen** - Display and visualization
15. **speech** - TTS/STT capabilities
16. **truth** - Truth validation (see codex/truth_engine.py)
17. **umbra** - Shadow operations

### Backend Engines (`bridge_backend/engines/`)
1. **arie** - ARIE specialized engine
2. **autonomy** - Autonomy backend
3. **chimera** - Chimera backend
4. **elysium** - Elysium engine
5. **envrecon** - Environment reconnaissance
6. **envscribe** - Environment scribing
7. **forge** - Forge Dominion token management
8. **github_forge** - GitHub integration
9. **hydra** - Multi-head operations
10. **hypshard_x** - HypShard v3 scaling
11. **leviathan** - Leviathan backend
12. **render_fallback** - Render deployment fallback
13. **sanctum** - Sanctum loop operations
14. **selftest** - Self-testing capabilities
15. **steward** - System stewardship
16. **umbra** - Umbra backend

### Special Engines (Codex)
- **Truth Engine** (`codex/truth_engine.py`) - Fact validation and deduplication
- **Parser Engine** (`codex/parser_engine.py`) - Document parsing and chunking
- **ALIK** (`.alik/` directory) - ALIK specialized technology
- **ARIE** (`docs/ARIE_*.md`) - 8+ ARIE documentation references

**Documentation:** Each engine has guides in `docs/`

---

## 👥 Role-Based Navigation

### New Users / Learning
1. **Start:** [START_HERE.md](START_HERE.md)
2. **Overview:** [README.md](README.md)
3. **Map:** [REPO_MAP.md](REPO_MAP.md) ← You are here: [NAVIGATION_GUIDE.md](NAVIGATION_GUIDE.md)
4. **Health:** [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md)
5. **Explore:** `docs/` directory

### Developers
1. **Architecture:** [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md)
2. **Backend:** `bridge_backend/README.md` (if exists) or explore `bridge_backend/`
3. **Frontend:** `bridge-frontend/README.md`
4. **Engines:** Browse `bridge_backend/bridge_core/engines/` and `docs/`
5. **API:** Check `bridge_backend/main.py` for endpoints

### DevOps / Deployment
1. **Deployment:** `SOVEREIGN_DEPLOYMENT.md`, `SOVEREIGN_ENGINES_DEPLOYMENT.md`
2. **Configuration:** `.env.example`, `netlify.toml`, `bridge.runtime.yaml`
3. **Security:** `SECURITY.md`, `SECURITY_AUDIT_SUMMARY.md`
4. **Scripts:** `start.sh`, `activate_autonomy.py`

### Contributors
1. **Guidelines:** Check for `CONTRIBUTING.md` or see [README.md](README.md)
2. **Testing:** `tests/` directory and vault scripts
3. **Documentation:** `docs/` - add new docs here
4. **Vault Usage:** `vault/README.md` for archival guidelines

---

## 🔍 Finding What You Need

### By Topic

**Engines:**
- Documentation: `docs/ENGINE_*.md`, `docs/*_ENGINE*.md`
- Code: `bridge_backend/bridge_core/engines/`, `bridge_backend/engines/`
- References: `docs/*_QUICK_REF.md`

**API & Endpoints:**
- Main API: `bridge_backend/main.py`
- Routes: `bridge_backend/routes/`
- Auto-generated: `bridge-frontend/src/api/auto_generated/`

**Configuration:**
- Environment: `.env.example`, vault old configs
- Runtime: `bridge.runtime.yaml`
- Netlify: `netlify.toml`
- Python: `requirements.txt`, `pytest.ini`

**Security:**
- Policies: `SECURITY.md`
- Audits: `SECURITY_AUDIT_SUMMARY.md`, `SOVEREIGN_AUDIT_SUMMARY.md`
- Contact: `SECURITY_CONTACT`

**Testing:**
- Test suites: `tests/`, `bridge_backend/tests/`
- Archived test scripts: `vault/archived_scripts/`
- Self-test: `bridge_backend/engines/selftest/`

**Database:**
- Reference SQL: `vault/reference_sql/`
- DB layer: `bridge_backend/db.py`
- Models: `bridge_backend/models.py`

**UI Components:**
- All components: `bridge-frontend/src/components/`
- Pages: `bridge-frontend/src/pages/`
- Styles: `bridge-frontend/src/styles.css`
- Vault UI: `bridge-frontend/src/components/VaultLogs.jsx`

### By File Type

**Markdown Documentation:**
```bash
find docs -name "*.md"                    # All docs
find . -name "*QUICK_REF.md"              # Quick references
find . -name "*_GUIDE.md"                 # Guides
```

**Python Code:**
```bash
find bridge_backend -name "*.py"          # Backend code
find bridge_core -name "*.py"             # Core code
find vault/archived_scripts -name "*.py"  # Archived scripts
```

**JavaScript/React:**
```bash
find bridge-frontend/src -name "*.jsx"    # React components
find bridge-frontend/src -name "*.js"     # JavaScript files
```

---

## 📋 Common Tasks

### Running the Application

**Backend:**
```bash
cd bridge_backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd bridge-frontend
npm install
npm run dev
```

**Quick Start:**
```bash
./start.sh  # If available
```

### Running Tests

**From vault (archived):**
```bash
python vault/archived_scripts/smoke_test_engines.py
python vault/archived_scripts/validate_genesis_unified.py
python vault/archived_scripts/verify_hxo_nexus.py
```

**Test suites:**
```bash
cd bridge_backend
pytest tests/
```

### Analyzing the Repository

**Using archived scripts:**
```bash
python vault/archived_scripts/study_repo_with_engines.py
bash vault/archived_scripts/run_repo_study.sh
```

**Counting lines:**
```bash
python vault/archived_scripts/count_loc.py
```

### Working with Database

**Reference SQL (from vault):**
```bash
# Initialize database
psql < vault/reference_sql/init.sql

# Apply patches
psql < vault/reference_sql/blueprint_partition_patch.sql

# Maintenance
psql < vault/reference_sql/maintenance.sql
```

### Accessing Vault UI

The Bridge UI has a **Vault Logs** tab accessible at:
- URL: `http://localhost:PORT/vault-logs`
- Component: `bridge-frontend/src/components/VaultLogs.jsx`
- API: Backend vault endpoints

Note: This is the runtime vault feature, separate from the root `vault/` directory.

---

## 🔗 Key Integrations

### ARIE (AI Reasoning & Intelligence Engine)
- **Documentation:** `docs/ARIE_*.md` (8 files)
- **Backend:** `bridge_backend/engines/arie/`
- **References:** `docs/ARIE_QUICK_REF.md`, `docs/ARIE_V196O_QUICK_REF.md`

### ALIK (AI Logic Integration Kit)
- **Directory:** `.alik/`
- **Status:** Present with .gitkeep

### Truth Engine
- **Core:** `codex/truth_engine.py`
- **Bridge Integration:** `bridge_backend/bridge_core/engines/truth/`
- **Tests:** `bridge_backend/tests/test_truth_engine.py`

### Parser Engine
- **Core:** `codex/parser_engine.py`
- **Bridge Integration:** `bridge_backend/bridge_core/engines/parser/`
- **Tests:** `bridge_backend/tests/test_parser_engine.py`

### HXO Nexus
- **Engine:** `bridge_backend/bridge_core/engines/hxo/`
- **Documentation:** `docs/HXO_NEXUS_*.md`
- **Verification:** `vault/archived_scripts/verify_hxo_nexus.py`

### Forge Dominion
- **Engine:** `bridge_backend/engines/forge/`
- **Documentation:** `FORGE_DOMINION_*.md`, `docs/FORGE_*.md`
- **Integration:** Token management and sovereignty

---

## 🛠️ Maintenance & Tools

### Development Tools
- **Location:** `tools/`
- **Scripts:** `scripts/`
- **Archived:** `vault/archived_scripts/`

### Configuration Drift
- **Script:** `vault/archived_scripts/get_env_drift.py`
- **Purpose:** Detect environment configuration drift

### Line Counting
- **Script:** `vault/archived_scripts/count_loc.py`
- **Purpose:** Count lines of code in project

### Smoke Testing
- **Scripts:** `vault/archived_scripts/smoke_test_engines.*`
- **Purpose:** Quick validation of all engines

---

## 📦 Dependencies

### Python (Backend)
- **File:** `requirements.txt` (root)
- **Backend:** `bridge_backend/requirements.txt`
- **Key:** FastAPI, asyncio, aiohttp, SQLAlchemy, etc.

### JavaScript (Frontend)
- **File:** `bridge-frontend/package.json`
- **Key:** React, React Router, Vite, etc.

### System
- **Python:** 3.12+
- **Node.js:** See `.nvmrc`

---

## 🚀 Deployment

### Netlify (Frontend)
- **Config:** `netlify.toml`
- **Functions:** `bridge-frontend/netlify/functions/`
- **Environment:** `.env.netlify.example`

### Runtime (Backend)
- **Config:** `bridge.runtime.yaml`
- **Guides:** `SOVEREIGN_DEPLOYMENT.md`, `SOVEREIGN_ENGINES_DEPLOYMENT.md`

### Docker
- **File:** `bridge_backend/Dockerfile`
- **Procfile:** `Procfile` (root)

---

## 📝 Documentation Standards

### Adding New Documentation
1. Create in appropriate `docs/` subdirectory
2. Use clear, descriptive filenames
3. Include quick reference if detailed guide
4. Cross-reference related docs
5. Update this navigation guide

### Archiving Files
1. Determine if file is reference/archival
2. Choose appropriate vault subdirectory
3. Move file preserving name
4. Update vault/README.md if significant
5. Update documentation references

---

## 🎓 Learning Paths

### Path 1: Understanding SR-AIbridge (1 hour)
1. START_HERE.md (5 min)
2. README.md (15 min)
3. NAVIGATION_GUIDE.md (10 min) ← You are here
4. REPO_MAP.md (10 min)
5. DIAGNOSTIC_REPORT.md (20 min)

### Path 2: Development Setup (30 min)
1. Clone repository
2. Review .env.example
3. Install dependencies (backend & frontend)
4. Run smoke tests (from vault)
5. Start applications

### Path 3: Engine Mastery (2-4 hours)
1. Read engine overview in DIAGNOSTIC_REPORT.md
2. Explore `bridge_backend/bridge_core/engines/`
3. Review individual engine docs in `docs/`
4. Study engine interconnections
5. Run engine-specific tests

### Path 4: Contributing (Variable)
1. Understand architecture (DIAGNOSTIC_REPORT.md)
2. Review SECURITY.md
3. Set up development environment
4. Make changes
5. Test thoroughly
6. Submit PR

---

## ❓ Troubleshooting

### Can't find a specific engine?
- Check `bridge_backend/bridge_core/engines/`
- Check `bridge_backend/engines/`
- Search docs: `find docs -name "*ENGINE_NAME*"`

### Missing dependencies?
- Backend: `pip install -r requirements.txt`
- Frontend: `cd bridge-frontend && npm install`

### Configuration issues?
- Review `.env.example`
- Check active configs in vault: `vault/old_configs/`
- Verify runtime config: `bridge.runtime.yaml`

### Tests failing?
- Run smoke tests: `python vault/archived_scripts/smoke_test_engines.py`
- Check test directory: `tests/`
- Review DIAGNOSTIC_REPORT.md for known issues

### Documentation unclear?
- Check for quick reference: `docs/*_QUICK_REF.md`
- Review related docs in `docs/`
- Use this navigation guide to find related content

---

## 🔐 Security Notes

- Never commit secrets or credentials
- Use `.env.example` as template, never `.env`
- Review SECURITY.md for policies
- Check SECURITY_AUDIT_SUMMARY.md for audit results
- Report vulnerabilities per SECURITY_CONTACT

---

## 📊 Repository Statistics

**As of last analysis:**
- Total Files: 1,526
- Total Lines: 354,643
- Total Size: 14.57 MB
- Python Files: 740 (104,965 lines)
- Markdown Files: 395 (134,711 lines)
- JavaScript/JSX: 141 (9,094 lines)
- Engines: 33+
- Documentation Files: 352+

**Health Status:** ✅ Excellent  
**Test Coverage:** Multiple test suites  
**Documentation Coverage:** Comprehensive

---

## 🎯 Next Steps

**After reading this guide:**

1. **Explore:** Browse the repository structure
2. **Learn:** Read relevant documentation
3. **Build:** Set up development environment
4. **Contribute:** Make improvements
5. **Share:** Help others navigate

**Quick Links:**
- [START_HERE.md](START_HERE.md) - Orientation
- [README.md](README.md) - Main docs
- [REPO_MAP.md](REPO_MAP.md) - Detailed map
- [DIAGNOSTIC_REPORT.md](DIAGNOSTIC_REPORT.md) - Health report
- [vault/README.md](vault/README.md) - Vault usage

---

## 📞 Support & Contact

- **Security:** See SECURITY_CONTACT
- **Issues:** GitHub Issues
- **Documentation:** `docs/` directory
- **Vault:** `vault/README.md`

---

**Navigation Guide Status:** ✅ Complete  
**Last Updated:** 2025-11-05  
**Sovereign Git Mode:** Active  
**Coverage:** Complete repository mapping

**Thank you for using SR-AIbridge!** 🌉
