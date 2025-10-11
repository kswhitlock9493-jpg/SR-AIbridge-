# Genesis Linkage Quick Reference

## v1.9.7c Feature Summary

Unifies TDE-X, Cascade, Truth, Autonomy, and Blueprint engines via Blueprint Registry as source of truth.

## Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Blueprint Registry** | Canonical engine manifest | `bridge_core/engines/blueprint/registry.py` |
| **TDE-X Link** | Manifest preloading at startup | `bridge_core/engines/blueprint/adapters/tde_link.py` |
| **Cascade Link** | Auto DAG rebuild on changes | `bridge_core/engines/blueprint/adapters/cascade_link.py` |
| **Truth Link** | Schema validation & certification | `bridge_core/engines/blueprint/adapters/truth_link.py` |
| **Autonomy Link** | Guardrail enforcement | `bridge_core/engines/blueprint/adapters/autonomy_link.py` |
| **Linked Routes** | API endpoints | `bridge_core/engines/routes_linked.py` |

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
| GET | `/engines/linked/status` | Linkage status and validation |
| GET | `/engines/linked/manifest` | Complete engine manifest |
| GET | `/engines/linked/manifest/{name}` | Specific engine blueprint |
| POST | `/engines/linked/initialize` | Initialize all linkages |
| GET | `/engines/linked/dependencies/{name}` | Engine dependencies and topics |

## Event Bus Topics

| Topic | Publisher | Purpose |
|-------|-----------|---------|
| `blueprint.events` | Blueprint Registry | Manifest updates |
| `deploy.signals` | TDE-X | Deployment signals |
| `deploy.facts` | Truth Engine | Certified facts |
| `deploy.actions` | Autonomy Engine | Action execution |
| `deploy.graph` | Cascade Engine | DAG updates |

## Engine Dependencies

```
Blueprint (no deps)
    ↓
TDE-X → reads Blueprint manifest
    ↓
Cascade → depends on Blueprint
    ↓
Truth → depends on Blueprint
    ↓
Autonomy → depends on Blueprint + Truth
```

## Python API

```python
from bridge_backend.bridge_core.engines.blueprint.registry import BlueprintRegistry

# Load manifest
manifest = BlueprintRegistry.load_all()

# Get specific engine
cascade = BlueprintRegistry.get_engine("cascade")

# Get dependencies
deps = BlueprintRegistry.get_dependencies("autonomy")

# Validate integrity
validation = BlueprintRegistry.validate_manifest_integrity()
```

## Testing

```bash
# Run all linkage tests
pytest tests/test_v197c_genesis_linkage.py -v -k "not trio"

# Run specific test
pytest tests/test_v197c_genesis_linkage.py::test_blueprint_registry_load_all -v
```

## Signal Flow

```
1. TDE-X starts → preloads Blueprint manifest
2. Validates shards (bootstrap, runtime, diagnostics)
3. Cascade subscribes to blueprint.events
4. Truth validates facts against manifest
5. Autonomy enforces blueprint guardrails
```

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `LINK_ENGINES` | `false` | Enable linkage endpoints |
| `BLUEPRINTS_ENABLED` | `false` | Enable blueprint routes |
| `AUTONOMY_GUARDRAILS` | `strict` | Guardrail enforcement mode |
| `BLUEPRINT_SYNC` | `true` | Enable sync validation |

## Files Modified

- `bridge_backend/runtime/tde_x/orchestrator.py` - Added manifest preloading
- `bridge_backend/main.py` - Added linked routes, version bump to 1.9.7c

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
