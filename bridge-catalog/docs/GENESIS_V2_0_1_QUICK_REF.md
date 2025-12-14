# Genesis v2.0.1 Quick Reference

## Installation

```bash
# Environment variables
export GENESIS_MODE=enabled
export TDE_V2_ENABLED=true
export GUARDIANS_ENFORCE_STRICT=true
export PORT=8000  # Render sets this automatically
```

## Emit Events

```python
from bridge_backend.genesis.adapters import (
    emit_intent, emit_heal, emit_fact,
    health_degraded, deploy_failed
)

# Intent
await emit_intent("engine.truth.fact.created", "engine.truth", {"data": "value"})

# Heal
await emit_heal("runtime.health.degraded", "runtime.health", {"component": "db"})

# Fact
await emit_fact("engine.truth.fact.certified", "engine.truth", {"fact_id": "123"})

# Convenience
await health_degraded("database", {"latency_ms": 500})
await deploy_failed("warm_caches", {"error": "timeout"})
```

## Subscribe to Events

```python
from bridge_backend.genesis.bus import genesis_bus

async def my_handler(event):
    print(f"Received: {event['topic']}")

genesis_bus.subscribe("engine.truth.*", my_handler)
```

## Check Safety

```python
from bridge_backend.bridge_core.guardians.gate import guardians_gate

allowed, reason = guardians_gate.allow(event)
if not allowed:
    print(f"Blocked: {reason}")
```

## Replay Events

```bash
# From watermark
python -m bridge_backend.genesis.replay --from-watermark 100

# From timestamp
python -m bridge_backend.genesis.replay --from-ts "2025-10-10T00:00:00Z"

# With topic filter
python -m bridge_backend.genesis.replay --from-watermark 0 --topic "engine.truth%"
```

## TDE-X v2 Status

```python
from bridge_backend.runtime.tde_x.orchestrator_v2 import tde_orchestrator

status = tde_orchestrator.get_status()
print(f"Stages: {status['stages']}")
```

## Topic Patterns

- `engine.<name>.<domain>.<verb>` - Engine events
- `system.<name>.<domain>.<verb>` - System events
- `runtime.<name>.<domain>.<verb>` - Runtime events
- `security.guardians.action.blocked` - Blocked actions
- `deploy.tde.stage.*` - Deploy stages

## Event Kinds

- `intent` - Cross-engine actions
- `heal` - Self-repair requests
- `fact` - Certified truths
- `audit` - Security tracking
- `metric` - Telemetry
- `control` - Deploy/config

## Configuration

```bash
# Genesis
GENESIS_MODE=enabled
GENESIS_PERSIST_BACKEND=sqlite  # or postgres
GENESIS_DEDUP_TTL_SECS=86400

# Guardians
GUARDIANS_ENFORCE_STRICT=true
GUARDIANS_RATE_LIMIT=100
GUARDIANS_MAX_DEPTH=10

# TDE-X v2
TDE_V2_ENABLED=true
TDE_MAX_STAGE_RUNTIME_SECS=900
TDE_RESUME_ON_BOOT=true

# Port
PORT=8000  # Render overrides
```

## Run Tests

```bash
pytest tests/test_genesis_v2_0_1.py -v
```

## Troubleshooting

**Port issues:**
```bash
echo $PORT
uvicorn bridge_backend.main:app --host 0.0.0.0 --port $PORT
```

**TDE-X failures:**
```bash
cat bridge_backend/.genesis/tde_state.json
export TDE_MAX_STAGE_RUNTIME_SECS=1200
```

**Guardians blocking:**
```bash
export GUARDIANS_ENFORCE_STRICT=false
curl http://localhost:8000/guardians/stats
```

## API Endpoints

- `GET /health` - Health status
- `GET /api/routes` - List routes
- `GET /api/version` - Version info

## Render Deploy

**render.yaml:**
```yaml
startCommand: "uvicorn bridge_backend.main:app --host 0.0.0.0 --port $PORT"
```

**Health Check:**
```yaml
healthCheckPath: /health/live
```
