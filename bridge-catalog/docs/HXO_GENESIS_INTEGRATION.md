# HXO Genesis Integration — Event Bus Topics

**Version:** v1.9.6p  
**Purpose:** Complete Genesis Bus integration reference

---

## Overview

HXO registers 11 new topics on the Genesis event bus for coordinated orchestration across all engines.

---

## Core HXO Topics

### `hxo.link.autonomy`

**Publisher:** Autonomy Engine  
**Subscriber:** HXO Core  
**Purpose:** Self-healing and adaptive orchestration signals

**Event Schema:**
```json
{
  "type": "heal.trigger",
  "plan_id": "string",
  "reason": "shard_failure|timeout|resource_exhaustion",
  "suggested_action": "retry|split|abort",
  "timestamp": "ISO8601"
}
```

**Use Cases:**
- Failed shard auto-retry
- Dynamic concurrency adjustment
- Predictive scaling

---

### `hxo.link.blueprint`

**Publisher:** Blueprint Engine  
**Subscriber:** HXO Core  
**Purpose:** Schema validation and structural integrity

**Event Schema:**
```json
{
  "type": "schema.validate",
  "plan_id": "string",
  "schema_valid": true,
  "mutations": [],
  "timestamp": "ISO8601"
}
```

**Use Cases:**
- Pre-execution plan validation
- Zero-downtime schema migrations
- Structural correctness guarantees

---

### `hxo.link.truth`

**Publisher:** Truth Engine  
**Subscriber:** HXO Core  
**Purpose:** Cryptographic certification and consensus

**Event Schema:**
```json
{
  "type": "certification.complete",
  "plan_id": "string",
  "merkle_root": "string",
  "certified": true,
  "signature": "string",
  "timestamp": "ISO8601"
}
```

**Use Cases:**
- Merkle tree root certification
- Harmonic consensus validation
- Audit trail generation

---

### `hxo.link.cascade`

**Publisher:** Cascade Engine  
**Subscriber:** HXO Core  
**Purpose:** Post-event orchestration and continuous deployment

**Event Schema:**
```json
{
  "type": "deploy.trigger",
  "deployment_id": "string",
  "stages": ["build", "test", "deploy"],
  "strategy": "progressive|blue-green|canary",
  "timestamp": "ISO8601"
}
```

**Use Cases:**
- Continuous deployment pipeline orchestration
- Progressive rollout
- Zero-downtime deployments

---

### `hxo.link.federation`

**Publisher:** Federation Engine  
**Subscriber:** HXO Core  
**Purpose:** Distributed control mesh coordination

**Event Schema:**
```json
{
  "type": "queue.ready",
  "queue_id": "string",
  "capacity": 1000,
  "current_load": 250,
  "timestamp": "ISO8601"
}
```

**Use Cases:**
- Multi-node shard distribution
- Federated execution
- Load balancing

---

### `hxo.link.parser`

**Publisher:** Parser Engine  
**Subscriber:** HXO Core  
**Purpose:** Plan parsing and linguistic interpretation

**Event Schema:**
```json
{
  "type": "plan.parsed",
  "plan_id": "string",
  "stages": [],
  "dependencies": {},
  "timestamp": "ISO8601"
}
```

**Use Cases:**
- Natural language to execution plan conversion
- Dynamic plan adjustment
- Intent-driven orchestration

---

### `hxo.link.leviathan`

**Publisher:** Leviathan Engine  
**Subscriber:** HXO Core  
**Purpose:** Predictive orchestration and load forecasting

**Event Schema:**
```json
{
  "type": "forecast.ready",
  "prediction_window_ms": 500,
  "predicted_load": {
    "cpu": 0.75,
    "memory": 0.60,
    "queue_depth": 120
  },
  "recommendations": [],
  "timestamp": "ISO8601"
}
```

**Use Cases:**
- Predictive shard allocation
- Pre-emptive resource scaling
- Genesis Bus traffic simulation

---

### `hxo.telemetry.metrics`

**Publisher:** HXO Core  
**Subscriber:** ARIE, Leviathan, Autonomy  
**Purpose:** Cross-federation telemetry streaming

**Event Schema:**
```json
{
  "type": "metrics.snapshot",
  "active_plans": 5,
  "active_shards": 120,
  "completed_shards": 1850,
  "failed_shards": 12,
  "avg_shard_latency_ms": 245,
  "p95_shard_latency_ms": 780,
  "timestamp": "ISO8601"
}
```

**Frequency:** Every 1 second  
**Retention:** Last 10,000 events (TERC)

---

### `hxo.heal.trigger`

**Publisher:** HXO Core, Autonomy Engine  
**Subscriber:** HXO Core, Autonomy Engine  
**Purpose:** Healing coordination

**Event Schema:**
```json
{
  "type": "heal.trigger",
  "plan_id": "string",
  "shard_id": "string",
  "failure_reason": "timeout|error|resource",
  "heal_depth": 2,
  "max_depth": 5,
  "timestamp": "ISO8601"
}
```

**Safety:** Guardian monitors heal depth to prevent recursion

---

### `hxo.heal.complete`

**Publisher:** HXO Core  
**Subscriber:** Autonomy Engine, ARIE  
**Purpose:** Healing completion notification

**Event Schema:**
```json
{
  "type": "heal.complete",
  "plan_id": "string",
  "shard_id": "string",
  "success": true,
  "heal_depth": 2,
  "actions_taken": ["retry", "split"],
  "timestamp": "ISO8601"
}
```

---

### `hxo.status.summary`

**Publisher:** HXO Core  
**Subscriber:** All engines, Frontend  
**Purpose:** Unified operational status

**Event Schema:**
```json
{
  "type": "status.summary",
  "status": "healthy|degraded|down",
  "active_plans": 5,
  "total_shards_pending": 200,
  "total_shards_running": 50,
  "total_shards_complete": 5000,
  "engine_links": {
    "autonomy": "healthy",
    "blueprint": "healthy",
    "truth": "healthy",
    "cascade": "healthy",
    "federation": "healthy",
    "parser": "healthy",
    "leviathan": "healthy",
    "arie": "healthy",
    "envrecon": "healthy"
  },
  "timestamp": "ISO8601"
}
```

**Frequency:** Every 5 seconds  
**Use Cases:** Health dashboards, monitoring, alerts

---

## Event Flow Diagrams

### Plan Submission Flow

```
User/Parser
    │
    ├──► hxo.plan.submit
    │
    ▼
  HXO Core
    │
    ├──► hxo.link.blueprint (schema validation)
    │       └──► blueprint.schema.validate
    │
    ├──► hxo.link.truth (consensus)
    │       └──► truth.certify.request
    │
    └──► hxo.plan.accepted
```

### Shard Execution Flow

```
HXO Core
    │
    ├──► hxo.shard.claimed
    │
    ├──► hxo.shard.running
    │
    ├──► hxo.shard.complete
    │
    └──► hxo.telemetry.metrics (updated)
```

### Healing Flow

```
HXO Core (detects failure)
    │
    ├──► hxo.heal.trigger
    │       └──► Autonomy
    │               └──► autonomy.heal.strategy
    │
    ├──► HXO Core (applies strategy)
    │
    └──► hxo.heal.complete
            └──► ARIE (audit)
```

---

## Temporal Event Replay Cache (TERC)

HXO maintains a rolling cache of the last 10,000 Genesis events for:

- **Audit replay** — Reconstruct event sequence
- **Failure recovery** — Resume from last known state
- **Compliance** — Event logs for audits

### Configuration

```bash
HXO_EVENT_CACHE_LIMIT=10000  # TERC size
```

### Query TERC

```bash
# Get recent events
curl -H "Authorization: Bearer $ADMIRAL_TOKEN" \
  http://localhost:8000/api/hxo/terc?limit=100

# Replay events for plan
curl -H "Authorization: Bearer $ADMIRAL_TOKEN" \
  http://localhost:8000/api/hxo/terc/replay?plan_id=abc123
```

---

## Event Routing (ALIR)

Adaptive Load Intent Router prioritizes Genesis events based on:

1. **Critical path** — Truth, Blueprint events (highest priority)
2. **Operational** — Shard lifecycle events (medium priority)
3. **Telemetry** — Metrics, status (low priority)

### Configuration

```bash
HXO_ALIR_ENABLED=true  # Enable adaptive routing
```

### Priority Levels

- **P0 (Critical):** Consensus, certification, security
- **P1 (High):** Shard execution, healing
- **P2 (Medium):** Telemetry, metrics
- **P3 (Low):** Status updates, diagnostics

---

## Integration Checklist

To integrate a new engine with HXO:

- [ ] Define event schema for `hxo.link.{engine}`
- [ ] Implement event publisher in engine
- [ ] Register subscriber in HXO genesis link
- [ ] Add event handler in `hxo_genesis_link.py`
- [ ] Update `HXO_ENGINE_MATRIX.md`
- [ ] Add health check endpoint
- [ ] Document in this file
- [ ] Add integration test

---

**Status:** ✅ Complete  
**Last Updated:** 2025-10-11
