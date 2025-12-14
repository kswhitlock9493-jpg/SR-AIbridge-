# HXO Genesis Topics

**Version:** 1.9.6n  
**Purpose:** Event matrix and flows for HXO + Genesis integration

---

## Overview

HXO publishes and subscribes to Genesis topics for:
- **Coordination**: Cross-engine orchestration
- **Observability**: Real-time status and audit
- **Self-Healing**: Autonomy-driven auto-tuning
- **Certification**: Truth-verified integrity

---

## Topic Registry

### HXO Topics

| Topic | Direction | Purpose | Payload |
|-------|-----------|---------|---------|
| `hxo.plan` | Publish | Plan submitted | `{plan_id, plan_name, stages, submitted_by}` |
| `hxo.shard.created` | Publish | Shard created | `{plan_id, stage_id, cas_id, phase}` |
| `hxo.shard.claimed` | Publish | Shard claimed by executor | `{plan_id, cas_id, stage_id}` |
| `hxo.shard.done` | Publish | Shard completed | `{plan_id, cas_id, stage_id, output_digest}` |
| `hxo.shard.failed` | Publish | Shard failed | `{plan_id, cas_id, stage_id, error}` |
| `hxo.aggregate.ready` | Publish | Merkle tree computed | `{plan_id, merkle_root, total_shards}` |
| `hxo.aggregate.certify` | Publish | Request Truth certification | `{plan_id, merkle_root, sample_proofs}` |
| `hxo.aggregate.finalized` | Publish | Plan finalized with cert | `{plan_id, certificate, timestamp}` |
| `hxo.aggregate.failed` | Publish | Certification failed | `{plan_id, merkle_root, reason}` |
| `hxo.autotune.signal` | Publish | Auto-tuning signal | `{plan_id, stage_id, signal_type, metric_value, suggested_action}` |
| `hxo.alert` | Publish | Critical alerts | `{plan_id, alert_type, severity, message}` |
| `hxo.audit` | Publish | Audit trail | `{user, role, operation, details, timestamp}` |

### HXO Subscriptions

| Topic | Handler | Purpose |
|-------|---------|---------|
| `genesis.heal` | `_on_heal_request` | Handle healing requests from Autonomy |
| `genesis.intent` | `_on_autonomy_intent` | Handle autonomy intents (autotune, etc.) |

---

## Event Flows

### Flow 1: Plan Submission

```
1. Admiral submits plan via API
   ↓
2. HXO validates plan (Blueprint)
   ↓
3. HXO publishes `hxo.plan`
   {
     "plan_id": "abc-123",
     "plan_name": "deploy_full_stack",
     "stages": 3,
     "submitted_by": "admiral"
   }
   ↓
4. HXO creates shards (Partitioners)
   ↓
5. For each shard, publish `hxo.shard.created`
   {
     "plan_id": "abc-123",
     "stage_id": "pack_backend",
     "cas_id": "def456",
     "phase": "pending"
   }
```

### Flow 2: Shard Execution

```
1. Scheduler picks shard
   ↓
2. HXO publishes `hxo.shard.claimed`
   {
     "plan_id": "abc-123",
     "cas_id": "def456",
     "stage_id": "pack_backend"
   }
   ↓
3. Executor runs shard
   ↓
4. On success, publish `hxo.shard.done`
   {
     "plan_id": "abc-123",
     "cas_id": "def456",
     "stage_id": "pack_backend",
     "output_digest": "xyz789"
   }
   ↓
5. OR on failure, publish `hxo.shard.failed`
   {
     "plan_id": "abc-123",
     "cas_id": "def456",
     "stage_id": "pack_backend",
     "error": "timeout after 15s"
   }
```

### Flow 3: Merkle Certification

```
1. All shards complete
   ↓
2. HXO builds Merkle tree
   ↓
3. HXO publishes `hxo.aggregate.ready`
   {
     "plan_id": "abc-123",
     "merkle_root": "aabbcc...",
     "total_shards": 150
   }
   ↓
4. HXO samples proofs
   ↓
5. HXO publishes `hxo.aggregate.certify`
   {
     "plan_id": "abc-123",
     "merkle_root": "aabbcc...",
     "sample_proofs": [
       {
         "leaf_cas_id": "def456",
         "leaf_hash": "...",
         "path": [...],
         "root_hash": "aabbcc..."
       }
     ]
   }
   ↓
6. Truth verifies proofs
   ↓
7. On success, HXO publishes `hxo.aggregate.finalized`
   {
     "plan_id": "abc-123",
     "certificate": {
       "certified": true,
       "certificate_id": "cert_abc_aabbcc",
       "timestamp": "2025-10-11T21:00:00Z"
     }
   }
   ↓
8. OR on failure, HXO publishes `hxo.aggregate.failed`
   {
     "plan_id": "abc-123",
     "merkle_root": "aabbcc...",
     "reason": "proof verification failed"
   }
   ↓
9. If failed, HXO auto-bisects and replays suspect subtree
```

### Flow 4: Auto-Tuning (Autonomy)

```
1. Shard execution detects hotspot (p95 > 8s)
   ↓
2. HXO publishes `hxo.autotune.signal`
   {
     "plan_id": "abc-123",
     "stage_id": "pack_backend",
     "signal_type": "hotspot",
     "metric_value": 12500,  // ms
     "suggested_action": "split_shard"
   }
   ↓
3. Autonomy receives signal
   ↓
4. Autonomy computes tuning recommendation
   ↓
5. Autonomy publishes `genesis.heal`
   {
     "source": "autonomy",
     "plan_id": "abc-123",
     "action": "split_shard",
     "parameters": {
       "split_factor": 4
     }
   }
   ↓
6. HXO receives heal request (subscribed to `genesis.heal`)
   ↓
7. HXO applies tuning (splits hot shard)
```

### Flow 5: Audit Trail

```
1. Any HXO operation (submit, abort, replay)
   ↓
2. HXO publishes `hxo.audit`
   {
     "user": "kyle",
     "role": "admiral",
     "operation": "plan.submit",
     "details": {
       "plan_id": "abc-123",
       "plan_name": "deploy_full_stack"
     },
     "timestamp": "2025-10-11T21:00:00Z"
   }
   ↓
3. Guardians/Audit engine records event
```

---

## Payload Schemas

### `hxo.plan`

```json
{
  "plan_id": "string (UUID)",
  "plan_name": "string",
  "stages": "integer (count)",
  "submitted_by": "string (user)"
}
```

### `hxo.shard.created`

```json
{
  "plan_id": "string",
  "stage_id": "string",
  "cas_id": "string (16-char hex)",
  "phase": "pending"
}
```

### `hxo.shard.done`

```json
{
  "plan_id": "string",
  "cas_id": "string",
  "stage_id": "string",
  "output_digest": "string (SHA-256)"
}
```

### `hxo.shard.failed`

```json
{
  "plan_id": "string",
  "cas_id": "string",
  "stage_id": "string",
  "error": "string (error message)"
}
```

### `hxo.autotune.signal`

```json
{
  "plan_id": "string",
  "stage_id": "string",
  "signal_type": "hotspot|high_latency|timeout_risk|queue_depth",
  "metric_value": "number",
  "suggested_action": "split_shard|increase_concurrency|change_partitioner",
  "timestamp": "ISO 8601"
}
```

### `hxo.aggregate.certify`

```json
{
  "plan_id": "string",
  "merkle_root": "string (SHA-256)",
  "sample_proofs": [
    {
      "leaf_cas_id": "string",
      "leaf_hash": "string",
      "path": [
        {"side": "left|right", "hash": "string"}
      ],
      "root_hash": "string"
    }
  ]
}
```

### `hxo.audit`

```json
{
  "user": "string",
  "role": "admiral|captain|...",
  "operation": "plan.submit|plan.abort|plan.replay",
  "details": {
    "plan_id": "string",
    "...": "operation-specific"
  },
  "timestamp": "ISO 8601"
}
```

---

## Integration Points

### With Autonomy

**HXO → Autonomy**:
- `hxo.autotune.signal`: Hot shard detection, timeout risks

**Autonomy → HXO**:
- `genesis.heal`: Tuning recommendations

### With Truth

**HXO → Truth**:
- `hxo.aggregate.certify`: Merkle root + sample proofs

**Truth → HXO**:
- (Implicit) Certification result via callback or polling

### With Blueprint

**HXO → Blueprint**:
- `blueprint.events` (job kind registration)

**Blueprint → HXO**:
- (Synchronous) Schema validation during plan submission

### With Parser

**Parser → HXO**:
- (Synchronous) Parses CLI/specs into HXOPlan

### With Federation

**HXO → Federation**:
- (Queue) Shard claims, shard results

**Federation → HXO**:
- (Queue) Remote shard execution results

---

## Event Ordering Guarantees

1. **Plan Events**: `hxo.plan` → `hxo.shard.created` (all shards) → execution events
2. **Shard Events**: `hxo.shard.created` → `hxo.shard.claimed` → (`hxo.shard.done` OR `hxo.shard.failed`)
3. **Aggregation Events**: `hxo.aggregate.ready` → `hxo.aggregate.certify` → (`hxo.aggregate.finalized` OR `hxo.aggregate.failed`)

---

## Monitoring Queries

### Get All Plans

```python
events = await genesis_bus.query_history(topic="hxo.plan")
```

### Get Shards for Plan

```python
events = await genesis_bus.query_history(
    topic="hxo.shard.*",
    filter={"plan_id": "abc-123"}
)
```

### Get Failed Shards

```python
events = await genesis_bus.query_history(
    topic="hxo.shard.failed"
)
```

### Get Audit Trail for User

```python
events = await genesis_bus.query_history(
    topic="hxo.audit",
    filter={"user": "kyle"}
)
```

---

## Rate Limiting

To prevent event storms, HXO implements:

1. **Batch Publishing**: Shard events batched (e.g., every 100 shards)
2. **Throttling**: Max 1000 events/second to Genesis bus
3. **Sampling**: Autotune signals sampled (not every shard)

Configuration:

```bash
export HXO_EVENT_BATCH_SIZE=100
export HXO_EVENT_MAX_RATE=1000
export HXO_AUTOTUNE_SAMPLE_RATE=0.1  # 10% of shards
```

---

## Appendix: Full Event Matrix

| Event | Producer | Consumers | Frequency |
|-------|----------|-----------|-----------|
| `hxo.plan` | HXO | Monitors, Audit | Per plan |
| `hxo.shard.created` | HXO | Monitors | Per shard |
| `hxo.shard.claimed` | HXO | Monitors | Per shard |
| `hxo.shard.done` | HXO | Monitors, Merkle | Per shard |
| `hxo.shard.failed` | HXO | Monitors, Autonomy | Per failure |
| `hxo.aggregate.certify` | HXO | Truth | Per plan |
| `hxo.autotune.signal` | HXO | Autonomy | Per hotspot |
| `hxo.audit` | HXO | Guardians | Per operation |
| `genesis.heal` | Autonomy | HXO | Per recommendation |
