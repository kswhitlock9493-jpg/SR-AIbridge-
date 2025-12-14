# HXO Operations Guide

**Version:** 1.9.6n  
**Audience:** Admirals, Operators

---

## Table of Contents

1. [Starting HXO](#starting-hxo)
2. [Submitting Plans](#submitting-plans)
3. [Monitoring Status](#monitoring-status)
4. [Aborting Plans](#aborting-plans)
5. [Replaying Failed Subtrees](#replaying-failed-subtrees)
6. [SLO Tuning](#slo-tuning)
7. [Troubleshooting](#troubleshooting)

---

## Starting HXO

### Enable HXO

Set environment variable:

```bash
export HXO_ENABLED=true
```

Restart the application. HXO routes will be available at `/api/hxo/*`.

### Verify HXO is Running

```bash
curl http://localhost:8000/api/hxo/status/test
# Should return 404 (plan not found), confirming endpoint is active
```

---

## Submitting Plans

### Method 1: Direct API Call

```bash
curl -X POST http://localhost:8000/api/hxo/create-and-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Admiral" \
  -d '{
    "name": "deploy_full_stack",
    "stages": [
      {
        "id": "pack_backend",
        "kind": "deploy.pack",
        "slo_ms": 120000
      },
      {
        "id": "db_migrate",
        "kind": "deploy.migrate",
        "slo_ms": 30000
      },
      {
        "id": "prime_registry",
        "kind": "deploy.prime",
        "slo_ms": 45000
      }
    ],
    "constraints": {
      "max_shards": 500000
    }
  }'
```

Response:
```json
{
  "plan_id": "abc-123-def",
  "name": "deploy_full_stack",
  "status": "submitted",
  "merkle_seed": null,
  "total_shards": 150
}
```

### Method 2: Using Parser (Future)

```bash
# Parse CLI command into plan
hxo deploy --stages pack,migrate,prime
```

---

## Monitoring Status

### Get Live Status

```bash
curl http://localhost:8000/api/hxo/status/{plan_id}
```

Response:
```json
{
  "plan_id": "abc-123-def",
  "plan_name": "deploy_full_stack",
  "total_shards": 150,
  "pending_shards": 20,
  "claimed_shards": 5,
  "running_shards": 10,
  "done_shards": 110,
  "failed_shards": 5,
  "merkle_root": "def456...",
  "truth_certified": false,
  "eta_seconds": 45.2
}
```

### Watch Status (Poll)

```bash
watch -n 2 "curl -s http://localhost:8000/api/hxo/status/{plan_id}"
```

### Genesis Events

Subscribe to HXO events via Genesis:

```python
from bridge_backend.genesis.bus import genesis_bus

async def on_shard_done(event):
    print(f"Shard {event['cas_id']} completed")

await genesis_bus.subscribe("hxo.shard.done", on_shard_done)
```

---

## Aborting Plans

### Abort Running Plan

Only Admirals can abort:

```bash
curl -X POST http://localhost:8000/api/hxo/abort/{plan_id} \
  -H "Authorization: Admiral"
```

Response:
```json
{
  "plan_id": "abc-123-def",
  "status": "aborted"
}
```

All pending/running shards will be marked as failed. Completed shards remain in checkpoint store.

---

## Replaying Failed Subtrees

If a plan has failed shards, you can replay them:

```bash
curl -X POST http://localhost:8000/api/hxo/replay/{plan_id} \
  -H "Authorization: Admiral"
```

**Note:** Replay is currently not fully implemented. In the meantime, you can:

1. Query failed shards from checkpoint store
2. Create a new plan with only failed shard inputs
3. Submit the new plan

---

## SLO Tuning

### Understanding SLOs

- **Stage SLO**: Max time for all shards in a stage
- **Shard Timeout**: Max time for a single shard

### Tuning Strategy

1. **Start Conservative**: Use default 120s stage SLO
2. **Monitor**: Watch actual shard execution times
3. **Adjust**: If p95 shard time > 8s, HXO will auto-split hot shards
4. **Iterate**: Reduce SLO as shards become more granular

### Example Tuning

Initial plan:
```json
{
  "id": "pack_backend",
  "kind": "deploy.pack",
  "slo_ms": 120000
}
```

After observing hot shards, manually adjust:
```json
{
  "id": "pack_backend",
  "kind": "deploy.pack",
  "slo_ms": 60000,  // Reduced SLO
  "partitioner": "by_module"  // Finer partitioner
}
```

Or let Autonomy auto-tune via `hxo.autotune.signal`.

---

## Troubleshooting

### Plan Stuck in "Pending"

**Symptom**: Status shows `pending_shards` > 0 but no progress.

**Causes**:
1. HXO engine not running
2. Genesis bus disabled
3. Checkpointer database locked

**Solutions**:
```bash
# Check HXO enabled
echo $HXO_ENABLED  # Should be "true"

# Check Genesis bus
echo $GENESIS_MODE  # Should be "enabled"

# Check checkpoint DB
ls -lh bridge_backend/.hxo/checkpoints.db
# Should exist and not be locked
```

### Shards Failing

**Symptom**: `failed_shards` increasing.

**Debug**:
```bash
# Get plan report
curl http://localhost:8000/api/hxo/report/{plan_id}

# Check Genesis audit events
curl http://localhost:8000/api/genesis/events?topic=hxo.shard.failed
```

**Common Causes**:
- Executor timeout (increase `HXO_SHARD_TIMEOUT_MS`)
- Resource exhaustion (reduce `HXO_MAX_CONCURRENCY`)
- Invalid inputs (check partition data)

### Merkle Certification Failing

**Symptom**: `truth_certified` remains `false`.

**Solutions**:
1. Check Truth engine is running
2. Verify sample proofs are generated
3. Check Genesis topic `hxo.aggregate.certify` is published

### Performance Issues

**Symptom**: Slow shard execution.

**Tuning**:
```bash
# Increase concurrency (careful with resource limits)
export HXO_MAX_CONCURRENCY=128

# Enable hot-shard splitting
export HXO_AUTOSPLIT_P95_MS=5000  # Lower threshold
export HXO_AUTOSPLIT_FACTOR=8     # More aggressive split
```

---

## Best Practices

1. **Start Small**: Test with a few shards before scaling to millions
2. **Monitor Early**: Watch first few shards to validate executors
3. **Use Checkpoints**: Never disable checkpointing in production
4. **Trust Autonomy**: Let auto-tuning adjust partitioners/schedulers
5. **Audit Everything**: Review `hxo.audit` events regularly

---

## Advanced: Manual Checkpoint Recovery

If HXO crashes mid-execution:

```python
from bridge_backend.engines.hypshard_x.rehydrator import HXORehydrator
from bridge_backend.engines.hypshard_x.checkpointer import HXOCheckpointer
from pathlib import Path

# Initialize
checkpointer = HXOCheckpointer(Path("bridge_backend/.hxo/checkpoints.db"))
rehydrator = HXORehydrator(checkpointer)

# Find incomplete plans
incomplete = await rehydrator.find_incomplete_plans()

# Resume each
for plan_id in incomplete:
    await rehydrator.resume_plan(plan_id)
```

---

## Metrics to Track

| Metric | Target | Warning |
|--------|--------|---------|
| Shard completion rate | > 95% | < 90% |
| Average shard time | < 5s | > 10s |
| Failed shard ratio | < 1% | > 5% |
| Merkle certification rate | 100% | < 100% |
| Rehydration success rate | 100% | < 100% |

---

## Support

For issues:
1. Check `hxo.audit` events in Genesis
2. Review checkpoint DB: `bridge_backend/.hxo/checkpoints.db`
3. Check HXO logs: Filter for `[HXO]` prefix
4. Escalate to Admiral with plan_id and timestamp
