# Component Index
## Complete File & Component Reference for SR-AIbridge

> **Purpose**: A comprehensive directory of every major file and component in the project with descriptions and locations.

---

## 📁 Root Level Files

### Documentation
| File | Purpose |
|------|---------|
| `README.md` | Main project documentation - START HERE |
| `MASTER_ROADMAP.md` | Complete project map and navigation guide |
| `SYSTEM_BLUEPRINT.md` | Technical architecture and implementation details |
| `BUILD_DOSSIER.md` | Step-by-step rebuild guide from scratch |
| `QUICK_START_30MIN.md` | Fast track 30-minute setup guide |
| `COMPONENT_INDEX.md` | This file - complete component reference |
| `ENGINE_CATALOG.md` | All 20 engines documented |
| `DEPLOYMENT.md` | Production deployment guide |
| `SECURITY.md` | Security features and best practices |
| `CHANGELOG.md` | Version history and updates (34KB) |
| `LICENSE` | MIT License |

### Configuration Files
| File | Purpose |
|------|---------|
| `.env.example` | Environment variables template |
| `.gitignore` | Git ignore rules |
| `requirements.txt` | Python dependencies (root) |
| `pytest.ini` | Testing configuration |
| `netlify.toml` | Frontend deployment config |
| `bridge.runtime.yaml` | BRH runtime configuration |

### Database Files
| File | Purpose |
|------|---------|
| `init.sql` | PostgreSQL database initialization (12KB) |
| `maintenance.sql` | Monthly database maintenance (5KB) |
| `blueprint_partition_patch.sql` | Table partitioning for agent_jobs (5KB) |

### Scripts & Tools
| File | Purpose |
|------|---------|
| `test_endpoints_full.py` | Comprehensive endpoint testing (15KB) |
| `smoke_test_engines.sh` | Engine validation script (9KB) |
| `validate_genesis_unified.py` | Genesis linkage validation (9KB) |
| `verify_hxo_nexus.py` | HXO Nexus connectivity test (6KB) |
| `activate_autonomy.py` | Autonomy engine activation (5KB) |
| `count_loc.py` | Lines of code counter (7KB) |
| `get_env_drift.py` | Environment drift detection (3KB) |
| `genesisctl` | Genesis control script |
| `start.sh` | Quick start script |

---

## 🐍 Backend (`bridge_backend/`)

### Core Files
| File | Location | Purpose | Size |
|------|----------|---------|------|
| `main.py` | `bridge_backend/` | FastAPI application entry point | 30KB |
| `config.py` | `bridge_backend/` | Configuration management | 4KB |
| `db.py` | `bridge_backend/` | Database connection and session | 16KB |
| `models.py` | `bridge_backend/` | SQLAlchemy database models | 6KB |
| `schemas.py` | `bridge_backend/` | Pydantic validation schemas | 9KB |
| `seed.py` | `bridge_backend/` | Demo data seeder | 17KB |
| `requirements.txt` | `bridge_backend/` | Python dependencies | 314 bytes |
| `Dockerfile` | `bridge_backend/` | Docker configuration | 833 bytes |

### Bridge Core (`bridge_backend/bridge_core/`)

#### Agents System
| File | Purpose |
|------|---------|
| `agents/__init__.py` | Agent module initialization |
| `agents/service.py` | Agent business logic |
| `agents/routes.py` | Agent API endpoints |
| `agents/models.py` | Agent-specific models |

#### Missions System
| File | Purpose |
|------|---------|
| `missions/__init__.py` | Mission module initialization |
| `missions/service.py` | Mission business logic |
| `missions/routes.py` | Mission API endpoints |
| `missions/blueprint_integration.py` | Blueprint integration |

#### Health Monitoring
| File | Purpose |
|------|---------|
| `health/__init__.py` | Health module initialization |
| `health/monitor.py` | Health monitoring service |
| `health/routes.py` | Health API endpoints |
| `health/self_healing.py` | Auto-recovery logic |

#### Guardians System
| File | Purpose |
|------|---------|
| `guardians/__init__.py` | Guardian module initialization |
| `guardians/service.py` | Guardian business logic |
| `guardians/routes.py` | Guardian API endpoints |
| `guardians/monitor.py` | Guardian monitoring |

#### Vault/Logging
| File | Purpose |
|------|---------|
| `vault/__init__.py` | Vault module initialization |
| `vault/logger.py` | Logging service |
| `vault/routes.py` | Vault API endpoints |
| `vault/storage.py` | Log storage management |

#### Fleet Management
| File | Purpose |
|------|---------|
| `fleet/__init__.py` | Fleet module initialization |
| `fleet/service.py` | Fleet coordination |
| `fleet/routes.py` | Fleet API endpoints |
| `fleet/armada.py` | Armada management |

#### Captains System
| File | Purpose |
|------|---------|
| `captains/__init__.py` | Captain module initialization |
| `captains/messaging.py` | Captain-to-captain messaging |
| `captains/routes.py` | Captain API endpoints |
| `captains/chat.py` | Chat functionality |

#### Custody/Keys
| File | Purpose |
|------|---------|
| `custody/__init__.py` | Custody module initialization |
| `custody/admiral_keys.py` | Cryptographic key management |
| `custody/dock_day.py` | Dock-day export system |
| `custody/routes.py` | Custody API endpoints |

#### Forge Dominion (Token Management)
| File | Purpose |
|------|---------|
| `token_forge_dominion/__init__.py` | Forge module initialization |
| `token_forge_dominion/manager.py` | Token lifecycle management |
| `token_forge_dominion/renewal.py` | Automatic token renewal |
| `token_forge_dominion/vault.py` | Secure token storage |

#### Runtime Handler (BRH)
| File | Purpose |
|------|---------|
| `runtime_handler.py` | Bridge Runtime Handler implementation |
| `runtime/__init__.py` | Runtime module |
| `runtime/supervisor.py` | Runtime supervision |
| `runtime/containers.py` | Container management |

---

## 🧠 Engines (`bridge_backend/bridge_core/engines/`)

### Blueprint Engine
| File | Purpose |
|------|---------|
| `blueprint/__init__.py` | Blueprint module init |
| `blueprint/blueprint_engine.py` | Core planning engine |
| `blueprint/planner_rules.py` | Planning logic |
| `blueprint/routes.py` | Blueprint API endpoints |
| `blueprint/registry.py` | Engine registry (20 engines) |
| `blueprint/adapters/` | Engine adapter modules |

### Leviathan Solver
| File | Purpose |
|------|---------|
| `leviathan/__init__.py` | Leviathan module init |
| `leviathan/solver.py` | Task orchestration |
| `leviathan/coordinator.py` | Engine coordination |
| `leviathan/routes.py` | Leviathan endpoints |

### Autonomy Engine
| File | Purpose |
|------|---------|
| `autonomy/__init__.py` | Autonomy module init |
| `autonomy/engine.py` | Self-healing engine |
| `autonomy/rules.py` | Autonomy rules |
| `autonomy/integrations.py` | Triage/federation integration |

### TDE-X Engine
| File | Purpose |
|------|---------|
| `tde_x/__init__.py` | TDE-X module init |
| `tde_x/tri_domain.py` | Three-shard execution |
| `tde_x/bootstrap.py` | Bootstrap shard |
| `tde_x/runtime.py` | Runtime shard |
| `tde_x/diagnostics.py` | Diagnostics shard |

### Cascade Engine
| File | Purpose |
|------|---------|
| `cascade/__init__.py` | Cascade module init |
| `cascade/dag.py` | DAG orchestration |
| `cascade/executor.py` | Task execution |

### Truth Engine
| File | Purpose |
|------|---------|
| `truth/__init__.py` | Truth module init |
| `truth/validator.py` | Fact certification |
| `truth/rollback.py` | Rollback protection |

### Super Engines (6)
| Directory | Engine | Purpose |
|-----------|--------|---------|
| `calculus_core/` | CalculusCore | Mathematical operations |
| `qhelm/` | QHelmSingularity | Quantum operations |
| `aurora/` | AuroraForge | Creative/science |
| `chronicle/` | ChronicleLoom | Historical analysis |
| `scroll/` | ScrollTongue | Language processing |
| `commerce/` | CommerceForge | Business analytics |

### Utility Engines (7)
| Directory | Engine | Purpose |
|-----------|--------|---------|
| `creativity/` | Creativity Bay | Asset management |
| `indoctrination/` | Indoctrination | Agent onboarding |
| `screen/` | Screen Engine | Screen sharing |
| `speech/` | Speech Engine | TTS/STT |
| `recovery/` | Recovery | Task dispatch |
| `agents_foundry/` | AgentsFoundry | Agent creation |
| `filing/` | Filing | File management |

---

## ⚛️ Frontend (`bridge-frontend/`)

### Root Files
| File | Purpose |
|------|---------|
| `package.json` | Node.js dependencies |
| `vite.config.js` | Vite build configuration |
| `index.html` | HTML entry point |
| `netlify.toml` | Netlify deployment config |
| `.npmrc` | NPM configuration |

### Source Files (`bridge-frontend/src/`)

| File | Purpose |
|------|---------|
| `main.jsx` | Application entry point |
| `App.jsx` | Main application component |
| `App.css` | Global styles |

### Components (`bridge-frontend/src/components/`)

#### Core Components
| Component | Purpose |
|-----------|---------|
| `CommandDeck.jsx` | Main unified dashboard |
| `Dashboard.jsx` | System overview |
| `SystemSelfTest.jsx` | Health monitoring dashboard |

#### Mission & Planning
| Component | Purpose |
|-----------|---------|
| `MissionLog.jsx` | Mission tracking (v1) |
| `MissionLogV2.jsx` | Mission tracking with blueprints |
| `BlueprintWizard.jsx` | Blueprint creation wizard |
| `AgentDeliberationPanel.jsx` | Real-time agent activity |

#### Agent & Fleet
| Component | Purpose |
|-----------|---------|
| `AgentPanel.jsx` | Agent management |
| `ArmadaMap.jsx` | Fleet visualization |
| `FleetStatus.jsx` | Fleet status display |

#### Communication
| Component | Purpose |
|-----------|---------|
| `CaptainToCaptain.jsx` | Captain messaging |
| `CaptainsChat.jsx` | Chat interface |
| `MessagePanel.jsx` | Message display |

#### Data & Logging
| Component | Purpose |
|-----------|---------|
| `VaultLogs.jsx` | Activity log viewer |
| `UnifiedLeviathanPanel.jsx` | Knowledge search |
| `DoctrineViewer.jsx` | Doctrine display |

#### Administration
| Component | Purpose |
|-----------|---------|
| `AdmiralKeysPanel.jsx` | Cryptographic key management |
| `BrainConsole.jsx` | Interactive command console |
| `PermissionsConsole.jsx` | Permission management |
| `IndoctrinationPanel.jsx` | System configuration |

#### Specialized Panels
| Component | Purpose |
|-----------|---------|
| `TierPanel.jsx` | Tier-based organization |
| `ChimeraPanel.jsx` | Chimera interface |
| `UmbraPanel.jsx` | Umbra management |
| `StewardPanel.jsx` | Steward interface |

### UI Components (`bridge-frontend/src/components/ui/`)
| Component | Purpose |
|-----------|---------|
| `button.jsx` | Reusable button |
| `card.jsx` | Card layout |
| `badge.jsx` | Status badges |
| `Tree.tsx` | Hierarchical tree view |

### API Client (`bridge-frontend/src/api/`)
| File | Purpose |
|------|---------|
| `client.js` | API client functions |
| `websocket.js` | WebSocket connections |
| `agents.js` | Agent API calls |
| `missions.js` | Mission API calls |

---

## 🔧 Infrastructure

### CI/CD (`.github/workflows/`)
| Workflow | Purpose |
|----------|---------|
| `bridge-deploy.yml` | Main deployment workflow |
| `bridge_autodeploy.yml` | Auto-deploy every 6 hours |
| `self-test.yml` | Health check workflow |

### Deployment
| File | Purpose |
|------|---------|
| `infra/render.yaml` | Render.com configuration |
| `netlify.toml` | Netlify configuration |
| `Procfile` | Process definition |

---

## 📚 Documentation (`docs/`)

### Quick References (26 files)
- `*_QUICK_REF.md` - Quick reference guides
- `*_GUIDE.md` - Comprehensive guides  
- `*_IMPLEMENTATION.md` - Implementation details

### Key Documentation
| File | Topic |
|------|-------|
| `AUTONOMY_INTEGRATION.md` | Autonomy system |
| `HXO_ENGINE_MATRIX.md` | HXO Nexus |
| `GITHUB_FORGE.md` | Forge Dominion |
| `ENVIRONMENT_SETUP.md` | Environment configuration |
| `BRIDGE_PARITY_ENGINE.md` | Parity system |
| `HEALER_NET.md` | Self-healing network |

---

## 📊 Stats Summary

### File Counts
- **Total Files**: 500+
- **Python Files**: 200+
- **JavaScript/JSX Files**: 50+
- **Markdown Documentation**: 100+
- **Configuration Files**: 20+

### Code Volume
- **Backend Python**: ~50,000 lines
- **Frontend JavaScript**: ~15,000 lines
- **Documentation**: ~100,000 words
- **SQL Scripts**: ~2,000 lines

### Component Counts
- **React Components**: 40+
- **API Endpoints**: 150+
- **Database Tables**: 20+
- **Engines**: 20
- **Workflows**: 3

---

## 🔍 Quick Find Guide

**Looking for...**

- **Agent management**: `bridge_backend/bridge_core/agents/`
- **Mission control**: `bridge_backend/bridge_core/missions/`
- **Health monitoring**: `bridge_backend/bridge_core/health/`
- **Engine code**: `bridge_backend/bridge_core/engines/`
- **Frontend dashboard**: `bridge-frontend/src/components/Dashboard.jsx`
- **API routes**: `bridge_backend/main.py`
- **Database models**: `bridge_backend/models.py`
- **Configuration**: `.env`, `config.py`
- **Deployment**: `netlify.toml`, `infra/render.yaml`
- **CI/CD**: `.github/workflows/`
- **Documentation**: `docs/`, `*.md` files
- **Tests**: `tests/`, `test_*.py`, `*_test.sh`

---

**Complete component reference for SR-AIbridge. Every file mapped, every component cataloged.**

*Navigate with confidence.*
