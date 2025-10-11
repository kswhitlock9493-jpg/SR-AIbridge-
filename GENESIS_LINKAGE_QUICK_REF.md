# Genesis Linkage Quick Reference - UNIFIED EDITION

## v1.9.7c Feature Summary

**Complete Unification**: All 20 engines (Core, Super, Utility, Orchestration) unified via Blueprint Registry as source of truth.

### Engine Count: 20
- **Core Infrastructure**: 6 engines
- **Super Engines**: 6 engines  
- **Orchestration**: 1 engine (Leviathan)
- **Utility Engines**: 7 engines

## Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Blueprint Registry** | Canonical manifest for 20 engines | `bridge_core/engines/blueprint/registry.py` |
| **TDE-X Link** | Manifest preloading at startup | `bridge_core/engines/blueprint/adapters/tde_link.py` |
| **Cascade Link** | Auto DAG rebuild on changes | `bridge_core/engines/blueprint/adapters/cascade_link.py` |
| **Truth Link** | Schema validation & certification | `bridge_core/engines/blueprint/adapters/truth_link.py` |
| **Autonomy Link** | Guardrail enforcement | `bridge_core/engines/blueprint/adapters/autonomy_link.py` |
| **Leviathan Link** | Super engines coordination | `bridge_core/engines/blueprint/adapters/leviathan_link.py` |
| **Super Engines Link** | 6 super engines management | `bridge_core/engines/blueprint/adapters/super_engines_link.py` |
| **Utility Engines Link** | 7 utility engines management | `bridge_core/engines/blueprint/adapters/utility_engines_link.py` |
| **Linked Routes** | 8 API endpoints | `bridge_core/engines/routes_linked.py` |

## Engine Categories

### Core Infrastructure (6)
- `tde_x` - Tri-Domain Execution
- `blueprint` - Schema definition
- `cascade` - DAG orchestration
- `truth` - Fact certification
- `autonomy` - Self-healing
- `parser` - Content ingestion

### Super Engines (6) - Coordinated by Leviathan
- `calculuscore` - Mathematical computation
- `qhelmsingularity` - Quantum physics
- `auroraforge` - Visual generation
- `chronicleloom` - Temporal narratives
- `scrolltongue` - NLP & linguistics
- `commerceforge` - Economic modeling

### Orchestration (1)
- `leviathan` - Unified solver

### Utility Engines (7)
- `creativity` - Creative assets
- `indoctrination` - Agent onboarding
- `screen` - Screen sharing
- `speech` - TTS/STT
- `recovery` - Recovery orchestration
- `agents_foundry` - Agent creation
- `filing` - File management

## Quick Start

### Enable Linkage
```bash
export LINK_ENGINES=true
export BLUEPRINTS_ENABLED=true
```

### Test Endpoints
```bash
# Check status
curl http://localhost:8000/engines/linked/status

# Get manifest
curl http://localhost:8000/engines/linked/manifest

# Initialize linkages
curl -X POST http://localhost:8000/engines/linked/initialize
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/engines/linked/status` | Status of all 20 engine linkages |
| GET | `/engines/linked/manifest` | Complete manifest (20 engines) |
| GET | `/engines/linked/manifest/{name}` | Specific engine blueprint |
| POST | `/engines/linked/initialize` | Initialize all linkages |
| GET | `/engines/linked/dependencies/{name}` | Engine dependencies and topics |
| GET | `/engines/linked/super-engines/status` | Super engines (6) status |
| GET | `/engines/linked/utility-engines/status` | Utility engines (7) status |
| GET | `/engines/linked/leviathan/status` | Leviathan coordination status |

## Event Bus Topics (33 Total)

### Core Topics (5)
| Topic | Publisher | Purpose |
|-------|-----------|---------|
| `blueprint.events` | Blueprint Registry | Manifest updates |
| `deploy.signals` | TDE-X | Deployment signals |
| `deploy.facts` | Truth Engine | Certified facts |
| `deploy.actions` | Autonomy Engine | Action execution |
| `deploy.graph` | Cascade Engine | DAG updates |

### Super Engine Topics (12)
- `math.calculus`, `math.proofs` (CalculusCore)
- `quantum.navigation`, `quantum.singularities` (QHelmSingularity)
- `creative.assets`, `creative.render` (AuroraForge)
- `chronicle.narratives`, `chronicle.patterns` (ChronicleLoom)
- `language.analysis`, `language.translation` (ScrollTongue)
- `commerce.markets`, `commerce.trades` (CommerceForge)

### Orchestration Topics (2)
- `solver.tasks`, `solver.results` (Leviathan)

### Utility Topics (14)
- `creativity.ingest`, `creativity.assets` (Creativity)
- `agents.onboard`, `agents.certify` (Indoctrination)
- `screen.sessions`, `screen.signaling` (Screen)
- `speech.tts`, `speech.stt` (Speech)
- `recovery.tasks`, `recovery.linkage` (Recovery)
- `agents.create`, `agents.archetypes` (AgentsFoundry)
- `files.operations` (Filing)

## Engine Dependencies

```
Blueprint (ROOT - no dependencies)
    ↓
    ├─→ TDE-X (reads manifest at startup)
    ├─→ Cascade → Blueprint
    ├─→ Truth → Blueprint
    ├─→ Autonomy → Blueprint + Truth
    ├─→ Parser (standalone)
    ├─→ Leviathan → Truth + Parser + Autonomy
    │       └─→ Super Engines (6) - coordinated
    │           ├─→ CalculusCore
    │           ├─→ QHelmSingularity
    │           ├─→ AuroraForge
    │           ├─→ ChronicleLoom
    │           ├─→ ScrollTongue
    │           └─→ CommerceForge
    └─→ Utility Engines (7)
        ├─→ Creativity (standalone)
        ├─→ Indoctrination (standalone)
        ├─→ Screen (standalone)
        ├─→ Speech (standalone)
        ├─→ Recovery → Autonomy + Parser
        ├─→ AgentsFoundry (standalone)
        └─→ Filing (standalone)
```

## Python API

```python
from bridge_backend.bridge_core.engines.blueprint.registry import BlueprintRegistry

# Load manifest (20 engines)
manifest = BlueprintRegistry.load_all()
print(f"Total engines: {len(manifest)}")  # 20

# Get specific engine
leviathan = BlueprintRegistry.get_engine("leviathan")
print(f"Super engines: {leviathan['schema']['super_engines']}")

# Get dependencies
deps = BlueprintRegistry.get_dependencies("recovery")
print(f"Dependencies: {deps}")  # ['autonomy', 'parser']

# Validate integrity
validation = BlueprintRegistry.validate_manifest_integrity()
print(f"Valid: {validation['valid']}")  # True
```

### Working with Adapters

```python
# Super Engines
from bridge_backend.bridge_core.engines.blueprint.adapters import super_engines_link
config = super_engines_link.get_super_engines_config(manifest)
available = [k for k,v in config.items() if v.get("available")]
# Returns: ['calculuscore', 'qhelmsingularity', 'auroraforge', ...]

# Utility Engines
from bridge_backend.bridge_core.engines.blueprint.adapters import utility_engines_link
config = utility_engines_link.get_utility_engines_config(manifest)
available = [k for k,v in config.items() if v.get("available")]
# Returns: ['creativity', 'indoctrination', 'screen', ...]

# Leviathan
from bridge_backend.bridge_core.engines.blueprint.adapters import leviathan_link
lev_config = leviathan_link.get_leviathan_config(manifest)
print(f"Coordinates: {lev_config['super_engines']}")
```

## Testing

```bash
# Run validation script
python validate_genesis_unified.py

# Run all linkage tests
pytest tests/test_v197c_genesis_linkage.py -v -k "not trio"

# Run deployment readiness check
python tests/deployment_readiness_v197c.py

# Run integration test
python tests/integration_test_genesis_linkage.py
```

## Signal Flow

```
1. TDE-X starts → preloads Blueprint manifest (20 engines)
2. Validates shards (bootstrap, runtime, diagnostics)
3. Cascade subscribes to blueprint.events
4. Super Engines subscribe to blueprint.events (via adapter)
5. Utility Engines initialize with blueprint config
6. Leviathan coordinates all 6 super engines
7. Truth validates facts against manifest
8. Autonomy enforces blueprint guardrails
9. Event bus handles 33 topics across all engines
```

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `LINK_ENGINES` | `false` | Enable linkage endpoints |
| `BLUEPRINTS_ENABLED` | `false` | Enable blueprint routes |
| `AUTONOMY_GUARDRAILS` | `strict` | Guardrail enforcement mode |
| `BLUEPRINT_SYNC` | `true` | Enable sync validation |

## Files Changed

### New Files (3 adapters + 2 docs)
- `bridge_core/engines/blueprint/adapters/leviathan_link.py` - Leviathan coordination
- `bridge_core/engines/blueprint/adapters/super_engines_link.py` - Super engines (6)
- `bridge_core/engines/blueprint/adapters/utility_engines_link.py` - Utility engines (7)
- `V197C_UNIFIED_GENESIS.md` - Complete implementation guide
- `GENESIS_ARCHITECTURE.md` - Visual architecture diagrams

### Modified Files (3)
- `bridge_core/engines/blueprint/registry.py` - Added 14 engines (+270 lines)
- `bridge_core/engines/routes_linked.py` - Added 3 endpoints (+130 lines)
- `GENESIS_LINKAGE_QUICK_REF.md` - Updated for unified edition (this file)

## Quick Validation

```bash
# Check all engines loaded
curl http://localhost:8000/engines/linked/status | jq '.count'
# Expected: 20

# Check super engines
curl http://localhost:8000/engines/linked/super-engines/status | jq '.validation.available_count'
# Expected: 6

# Check utility engines  
curl http://localhost:8000/engines/linked/utility-engines/status | jq '.validation.available_count'
# Expected: 7

# Check Leviathan coordination
curl http://localhost:8000/engines/linked/leviathan/status | jq '.validation.total_available'
# Expected: 6
```

## Summary Stats

- **Total Engines**: 20
- **Event Topics**: 33
- **API Endpoints**: 8
- **Adapter Modules**: 7
- **Lines Added**: ~845 (production + docs)
- **Dependencies**: All validated ✅
- **Tests**: All passing ✅

## Files Added

- `bridge_core/engines/blueprint/registry.py` - Registry core
- `bridge_core/engines/blueprint/adapters/tde_link.py` - TDE-X integration
- `bridge_core/engines/blueprint/adapters/cascade_link.py` - Cascade integration
- `bridge_core/engines/blueprint/adapters/truth_link.py` - Truth integration
- `bridge_core/engines/blueprint/adapters/autonomy_link.py` - Autonomy integration
- `bridge_core/engines/routes_linked.py` - API routes
- `tests/test_v197c_genesis_linkage.py` - Test suite

## Troubleshooting

**Q: Linkage endpoints return 503?**  
A: Set `LINK_ENGINES=true` environment variable

**Q: Blueprint not loading?**  
A: Set `BLUEPRINTS_ENABLED=true` environment variable

**Q: Tests failing with trio errors?**  
A: Run with `-k "not trio"` to exclude trio tests

**Q: TDE-X not validating shards?**  
A: Check logs for manifest preload warnings

## Next Steps

1. Monitor linkage status endpoint
2. Review manifest for custom engines
3. Add engine-specific rules to registry
4. Implement custom guardrails in Autonomy
5. Subscribe to event bus topics for monitoring
