# HXO Quick Reference

**Version:** 1.9.6n — Hypshard-X Orchestrator  
**Purpose:** Infinite shards, finite time — federated autonomy with truth certification

---

## Quick Start

### 1. Enable HXO

```bash
export HXO_ENABLED=true
```

### 2. Submit a Plan

```bash
curl -X POST http://localhost:8000/api/hxo/create-and-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Admiral" \
  -d '{
    "name": "deploy_backend",
    "stages": [
      {"id": "pack", "kind": "deploy.pack", "slo_ms": 120000},
      {"id": "migrate", "kind": "deploy.migrate", "slo_ms": 30000}
    ],
    "constraints": {"max_shards": 10000}
  }'
```

### 3. Monitor Status

```bash
# Replace {plan_id} with actual plan ID from step 2
curl http://localhost:8000/api/hxo/status/{plan_id}
```

---

## API Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/hxo/create-and-submit` | POST | Admiral | Create and submit plan |
| `/api/hxo/status/{plan_id}` | GET | Any | Get plan status |
| `/api/hxo/report/{plan_id}` | GET | Any | Get final report with Merkle root |
| `/api/hxo/abort/{plan_id}` | POST | Admiral | Abort running plan |

---

## Job Kinds

| Kind | Description | Default SLO |
|------|-------------|-------------|
| `deploy.pack` | Pack backend files | 120s |
| `deploy.migrate` | Database migrations | 30s |
| `deploy.prime` | Prime caches/registry | 45s |
| `assets.index` | Index assets | 60s |
| `docs.index` | Index documentation | 30s |

---

## Environment Variables

### Core Settings

```bash
# Enable/disable HXO
HXO_ENABLED=true

# Safety limits
HXO_DEFAULT_SLO_MS=120000        # 2 minutes
HXO_SHARD_TIMEOUT_MS=15000       # 15 seconds
HXO_MAX_CONCURRENCY=64           # Max parallel shards
HXO_MAX_SHARDS=1000000           # Hard cap
```

### Auto-Tuning

```bash
# Split shards if p95 latency exceeds threshold
HXO_AUTOSPLIT_P95_MS=8000        # 8 seconds
HXO_AUTOSPLIT_FACTOR=4           # Split into 4 sub-shards
```

### Storage

```bash
HXO_DB_PATH=bridge_backend/.hxo/checkpoints.db
HXO_ARTIFACTS_DIR=bridge_backend/.hxo/artifacts
```

### RBAC

```bash
HXO_ALLOW_CAPTAIN_VIEW=true      # Captains can view status
```

---

## Plan Structure

Minimal plan:

```json
{
  "name": "my_plan",
  "stages": [
    {
      "id": "stage_1",
      "kind": "deploy.pack"
    }
  ]
}
```

Full plan:

```json
{
  "name": "full_deploy",
  "stages": [
    {
      "id": "pack_backend",
      "kind": "deploy.pack",
      "slo_ms": 120000,
      "partitioner": "by_filesize",
      "executor": "pack_backend",
      "scheduler": "fair_round_robin",
      "config": {
        "total_files": 100,
        "chunk_size_mb": 10
      }
    }
  ],
  "constraints": {
    "max_shards": 500000,
    "timebox_ms": 600000
  }
}
```

---

## Status Response

```json
{
  "plan_id": "abc-123",
  "plan_name": "deploy_backend",
  "total_shards": 150,
  "pending_shards": 10,
  "claimed_shards": 5,
  "running_shards": 20,
  "done_shards": 110,
  "failed_shards": 5,
  "merkle_root": "aabbcc...",
  "truth_certified": true,
  "started_at": "2025-10-11T20:00:00Z",
  "finished_at": null,
  "eta_seconds": 45.2
}
```

---

## Genesis Topics

### Published by HXO

- `hxo.plan` — Plan submitted
- `hxo.shard.created` — Shard created
- `hxo.shard.done` — Shard completed
- `hxo.shard.failed` — Shard failed
- `hxo.aggregate.certify` — Request certification
- `hxo.autotune.signal` — Auto-tuning signal
- `hxo.audit` — Audit trail

### Subscribed by HXO

- `genesis.heal` — Healing requests from Autonomy
- `genesis.intent` — Autonomy intents

---

## Partitioners

| Partitioner | Use Case | Config |
|-------------|----------|--------|
| `by_filesize` | Large file operations | `total_files`, `chunk_size_mb` |
| `by_module` | Module-based builds | `modules` |
| `by_dag_depth` | Dependency-aware work | `max_depth` |
| `by_route_map` | Route/endpoint work | `routes` |
| `by_asset_bucket` | Asset categorization | `buckets` |
| `by_sql_batch` | SQL batch operations | `batch_size`, `total_rows` |

---

## Executors

| Executor | Purpose | Idempotent |
|----------|---------|------------|
| `pack_backend` | Pack/bundle files | ✅ Yes |
| `warm_registry` | Warm registry | ✅ Yes |
| `index_assets` | Index assets | ✅ Yes |
| `prime_caches` | Prime caches | ✅ Yes |
| `docs_index` | Index docs | ✅ Yes |
| `sql_migrate` | SQL migrations | ⚠️ Requires care |

---

## Common Operations

### Abort a Plan

```bash
curl -X POST http://localhost:8000/api/hxo/abort/{plan_id} \
  -H "Authorization: Admiral"
```

### Get Final Report

```bash
curl http://localhost:8000/api/hxo/report/{plan_id}
```

### Watch Status in Real-Time

```bash
watch -n 2 "curl -s http://localhost:8000/api/hxo/status/{plan_id} | jq '.'"
```

---

## Troubleshooting

### Plan Not Starting

```bash
# Check if HXO is enabled
echo $HXO_ENABLED

# Check Genesis bus
echo $GENESIS_MODE

# Check logs
tail -f logs/app.log | grep HXO
```

### Shards Failing

```bash
# Get status
curl http://localhost:8000/api/hxo/status/{plan_id}

# Check failed shard events
curl http://localhost:8000/api/genesis/events?topic=hxo.shard.failed
```

### Slow Execution

```bash
# Increase concurrency
export HXO_MAX_CONCURRENCY=128

# Lower auto-split threshold
export HXO_AUTOSPLIT_P95_MS=5000
```

---

## File Locations

```
bridge_backend/
  engines/hypshard_x/          # HXO engine code
    core.py                    # Main orchestration
    models.py                  # Data models
    routes.py                  # API endpoints
    partitioners.py            # Partitioning strategies
    schedulers.py              # Scheduling algorithms
    executors.py               # Execution units
    checkpointer.py            # Persistence
    merkle.py                  # Merkle tree
    rehydrator.py              # Resumption logic
  
  bridge_core/engines/adapters/  # Integration adapters
    hxo_genesis_link.py        # Genesis integration
    hxo_federation_link.py     # Federation queues
    hxo_autonomy_link.py       # Autonomy self-healing
    hxo_truth_link.py          # Truth certification
    hxo_blueprint_link.py      # Blueprint schemas
    hxo_parser_link.py         # Plan parsing
    hxo_permission_link.py     # RBAC
  
  .hxo/                        # Runtime state
    checkpoints.db             # SQLite checkpoint store
    artifacts/                 # Shard artifacts
    journal/                   # Event journals

docs/
  HXO_OVERVIEW.md              # Architecture guide
  HXO_OPERATIONS.md            # Operations guide
  HXO_BLUEPRINT_CONTRACT.md    # Job kind schemas
  HXO_GENESIS_TOPICS.md        # Event matrix
```

---

## Integration with TDE-X

HXO can be used as the execution engine for TDE-X stages:

```python
# In TDE-X orchestrator
from bridge_backend.engines.hypshard_x.core import get_hxo_core
from bridge_backend.engines.hypshard_x.models import HXOPlan, HXOStage

async def run_long_stage():
    stage = HXOStage(
        id="pack_backend",
        kind="deploy.pack",
        slo_ms=120000
    )
    
    plan = HXOPlan(
        name="tde_x_deploy",
        stages=[stage]
    )
    
    hxo = get_hxo_core()
    plan_id = await hxo.submit_plan(plan)
    
    # Yield control, HXO continues in background
    return {"status": "submitted", "plan_id": plan_id}
```

---

## Capabilities (RBAC)

| Capability | Description | Required Role |
|------------|-------------|---------------|
| `hxo:plan` | Create plans | Admiral |
| `hxo:submit` | Submit plans | Admiral |
| `hxo:abort` | Abort plans | Admiral |
| `hxo:replay` | Replay failed subtrees | Admiral |
| `hxo:view` | View status | Admiral, Captain |
| `hxo:audit` | View audit logs | Admiral, Captain |

---

## Best Practices

1. ✅ **Start small**: Test with 10-100 shards before scaling
2. ✅ **Monitor early**: Watch first few shards closely
3. ✅ **Use checkpoints**: Never disable in production
4. ✅ **Trust auto-tuning**: Let Autonomy adjust parameters
5. ✅ **Audit regularly**: Review `hxo.audit` events
6. ❌ **Don't** set `HXO_MAX_SHARDS` > 1M without testing
7. ❌ **Don't** disable `HXO_SHARD_TIMEOUT_MS` (safety guard)

---

## Further Reading

- [HXO_OVERVIEW.md](./docs/HXO_OVERVIEW.md) — Architecture details
- [HXO_OPERATIONS.md](./docs/HXO_OPERATIONS.md) — Operations guide
- [HXO_BLUEPRINT_CONTRACT.md](./docs/HXO_BLUEPRINT_CONTRACT.md) — Job schemas
- [HXO_GENESIS_TOPICS.md](./docs/HXO_GENESIS_TOPICS.md) — Event flows
