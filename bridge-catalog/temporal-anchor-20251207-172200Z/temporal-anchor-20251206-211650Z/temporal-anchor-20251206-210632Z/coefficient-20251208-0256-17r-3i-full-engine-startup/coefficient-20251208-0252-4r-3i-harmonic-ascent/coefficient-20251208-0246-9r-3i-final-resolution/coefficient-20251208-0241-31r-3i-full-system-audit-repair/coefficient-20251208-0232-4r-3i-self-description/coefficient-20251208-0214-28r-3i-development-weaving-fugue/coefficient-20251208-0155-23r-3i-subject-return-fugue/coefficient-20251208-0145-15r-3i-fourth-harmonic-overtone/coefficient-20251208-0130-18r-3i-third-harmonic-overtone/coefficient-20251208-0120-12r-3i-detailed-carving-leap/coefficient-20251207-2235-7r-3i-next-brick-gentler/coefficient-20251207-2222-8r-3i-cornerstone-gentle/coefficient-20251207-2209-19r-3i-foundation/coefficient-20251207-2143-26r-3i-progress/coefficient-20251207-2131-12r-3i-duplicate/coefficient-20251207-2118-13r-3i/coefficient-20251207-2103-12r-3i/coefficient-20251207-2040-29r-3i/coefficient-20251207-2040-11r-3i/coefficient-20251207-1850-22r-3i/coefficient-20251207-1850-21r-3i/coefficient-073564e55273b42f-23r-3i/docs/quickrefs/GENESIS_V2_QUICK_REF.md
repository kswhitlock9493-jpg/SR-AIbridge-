# Genesis v2.0.0 Quick Reference

## What is Genesis?

**Genesis** = Universal engine integration framework that unifies all 15+ SR-AIbridge engines into a single living digital organism.

## Quick Start

### Enable Genesis (Default: Enabled)
```bash
export GENESIS_MODE=enabled
export GENESIS_HEARTBEAT_INTERVAL=15
```

### Check Genesis Pulse
```bash
curl http://localhost:8000/api/genesis/pulse
```

### View System Map
```bash
curl http://localhost:8000/api/genesis/map
```

---

## Genesis Event Topics

| Topic | Purpose | Publishers | Subscribers |
|-------|---------|------------|-------------|
| `genesis.intent` | Intent propagation | TDE-X, Cascade, Parser, Fleet, Console | All engines |
| `genesis.fact` | Fact certification | Truth, Custody | Autonomy, Cascade |
| `genesis.heal` | Repair & healing | Autonomy, Recovery | Guardians |
| `genesis.create` | Generative output | Leviathan, Creativity | - |
| `genesis.echo` | System introspection | Orchestrator | - |

---

## Key Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/genesis/pulse` | Heartbeat & health status |
| `GET /api/genesis/manifest` | Complete engine manifest |
| `GET /api/genesis/health` | Detailed health report |
| `GET /api/genesis/echo` | Introspection report |
| `GET /api/genesis/map` | System topology |
| `GET /api/genesis/events` | Event history |
| `GET /api/genesis/stats` | Bus statistics |

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `GENESIS_MODE` | `enabled` | Enable/disable Genesis |
| `GENESIS_STRICT_POLICY` | `true` | Strict topic validation |
| `GENESIS_HEARTBEAT_INTERVAL` | `15` | Heartbeat interval (sec) |
| `GENESIS_MAX_CROSSSIGNAL` | `1024` | Max event history |
| `GENESIS_TRACE_LEVEL` | `2` | Logging verbosity (0-3) |

---

## Engine Roles

| Engine | Role | Component Type |
|--------|------|----------------|
| Blueprint | DNA | Core |
| TDE-X | Heart | Core |
| Cascade | Nervous System | Core |
| Truth | Immune System | Core |
| Autonomy | Reflex Arc | Core |
| Leviathan | Cerebral Cortex | Compute |
| Creativity | Imagination | Generative |
| Parser/Speech | Language Center | Interface |
| Fleet/Custody/Console | Operational Limbs | Operations |
| Captains/Guardians | Immune Guardians | Protection |
| Recovery | Repair Mechanism | Healing |

---

## Python API

### Publishing Events
```python
from bridge_backend.genesis.bus import genesis_bus

await genesis_bus.publish("genesis.intent", {
    "type": "my.event",
    "data": "value"
})
```

### Subscribing to Events
```python
from bridge_backend.genesis.bus import genesis_bus

genesis_bus.subscribe("genesis.fact", lambda e: print(e))
```

### Registering Engines
```python
from bridge_backend.genesis.manifest import genesis_manifest

genesis_manifest.register_engine("my_engine", {
    "genesis_role": "My component",
    "topics": ["genesis.intent"],
    "dependencies": []
})
```

### Health Updates
```python
from bridge_backend.genesis.introspection import genesis_introspection

genesis_introspection.update_health("my_engine", True)
health = genesis_introspection.get_health_status()
```

---

## Testing

```bash
# Run Genesis tests
pytest tests/test_v200_genesis.py -v

# Run specific test
pytest tests/test_v200_genesis.py::TestGenesisEventBus -v

# Run with coverage
pytest tests/test_v200_genesis.py --cov=bridge_backend.genesis
```

---

## Signal Flow

```
TDE-X (Heart) → genesis.intent → Cascade (Nervous System)
                                        ↓
Truth (Immune) → genesis.fact → Autonomy (Reflex Arc)
                                        ↓
                              genesis.heal
                                        ↓
                           Guardians (validate)
                                        ↓
                           Recovery (execute)
                                        ↓
                              genesis.echo
                                        ↓
                          Introspection (report)
```

---

## Health Check Response

```json
{
  "ok": true,
  "pulse": "alive",
  "health": {
    "overall_healthy": true,
    "components": {
      "tde_x": true,
      "cascade": true,
      "truth": true,
      "autonomy": true
    },
    "healthy_count": 15,
    "total_count": 15,
    "health_percentage": 100.0
  }
}
```

---

## Troubleshooting

### Genesis Not Starting
```bash
# Check mode
echo $GENESIS_MODE

# Enable explicitly
export GENESIS_MODE=enabled
```

### Missing Engines
```bash
# Check manifest
curl http://localhost:8000/api/genesis/manifest

# Check health
curl http://localhost:8000/api/genesis/health
```

### Debug Events
```bash
# Set high trace level
export GENESIS_TRACE_LEVEL=3

# Check event history
curl http://localhost:8000/api/genesis/events?limit=50
```

---

## Key Features

✅ **15+ Engines Unified** - All engines communicate via Genesis bus  
✅ **Self-Healing** - Autonomy + Recovery work automatically  
✅ **Real-Time Health** - Continuous health monitoring  
✅ **Event Tracing** - Full event history and replay  
✅ **Introspection** - Complete system visibility  
✅ **Backward Compatible** - Works with v1.9.7c linkage  

---

## Files Added

```
bridge_backend/genesis/
  __init__.py           # Genesis framework exports
  bus.py                # Event multiplexer
  manifest.py           # Engine registry
  introspection.py      # Telemetry & health
  orchestration.py      # Coordination loop
  routes.py             # API endpoints

bridge_backend/bridge_core/engines/adapters/
  __init__.py           # Adapter exports
  genesis_link.py       # Engine linkage

tests/
  test_v200_genesis.py  # Test suite
```

---

## Deployment

### Render
1. Set `GENESIS_MODE=enabled` in environment
2. Deploy as normal
3. Monitor via `/api/genesis/pulse`

### Local Development
```bash
export GENESIS_MODE=enabled
python -m bridge_backend.run
```

---

## Related Docs

- [GENESIS_V2_GUIDE.md](./GENESIS_V2_GUIDE.md) - Complete guide
- [GENESIS_LINKAGE_GUIDE.md](./GENESIS_LINKAGE_GUIDE.md) - v1.9.7c guide

---

**Genesis v2.0.0 - One Organism, Infinite Possibilities** 🌌
