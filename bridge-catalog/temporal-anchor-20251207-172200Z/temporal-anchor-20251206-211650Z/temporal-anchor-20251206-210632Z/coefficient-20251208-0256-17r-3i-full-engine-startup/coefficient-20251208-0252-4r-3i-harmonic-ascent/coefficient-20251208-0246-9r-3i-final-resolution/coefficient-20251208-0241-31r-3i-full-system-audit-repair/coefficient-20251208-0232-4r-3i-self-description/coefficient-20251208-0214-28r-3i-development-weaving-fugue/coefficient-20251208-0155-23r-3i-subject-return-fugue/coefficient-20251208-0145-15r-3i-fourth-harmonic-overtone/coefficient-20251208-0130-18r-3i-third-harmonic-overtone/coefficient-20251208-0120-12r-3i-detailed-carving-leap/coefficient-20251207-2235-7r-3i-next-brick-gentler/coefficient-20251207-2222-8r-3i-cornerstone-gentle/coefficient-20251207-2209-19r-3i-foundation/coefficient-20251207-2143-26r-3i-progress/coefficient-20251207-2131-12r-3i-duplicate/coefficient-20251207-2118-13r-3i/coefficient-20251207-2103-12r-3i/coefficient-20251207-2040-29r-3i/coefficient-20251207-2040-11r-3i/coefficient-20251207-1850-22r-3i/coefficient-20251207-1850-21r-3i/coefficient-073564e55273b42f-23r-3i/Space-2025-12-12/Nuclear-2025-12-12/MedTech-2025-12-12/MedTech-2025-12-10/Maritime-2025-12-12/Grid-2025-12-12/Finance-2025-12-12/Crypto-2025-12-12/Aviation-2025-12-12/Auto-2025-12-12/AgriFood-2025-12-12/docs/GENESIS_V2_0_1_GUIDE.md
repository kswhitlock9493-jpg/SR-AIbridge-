# Genesis v2.0.1 — Project Genesis: Universal Engine Assimilation

## Overview

Genesis v2.0.1 establishes a **Universal Engine Communication Contract** that unifies all engines, systems, and tools under a single, typed event bus with built-in safety, idempotency, and self-healing capabilities.

### What Genesis v2.0.1 Provides

1. **Genesis Core Contract (GCC)** - Typed event envelope with versioning
2. **Universal Adapters** - One-line publish/subscribe for all engines
3. **Guardians-First Safety** - Blocks recursion, destructive ops, violations
4. **Self-Healing** - Automatic health monitoring and repair
5. **Event Persistence** - Idempotency, dedupe, replay, DLQ
6. **TDE-X v2** - Resumable deployment stages (no more timeouts)

---

## Architecture

### 1. Genesis Core Contract (GCC)

Every event flowing through Genesis follows this contract:

```python
from bridge_backend.genesis.contracts import GenesisEvent

event = GenesisEvent(
    id="550e8400-e29b-41d4-a716-446655440000",        # Auto-generated UUID
    ts=datetime.utcnow(),                             # Auto-generated timestamp
    topic="engine.truth.fact.created",                # Topic namespace
    source="engine.truth",                            # Source identifier
    kind="fact",                                      # Event kind
    correlation_id="mission-42-analysis",             # Optional: links related events
    causation_id="550e8400-e29b-41d4-a716-446655440001",  # Optional: causal chain
    schema="genesis.event.v1",                        # Schema version
    payload={"subject": "mission/42", "claim": "jobs-indexed"},  # Event data
    dedupe_key="mission/42#jobs-indexed"              # Optional: idempotency key
)
```

#### Event Kinds

- **intent** - Intent propagation across engines
- **heal** - Repair requests and confirmations
- **fact** - Fact synchronization and certification
- **audit** - Security and compliance tracking
- **metric** - Performance and telemetry
- **control** - Deploy orchestration and config

#### Topic Namespace

Topics follow the pattern: `namespace.component.domain.verb`

- **engine.*** - Engine events (truth, cascade, autonomy, etc.)
- **system.*** - System events (guardians, captains, fleet, etc.)
- **runtime.*** - Runtime events (health, deploy, metrics)
- **security.*** - Security events (guardians blocking)
- **deploy.*** - Deployment events (TDE-X stages)

---

### 2. Universal Adapters

Publishing events is now a single function call:

```python
from bridge_backend.genesis.adapters import emit_intent, emit_heal, emit_fact

# Publish an intent
await emit_intent(
    topic="engine.truth.fact.created",
    source="engine.truth",
    payload={"subject": "mission/42", "claim": "jobs-indexed"},
    dedupe_key="mission/42#jobs-indexed"  # Optional: prevents duplicates
)

# Report degraded health
await emit_heal(
    topic="runtime.health.database.degraded",
    source="runtime.health",
    payload={"component": "database", "latency_ms": 500}
)

# Certify a fact
await emit_fact(
    topic="engine.truth.fact.certified",
    source="engine.truth",
    payload={"fact_id": "fact-123", "confidence": 0.98}
)
```

#### Convenience Helpers

```python
from bridge_backend.genesis.adapters import health_degraded, deploy_failed

# Report component health issue
await health_degraded("database", {"latency_ms": 500})

# Report deploy stage failure
await deploy_failed("warm_caches", {"error": "timeout", "attempt": 2})
```

---

### 3. Guardians-First Safety

Every event passes through the Guardians Gate before processing:

```python
from bridge_backend.bridge_core.guardians.gate import guardians_gate

# Guardians check event safety
allowed, reason = guardians_gate.allow(event)
if not allowed:
    # Event blocked and audit trail created
    logger.warning(f"Blocked: {reason}")
```

#### What Guardians Block

- **Destructive patterns** - `*.delete.all`, `*.destroy.*`, `*.purge.*`
- **Recursion loops** - Events triggering themselves repeatedly
- **Rate limit violations** - Too many events per topic per minute
- **Suspicious payloads** - SQL injection, script injection
- **Cross-namespace violations** - Unauthorized namespace access

#### Configuration

```bash
GUARDIANS_ENFORCE_STRICT=true     # Enforce strict checking
GUARDIANS_RATE_LIMIT=100          # Events per topic per minute
GUARDIANS_MAX_DEPTH=10            # Max recursion depth
```

---

### 4. Event Persistence & Replay

All events are persisted with idempotency and replay support:

```python
from bridge_backend.genesis.persistence import genesis_persistence
from bridge_backend.genesis.replay import genesis_replay

# Check if event is duplicate
is_dup = await genesis_persistence.is_duplicate("my-dedupe-key")

# Record event (with dedupe)
await genesis_persistence.record_event(
    event_id="event-123",
    topic="engine.truth.fact.created",
    source="engine.truth",
    kind="fact",
    payload={"test": "data"},
    dedupe_key="unique-key"  # Prevents duplicate processing
)

# Replay events from watermark
events = await genesis_replay.replay_from_watermark(
    watermark=100,
    topic_pattern="engine.truth%",
    limit=1000,
    emit=True  # Re-emit to bus
)
```

#### Replay CLI

```bash
# Replay from watermark
python -m bridge_backend.genesis.replay --from-watermark 100 --topic "engine.truth%"

# Replay from timestamp
python -m bridge_backend.genesis.replay --from-ts "2025-10-10T00:00:00Z"
```

#### Configuration

```bash
GENESIS_PERSIST_BACKEND=sqlite           # or postgres
GENESIS_DEDUP_TTL_SECS=86400            # 24 hours
GENESIS_DB_PATH=bridge_backend/.genesis/events.db
```

---

### 5. TDE-X v2 - Resumable Deployment

TDE-X v2 breaks deployment into resumable stages that don't block boot:

#### Stages

1. **post_boot** - Essential initialization (DB warming, health checks)
2. **warm_caches** - Cache preloading (protocols, agents, manifests)
3. **index_assets** - Asset indexing (docs, search, embeddings)
4. **scan_federation** - Federation discovery and sync

#### Usage

TDE-X v2 runs automatically on startup:

```python
from bridge_backend.runtime.tde_x.orchestrator_v2 import tde_orchestrator

# Get status
status = tde_orchestrator.get_status()
print(status["stages"])  # Shows stage status

# Stages run in background, emitting Genesis events:
# - deploy.tde.stage.started
# - deploy.tde.stage.completed
# - deploy.tde.stage.failed (triggers heal)
```

#### Configuration

```bash
TDE_V2_ENABLED=true                    # Enable TDE-X v2
TDE_MAX_STAGE_RUNTIME_SECS=900         # 15 minutes per stage
TDE_RESUME_ON_BOOT=true                # Resume incomplete stages
```

#### State Persistence

Stage progress is saved to `bridge_backend/.genesis/tde_state.json` and survives restarts.

---

## Deployment

### Render Configuration

**Start Command:**
```bash
uvicorn bridge_backend.main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
```bash
PORT=10000                              # Render sets automatically
GENESIS_MODE=enabled                    # Enable Genesis framework
TDE_V2_ENABLED=true                     # Enable TDE-X v2
GUARDIANS_ENFORCE_STRICT=true           # Strict safety checks
GENESIS_PERSIST_BACKEND=postgres        # Use Postgres for persistence
GENESIS_DEDUP_TTL_SECS=86400           # 24-hour dedup window
TDE_MAX_STAGE_RUNTIME_SECS=900         # 15-minute stage timeout
TDE_RESUME_ON_BOOT=true                # Resume on restart
```

### Port Binding

Genesis v2.0.1 fixes the Render port-scan loop:

- **No port scanning** - Reads `$PORT` exactly once
- **No loops** - Simple validation and fallback to 8000
- **Clean binding** - uvicorn binds directly to resolved port

```python
# In main.py
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("bridge_backend.main:app", host="0.0.0.0", port=port, reload=False)
```

---

## Engine Integration Examples

### Truth Engine

```python
from bridge_backend.genesis.adapters import emit_fact

# Certify a fact
await emit_fact(
    topic="engine.truth.fact.created",
    source="engine.truth",
    payload={
        "subject": "mission/42",
        "claim": "jobs-indexed",
        "confidence": 0.98
    },
    dedupe_key="mission/42#jobs-indexed"
)
```

### Autonomy Engine

```python
from bridge_backend.genesis.adapters import emit_intent

# Propose autonomous action
await emit_intent(
    topic="engine.autonomy.action.proposed",
    source="engine.autonomy",
    payload={
        "action": "fix_parity_issue",
        "target": "federation_sync",
        "rationale": "Detected state mismatch"
    }
)
```

### Cascade Engine

```python
from bridge_backend.genesis.adapters import emit_control

# Start workflow
await emit_control(
    topic="engine.cascade.flow.started",
    source="engine.cascade",
    payload={
        "flow_id": "workflow-123",
        "steps": ["step1", "step2", "step3"]
    },
    correlation_id="workflow-123"
)
```

---

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_genesis_v2_0_1.py -v
```

**Test Coverage:**
- ✅ Genesis contracts (3 tests)
- ✅ Genesis adapters (5 tests)
- ✅ Persistence & dedupe (5 tests)
- ✅ Guardians safety gate (4 tests)
- ✅ Event replay (2 tests)
- ✅ Port resolution (3 tests)
- ✅ TDE-X v2 orchestrator (3 tests)

**Total: 25 tests, all passing**

---

## Migration Guide

### From v1.9.x to v2.0.1

1. **Update render.yaml:**
   ```yaml
   startCommand: "uvicorn bridge_backend.main:app --host 0.0.0.0 --port $PORT"
   ```

2. **Set environment variables:**
   ```bash
   TDE_V2_ENABLED=true
   GUARDIANS_ENFORCE_STRICT=true
   ```

3. **Update engine code to use Genesis adapters:**
   ```python
   # Old way (still works)
   await genesis_bus.publish("topic", {"data": "value"})
   
   # New way (recommended)
   await emit_intent("topic", "source", {"data": "value"})
   ```

4. **No breaking changes** - All existing code continues to work.

---

## Troubleshooting

### Port Binding Issues

**Problem:** App not binding to correct port

**Solution:**
```bash
# Check PORT env var
echo $PORT

# Verify render.yaml start command
uvicorn bridge_backend.main:app --host 0.0.0.0 --port $PORT
```

### TDE-X Stage Failures

**Problem:** Stage timeout or failure

**Solution:**
```bash
# Check TDE-X state
cat bridge_backend/.genesis/tde_state.json

# Increase timeout
export TDE_MAX_STAGE_RUNTIME_SECS=1200  # 20 minutes

# Check Genesis events for heal messages
# Look for: deploy.tde.*.failed
```

### Guardians Blocking Events

**Problem:** Events being blocked unexpectedly

**Solution:**
```bash
# Check guardians stats
curl http://localhost:8000/guardians/stats

# Disable strict mode temporarily
export GUARDIANS_ENFORCE_STRICT=false

# Review blocked event audit trail
# Events are logged with security.guardians.action.blocked
```

---

## Success Metrics

✅ **Port binding** - App binds to correct port (8000 local, $PORT on Render)  
✅ **No port loops** - Single read of PORT env var, no scanning  
✅ **TDE-X v2** - Background stages, resumable, no deploy timeouts  
✅ **Genesis events** - All engines publish/subscribe via typed contract  
✅ **Guardians** - Safety checks block dangerous operations  
✅ **Persistence** - Events stored with idempotency and replay  
✅ **Tests** - 25/25 passing  
✅ **AsyncSession** - No FastAPI schema errors (already fixed in v1.9.6)  
✅ **Blueprint** - Optional engine with clear fallback  

---

## API Reference

### Genesis Adapters

```python
# Event emission
emit_intent(topic, source, payload, **kwargs) -> Optional[str]
emit_heal(topic, source, payload, **kwargs) -> Optional[str]
emit_fact(topic, source, payload, **kwargs) -> Optional[str]
emit_audit(topic, source, payload, **kwargs) -> Optional[str]
emit_metric(topic, source, payload, **kwargs) -> Optional[str]
emit_control(topic, source, payload, **kwargs) -> Optional[str]

# Convenience helpers
health_degraded(component, details) -> Optional[str]
deploy_failed(stage, details) -> Optional[str]
deploy_stage_started(stage, details=None) -> Optional[str]
deploy_stage_completed(stage, details=None) -> Optional[str]
```

### Genesis Persistence

```python
# Initialize
genesis_persistence.initialize() -> None

# Dedupe checking
genesis_persistence.is_duplicate(dedupe_key) -> bool

# Event recording
genesis_persistence.record_event(
    event_id, topic, source, kind, payload,
    dedupe_key=None, correlation_id=None, causation_id=None
) -> bool

# Event retrieval
genesis_persistence.get_events(
    topic_pattern=None, from_watermark=None,
    to_watermark=None, limit=100
) -> List[Dict]

# Watermark
genesis_persistence.get_watermark() -> int
```

### Genesis Replay

```python
# Replay from watermark
genesis_replay.replay_from_watermark(
    watermark, topic_pattern=None,
    limit=1000, emit=True
) -> List[Dict]

# Replay from timestamp
genesis_replay.replay_from_timestamp(
    from_ts, topic_pattern=None,
    limit=1000, emit=True
) -> List[Dict]

# Get current watermark
genesis_replay.get_current_watermark() -> int
```

### Guardians Gate

```python
# Check event safety
guardians_gate.allow(event) -> Tuple[bool, Optional[str]]

# Add bypass key for emergency ops
guardians_gate.add_bypass_key(key) -> None

# Get stats
guardians_gate.get_stats() -> Dict
```

### TDE-X v2 Orchestrator

```python
# Get status
tde_orchestrator.get_status() -> Dict

# Status includes:
# - stages: {stage_name: {status, started_at, completed_at, error}}
# - started_at, completed_at
# - resume_on_boot, max_stage_runtime_secs
```

---

## Support

For issues or questions:

1. Check logs for Genesis events: `grep "genesis" logs/*.log`
2. Review TDE-X state: `cat bridge_backend/.genesis/tde_state.json`
3. Run tests: `pytest tests/test_genesis_v2_0_1.py -v`
4. Open an issue with logs and state files

---

**Genesis v2.0.1** - Every engine speaks one contract, heals on its own, and never loops itself to death.
