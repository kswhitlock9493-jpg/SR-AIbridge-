# v2.0.0 — Project Genesis: Universal Engine Integration

## Overview

**Project Genesis** establishes SR-AIbridge as a **living computational organism** — a unified architecture where every engine becomes a node in a fully synchronized network capable of perceiving, reasoning, repairing, and evolving in real time.

Genesis v2.0.0 integrates **15+ engines** under a single orchestration framework, transforming the bridge from a collection of components into a cohesive digital organism.

---

## Core Architecture

### The Genesis Framework Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Genesis Bus** | Central event multiplexer - nervous system | `bridge_backend/genesis/bus.py` |
| **Genesis Manifest** | Universal engine registry - DNA | `bridge_backend/genesis/manifest.py` |
| **Genesis Introspection** | Telemetry and self-mapping | `bridge_backend/genesis/introspection.py` |
| **Genesis Orchestrator** | Core coordination loop | `bridge_backend/genesis/orchestration.py` |
| **Genesis Link Adapters** | Engine connections | `bridge_backend/bridge_core/engines/adapters/genesis_link.py` |
| **Genesis API Routes** | Health checks and introspection | `bridge_backend/genesis/routes.py` |

---

## Genesis Organism Roles

Each engine serves a specific role in the Genesis organism:

| Engine | Genesis Role | Function |
|--------|--------------|----------|
| **Blueprint** | DNA of the Bridge | Defines structure, schema, and doctrine |
| **TDE-X** | Heart | Pulse of operations (deploy & environment lifecycles) |
| **Cascade** | Nervous System | Manages post-deploy flows & DAGs |
| **Truth** | Immune System | Certifies facts & runtime integrity |
| **Autonomy** | Reflex Arc | Executes self-healing & optimization |
| **Leviathan** | Cerebral Cortex | Large-scale distributed inference |
| **Creativity** | Imagination | Generative logic & UX narrative |
| **Parser** | Language Center | Communication interface |
| **Speech** | Language Center | Speech synthesis & comprehension |
| **Fleet** | Operational Limbs | Agent management |
| **Custody** | Operational Limbs | Storage & state management |
| **Console** | Operational Limbs | Command routing |
| **Captains** | Immune Guardians | Policy layer |
| **Guardians** | Immune Guardians | Protection layer |
| **Recovery** | Repair Mechanism | System restoration |

---

## Genesis Event Topics

The Genesis Event Bus uses five core topics for cross-engine communication:

### 1. `genesis.intent`
**Purpose**: Intent propagation across engines

**Publishers**: TDE-X, Cascade, Parser, Speech, Fleet, Console, Captains

**Use Cases**:
- Deployment signals from TDE-X
- DAG updates from Cascade
- User commands from Console
- Policy changes from Captains

### 2. `genesis.fact`
**Purpose**: Fact synchronization and certification

**Publishers**: Truth, Custody

**Use Cases**:
- Certified facts from Truth Engine
- State snapshots from Custody
- Runtime integrity checks

### 3. `genesis.heal`
**Purpose**: Repair requests and confirmations

**Publishers**: Autonomy, Recovery

**Subscribers**: Guardians (validates heal actions)

**Use Cases**:
- Self-healing actions from Autonomy
- Recovery job outcomes
- Health degradation alerts

### 4. `genesis.create`
**Purpose**: Emergent build and synthesis

**Publishers**: Leviathan, Creativity

**Use Cases**:
- Distributed inference results from Leviathan
- Creative generation outputs from Creativity
- Emergent pattern synthesis

### 5. `genesis.echo`
**Purpose**: Introspective telemetry for the entire organism

**Publisher**: Genesis Orchestrator

**Use Cases**:
- System-wide health reports
- Heartbeat pulses
- Introspection data

---

## Environment Variables

Configure Genesis behavior with these environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `GENESIS_MODE` | `enabled` | Enable/disable Genesis framework |
| `GENESIS_STRICT_POLICY` | `true` | Enforce strict topic validation |
| `GENESIS_HEARTBEAT_INTERVAL` | `15` | Heartbeat interval in seconds |
| `GENESIS_MAX_CROSSSIGNAL` | `1024` | Maximum event history size |
| `GENESIS_TRACE_LEVEL` | `2` | Logging verbosity (0-3) |

### Trace Levels
- **0**: No tracing
- **1**: Topic validation warnings only
- **2**: Event publications logged (default)
- **3**: Full debug with exception traces

---

## API Endpoints

All Genesis endpoints are prefixed with `/api/genesis`:

### `GET /api/genesis/pulse`
Genesis heartbeat - returns current health and pulse status

**Response**:
```json
{
  "ok": true,
  "pulse": "alive",
  "health": {
    "overall_healthy": true,
    "healthy_count": 15,
    "total_count": 15,
    "health_percentage": 100.0
  },
  "heartbeat": {
    "last_heartbeat": "2025-10-11T05:50:00Z",
    "interval_seconds": 15
  },
  "orchestrator": {
    "running": true,
    "enabled": true
  }
}
```

### `GET /api/genesis/manifest`
Get complete unified manifest of all engines

### `GET /api/genesis/manifest/{engine_name}`
Get manifest for a specific engine (e.g., `/api/genesis/manifest/cascade`)

### `GET /api/genesis/health`
Detailed health status of all Genesis components

### `GET /api/genesis/echo`
Comprehensive introspection report (echo)

### `GET /api/genesis/map`
System topology map showing all engines and relationships

### `GET /api/genesis/events?limit=100`
Recent event history from Genesis bus

### `GET /api/genesis/stats`
Genesis bus statistics and metrics

---

## Signal Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Genesis Organism                        │
│                                                             │
│  ┌──────────────┐     genesis.intent      ┌──────────────┐│
│  │   TDE-X      │─────────────────────────▶│   Cascade    ││
│  │   (Heart)    │                          │  (Nervous)   ││
│  └──────────────┘                          └──────────────┘│
│         │                                         │         │
│         │                                         │         │
│         ▼ genesis.intent                         ▼         │
│  ┌──────────────┐     genesis.fact       ┌──────────────┐│
│  │   Truth      │─────────────────────────▶│  Autonomy    ││
│  │  (Immune)    │                          │  (Reflex)    ││
│  └──────────────┘                          └──────────────┘│
│         │                                         │         │
│         │                                         │         │
│         ▼                                         ▼         │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         Genesis Orchestrator (Coordination)          │ │
│  └──────────────────────────────────────────────────────┘ │
│                            │                               │
│                            ▼ genesis.echo                  │
│                  ┌──────────────────┐                      │
│                  │  Introspection   │                      │
│                  │  & Telemetry     │                      │
│                  └──────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Initialization Sequence

Genesis bootstraps automatically on application startup:

1. **Genesis Bus Initialization**: Event multiplexer starts
2. **Manifest Sync**: Synchronizes with Blueprint Registry
3. **Engine Link Registration**: All engines connect to Genesis bus
4. **Health Checks**: Initial health status recorded for each engine
5. **Orchestrator Start**: Main coordination loop begins
6. **Heartbeat Pulse**: Regular heartbeat every 15 seconds (configurable)

---

## Usage Examples

### Publishing Events

```python
from bridge_backend.genesis.bus import genesis_bus

# Publish an intent event
await genesis_bus.publish("genesis.intent", {
    "type": "deploy.signal",
    "source": "tde_x",
    "shard": "bootstrap"
})

# Publish a fact
await genesis_bus.publish("genesis.fact", {
    "type": "truth.certified",
    "fact": {"deployment": "ready"},
    "certified": True
})
```

### Subscribing to Events

```python
from bridge_backend.genesis.bus import genesis_bus

# Subscribe to intent events
def handle_intent(event):
    print(f"Received intent: {event['type']}")

genesis_bus.subscribe("genesis.intent", handle_intent)
```

### Registering Engines

```python
from bridge_backend.genesis.manifest import genesis_manifest

# Register a custom engine
genesis_manifest.register_engine("my_engine", {
    "genesis_role": "Custom processor",
    "description": "My custom engine",
    "topics": ["genesis.create"],
    "dependencies": ["blueprint"]
})
```

### Health Monitoring

```python
from bridge_backend.genesis.introspection import genesis_introspection

# Update health status
genesis_introspection.update_health("my_engine", True)

# Get overall health
health = genesis_introspection.get_health_status()
print(f"System health: {health['health_percentage']}%")
```

---

## Backward Compatibility

Genesis maintains **full backward compatibility** with v1.9.7c Genesis Linkage:

- All existing Blueprint Registry functions work unchanged
- Legacy event topics (`blueprint.events`, `deploy.signals`, etc.) are supported
- Existing engine adapters continue to function
- TDE-X, Cascade, Truth, and Autonomy linkages preserved

Genesis **extends** rather than replaces the existing linkage system.

---

## Migration from v1.9.7c

### For Users
No action required - Genesis is enabled by default and maintains compatibility.

### For Developers

**Old Way (v1.9.7c)**:
```python
from bridge_backend.bridge_core.engines.blueprint.registry import BlueprintRegistry
manifest = BlueprintRegistry.load_all()
```

**New Way (v2.0.0 - Recommended)**:
```python
from bridge_backend.genesis.manifest import genesis_manifest
manifest = genesis_manifest.get_manifest()
```

Both approaches work and return compatible data.

---

## Testing

Run Genesis test suite:

```bash
pytest tests/test_v200_genesis.py -v
```

Test coverage:
- ✅ Genesis Event Bus (publish/subscribe, history, stats)
- ✅ Genesis Manifest (registration, dependencies, validation)
- ✅ Genesis Introspection (health, metrics, heartbeat)
- ✅ Genesis Orchestrator (start/stop, action execution)
- ✅ Integration tests (cross-engine communication)

---

## Deployment

### Render

Genesis works seamlessly with Render deployment:

1. Set environment variables in Render dashboard
2. Deploy as normal - Genesis bootstraps automatically
3. Monitor via `/api/genesis/pulse` endpoint

### Netlify

For frontend integration:

1. Frontend can query `/api/genesis/health` for status
2. Use `/api/genesis/map` to discover available engines
3. Subscribe to events via WebSocket (future enhancement)

---

## Troubleshooting

### Genesis Not Starting

**Issue**: Genesis framework not initializing

**Solution**: Check `GENESIS_MODE` environment variable
```bash
export GENESIS_MODE=enabled
```

### Missing Engine Links

**Issue**: Some engines not appearing in manifest

**Solution**: Check engine health status
```bash
curl http://localhost:8000/api/genesis/health
```

### Event Not Publishing

**Issue**: Events not being received by subscribers

**Solution**: 
1. Verify `GENESIS_STRICT_POLICY` allows your topic
2. Check trace level: `export GENESIS_TRACE_LEVEL=3`
3. Review logs for validation warnings

---

## Future Enhancements

Planned for future releases:

- **WebSocket Support**: Real-time event streaming to frontends
- **Distributed Genesis**: Multi-instance coordination
- **AI-Driven Optimization**: Self-learning orchestration
- **Visual System Map**: Interactive topology visualization
- **Event Replay**: Time-travel debugging for events
- **Smart Routing**: Intelligent event routing based on load

---

## Summary

**Genesis v2.0.0** transforms SR-AIbridge into a unified digital organism where:

✅ **All 15+ engines** communicate via a central nervous system  
✅ **Self-healing** occurs automatically through Autonomy + Recovery  
✅ **Full introspection** available via echo reports and health checks  
✅ **Backward compatible** with v1.9.7c Genesis Linkage  
✅ **Production ready** for Render + Netlify deployment  

The organism is **alive**, **self-aware**, and **continuously evolving**.

---

## Related Documentation

- [GENESIS_LINKAGE_GUIDE.md](./GENESIS_LINKAGE_GUIDE.md) - v1.9.7c implementation
- [GENESIS_LINKAGE_QUICK_REF.md](./GENESIS_LINKAGE_QUICK_REF.md) - Quick reference
- [BLUEPRINT_ENGINE_GUIDE.md](./BLUEPRINT_ENGINE_GUIDE.md) - Blueprint Engine details
- [TDE_X_DEPLOYMENT_GUIDE.md](./TDE_X_DEPLOYMENT_GUIDE.md) - TDE-X orchestration

---

**Genesis is the future of SR-AIbridge — a single, unified organism.**
