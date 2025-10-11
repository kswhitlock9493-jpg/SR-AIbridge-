# v1.9.7c — Genesis Linkage Implementation Guide

## Overview

v1.9.7c "Genesis Linkage" unifies all deploy-critical engines (TDE-X, Cascade, Truth, Autonomy, Blueprint) into a single orchestration layer driven by the Blueprint Engine as the source of schema truth and design intent.

## Architecture

### Blueprint Registry
- **Location**: `bridge_backend/bridge_core/engines/blueprint/registry.py`
- **Purpose**: Canonical manifest describing every engine's structure, schema, and inter-engine relationships
- **Key Methods**:
  - `load_all()` - Load complete engine manifest
  - `get_engine(name)` - Get specific engine blueprint
  - `get_dependencies(name)` - Get engine dependencies
  - `validate_manifest_integrity()` - Validate all dependencies exist

### Engine Linkages

#### 1. Blueprint → TDE-X
- **Adapter**: `bridge_backend/bridge_core/engines/blueprint/adapters/tde_link.py`
- **Integration Point**: TDE-X orchestrator startup
- **Function**: 
  - `preload_manifest()` - Load Blueprint manifest at startup
  - `validate_shard(name, manifest)` - Validate shard exists in blueprint
- **Events Published**: `blueprint.events` with type `manifest.loaded`

#### 2. Blueprint → Cascade
- **Adapter**: `bridge_backend/bridge_core/engines/blueprint/adapters/cascade_link.py`
- **Integration Point**: Event bus subscription
- **Function**:
  - `subscribe_to_blueprint_updates()` - Subscribe to blueprint changes
  - `handle_blueprint_event(event)` - Handle blueprint update events
  - `rebuild_dag(event)` - Rebuild DAG when blueprint changes
- **Events Subscribed**: `blueprint.events`
- **Events Published**: `deploy.graph` with type `dag.rebuild`

#### 3. Blueprint → Truth
- **Adapter**: `bridge_backend/bridge_core/engines/blueprint/adapters/truth_link.py`
- **Integration Point**: Fact certification
- **Function**:
  - `validate_blueprint_sync(manifest, state)` - Check blueprint/state alignment
  - `certify_fact(fact, manifest)` - Certify facts against blueprint schema
- **Events Published**: `deploy.facts` with types `fact.blueprint.synced` or `fact.blueprint.drift`

#### 4. Blueprint → Autonomy
- **Adapter**: `bridge_backend/bridge_core/engines/blueprint/adapters/autonomy_link.py`
- **Integration Point**: Action execution
- **Function**:
  - `get_autonomy_rules(manifest)` - Extract guardrails from blueprint
  - `execute_action_with_guardrails(action, rules, facts)` - Execute safe actions
- **Events Published**: `deploy.actions` with type `action.executed`

## API Endpoints

All endpoints are prefixed with `/engines/linked` and gated by `LINK_ENGINES` environment variable.

### GET /engines/linked/status
Get status of all engine linkages.

**Response**:
```json
{
  "enabled": true,
  "engines": ["tde_x", "blueprint", "cascade", "truth", "autonomy", "parser"],
  "count": 6,
  "validation": {
    "valid": true,
    "errors": [],
    "engine_count": 6
  },
  "linkages": {
    "tde_x": "Blueprint → TDE-X manifest preloading",
    "cascade": "Blueprint → Cascade DAG auto-rebuild",
    "truth": "Blueprint → Truth schema validation",
    "autonomy": "Blueprint → Autonomy guardrails"
  }
}
```

### GET /engines/linked/manifest
Get complete Blueprint manifest with all engine definitions.

**Response**: Complete manifest object with all engines

### GET /engines/linked/manifest/{engine_name}
Get Blueprint manifest for a specific engine.

**Parameters**:
- `engine_name` - Name of the engine (e.g., `cascade`, `truth`, `autonomy`)

**Response**: Engine blueprint object

### POST /engines/linked/initialize
Initialize all engine linkages and event subscriptions.

**Response**:
```json
{
  "initialized": ["cascade"],
  "errors": [],
  "validation": {
    "valid": true,
    "errors": [],
    "engine_count": 6
  }
}
```

### GET /engines/linked/dependencies/{engine_name}
Get dependencies and topics for a specific engine.

**Parameters**:
- `engine_name` - Name of the engine

**Response**:
```json
{
  "engine": "cascade",
  "dependencies": ["blueprint"],
  "topics": ["deploy.graph", "blueprint.events:update"]
}
```

## Signal Flow

```
BlueprintRegistry.load_all()
        ↓
TDE-X bootstrap → runtime → diagnostics → emits deploy.signals
        ↓
Truth certifies facts → emits deploy.facts
        ↓
Cascade builds DAG from Blueprint + facts → enqueues jobs
        ↓
Autonomy reads Blueprint + facts → executes safe actions
        ↓
Federation/Netlify hydration on ready=true
```

## Event Bus Topics

- `blueprint.events` - Blueprint manifest changes and updates
- `deploy.signals` - TDE-X deployment signals
- `deploy.facts` - Truth-certified facts
- `deploy.actions` - Autonomy actions executed
- `deploy.graph` - Cascade DAG updates

## Configuration

### Environment Variables

#### Required
None - all linkages work with existing configuration.

#### Optional
- `LINK_ENGINES=true` - Enable Genesis Linkage API endpoints (default: false)
- `BLUEPRINTS_ENABLED=true` - Enable Blueprint Engine routes (default: false)
- `AUTONOMY_GUARDRAILS=strict` - Set autonomy guardrail mode (default: strict)
- `BLUEPRINT_SYNC=true` - Enable blueprint sync validation (default: true)

### Deployment Config (unchanged)

**Start Command**: 
```bash
python -m bridge_backend.run
```

**Health Check Path**: 
```
/health/live
```

## Benefits

✅ **Unified schema truth** — No route or model drift  
✅ **Engines become declarative** — Self-describing through blueprint  
✅ **TDE-X verifies design integrity** — Before deploy  
✅ **Cascade stays synchronized** — With real design, not stale code  
✅ **Truth certifies alignment** — Between declared and observed state  
✅ **Autonomy operates safely** — Within blueprint-defined guardrails  

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_v197c_genesis_linkage.py -v -k "not trio"
```

Tests cover:
- Blueprint registry loading and validation
- All four adapter linkages (TDE-X, Cascade, Truth, Autonomy)
- Event publishing and subscription
- Guardrail enforcement
- Fact certification
- DAG rebuilding

## Implementation Files

### New Files (10)
1. `bridge_backend/bridge_core/engines/blueprint/registry.py` - Blueprint Registry
2. `bridge_backend/bridge_core/engines/blueprint/adapters/__init__.py` - Adapters package
3. `bridge_backend/bridge_core/engines/blueprint/adapters/tde_link.py` - TDE-X adapter
4. `bridge_backend/bridge_core/engines/blueprint/adapters/cascade_link.py` - Cascade adapter
5. `bridge_backend/bridge_core/engines/blueprint/adapters/truth_link.py` - Truth adapter
6. `bridge_backend/bridge_core/engines/blueprint/adapters/autonomy_link.py` - Autonomy adapter
7. `bridge_backend/bridge_core/engines/routes_linked.py` - Linked engines API routes
8. `tests/test_v197c_genesis_linkage.py` - Comprehensive test suite

### Modified Files (2)
1. `bridge_backend/runtime/tde_x/orchestrator.py` - Added manifest preloading
2. `bridge_backend/main.py` - Added linked routes registration and version bump

## Usage Examples

### Check Linkage Status
```bash
curl http://localhost:8000/engines/linked/status
```

### Get Complete Manifest
```bash
curl http://localhost:8000/engines/linked/manifest
```

### Get Specific Engine Blueprint
```bash
curl http://localhost:8000/engines/linked/manifest/cascade
```

### Initialize Linkages
```bash
curl -X POST http://localhost:8000/engines/linked/initialize
```

### Get Engine Dependencies
```bash
curl http://localhost:8000/engines/linked/dependencies/autonomy
```

## Future Enhancements

- Dynamic manifest updates via API
- Schema versioning and migration
- Engine health monitoring via linkages
- Cross-engine transaction support
- Blueprint-driven auto-scaling policies
