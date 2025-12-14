# HXO Overview — Hypshard-X Orchestrator

**Version:** 1.9.6n  
**Status:** Production-ready  
**Purpose:** Infinite shards, finite time — federated autonomy with truth certification

---

## What is HXO?

The Hypshard-X Orchestrator (HXO) is a sophisticated work orchestration engine designed to atomize long-running jobs into tiny, idempotent, resumable shards that can execute in parallel across time and space (processes, restarts, redeploys) with strong correctness guarantees.

### Core Problem

Render's hard timeout punishes monolithic deploys. Traditional deployment strategies struggle with:
- Platform timeouts (e.g., 10-minute hard limits)
- Non-resumable work after crashes/redeploys
- Lack of progress visibility
- No integrity guarantees for partial completion

### HXO Solution

HXO solves these problems through:

1. **Adaptive Sharding**: Scale from 1 to 1,000,000+ shards dynamically
2. **Content-Addressed Deduplication**: Each shard has a deterministic CAS ID
3. **Merkle Aggregation**: Single root hash represents entire job integrity
4. **Idempotent Execution**: Exactly-once semantics via checkpointing
5. **Resumable Across Redeploys**: Checkpoint store persists state
6. **Self-Healing**: Auto-tuning with Autonomy integration
7. **Truth Certification**: Cryptographic proof of correctness

---

## Architecture

### Core Components

```
HXO Core Engine
├── Planner: Converts high-level plans into DAG of shards
├── Partitioners: Split work (by filesize, module, DAG depth, etc.)
├── Schedulers: Fair round-robin, hot-shard splitting, backpressure
├── Executors: Idempotent work units (pack, migrate, index, etc.)
├── Checkpointer: SQLite persistence for resumption
├── Merkle Tree: Cryptographic aggregation
└── Rehydrator: Resume incomplete plans after redeploy
```

### Integration Adapters

```
Adapters (bridge_core/engines/adapters/)
├── hxo_genesis_link: Event bus integration
├── hxo_federation_link: Queue mechanisms
├── hxo_autonomy_link: Self-healing and auto-tuning
├── hxo_truth_link: Merkle certification
├── hxo_blueprint_link: Schema validation
├── hxo_parser_link: Plan parsing
└── hxo_permission_link: RBAC (Admiral-locked)
```

---

## Content-Addressed Shards (CAS)

Each shard is identified by a hash of `(task_spec + inputs + deps)`:

```python
cas_id = hash(stage_id || executor || inputs || dependencies)
```

Benefits:
- **Deduplication**: Same work = same CAS ID = skip redundant execution
- **Retries**: Failed shard can be retried with same ID
- **Cross-run reuse**: Completed shards from previous runs can be reused

---

## Merkle Tree Aggregation

HXO builds a Merkle tree from shard results:

```
           Root Hash
          /          \
    Branch A      Branch B
    /      \      /      \
  Leaf1  Leaf2  Leaf3  Leaf4
  (shard results)
```

- **Leaf**: `hash(executor_id || input_hash || output_digest || attempt_meta)`
- **Branch**: `hash(left_hash || right_hash)`
- **Root**: Single hash representing entire job

Truth engine verifies root + sample proofs. On failure, HXO auto-bisects and replays suspect subtree.

---

## Execution Flow

1. **Plan Creation**: Parser translates spec → HXOPlan with stages
2. **Shard Generation**: Partitioners split each stage into shards
3. **Scheduling**: Scheduler orders shards (fair, hot-split, backpressure-aware)
4. **Execution**: Executors process shards idempotently
5. **Checkpointing**: State persisted after each shard
6. **Aggregation**: Merkle tree built from results
7. **Certification**: Truth verifies root hash + sample proofs
8. **Finalization**: Plan marked complete, audit published

---

## Resumability

HXO survives redeploys:

```
Before Redeploy:
- Plan submitted
- 50/100 shards completed
- Checkpoint: plan, shards, results saved to SQLite

After Redeploy:
- HXO starts up
- Rehydrator loads incomplete plans
- Resumes only missing 50 shards
- Continues from checkpoint
```

---

## Self-Healing with Autonomy

HXO emits signals when hot paths detected:

```python
# Hot shard detected
await notify_autotune_signal({
    "plan_id": "...",
    "stage_id": "...",
    "signal_type": "hotspot",
    "metric_value": latency_ms,
    "suggested_action": "split_shard"
})
```

Autonomy responds with tuning recommendations:
- Split hot shards into smaller units
- Increase concurrency limits
- Change partitioner strategy

---

## Job Kinds (Blueprint Contract)

HXO defines shardable job types:

| Job Kind | Description | Partitioners | Executors |
|----------|-------------|--------------|-----------|
| `deploy.pack` | Pack backend files | by_filesize, by_module | pack_backend |
| `deploy.migrate` | Database migrations | by_sql_batch | sql_migrate |
| `deploy.prime` | Prime caches | by_module, by_dag_depth | warm_registry, prime_caches |
| `assets.index` | Index assets | by_asset_bucket, by_filesize | index_assets |
| `docs.index` | Index docs | by_route_map | docs_index |

Each job kind has safety policies (allow_non_idempotent, require_dry_run).

---

## Configuration

Environment variables (all optional, safe defaults):

```bash
# Enable/disable
HXO_ENABLED=true

# Safety/timebox
HXO_DEFAULT_SLO_MS=120000          # 2 min default stage SLO
HXO_SHARD_TIMEOUT_MS=15000         # 15s per-shard watchdog
HXO_MAX_CONCURRENCY=64             # Max parallel shards

# Adaptivity
HXO_AUTOSPLIT_P95_MS=8000          # Split if p95 > 8s
HXO_AUTOSPLIT_FACTOR=4             # Split into 4 sub-shards
HXO_MAX_SHARDS=1000000             # Hard cap

# Storage
HXO_DB_PATH=bridge_backend/.hxo/checkpoints.db
HXO_ARTIFACTS_DIR=bridge_backend/.hxo/artifacts

# RBAC
HXO_ALLOW_CAPTAIN_VIEW=true        # Captains can view status
```

---

## Genesis Topics

HXO publishes to Genesis event bus:

- `hxo.plan`: Plan submitted
- `hxo.shard.created`: Shard created
- `hxo.shard.claimed`: Shard claimed by executor
- `hxo.shard.done`: Shard completed successfully
- `hxo.shard.failed`: Shard failed
- `hxo.aggregate.ready`: Merkle tree ready
- `hxo.aggregate.certify`: Requesting Truth certification
- `hxo.aggregate.finalized`: Plan finalized with cert
- `hxo.autotune.signal`: Auto-tuning signal for Autonomy
- `hxo.alert`: Critical alerts
- `hxo.audit`: Audit trail

---

## RBAC (Admiral-Locked)

HXO operations are locked to Admiral by default:

| Capability | Description | Default Roles |
|------------|-------------|---------------|
| `hxo:plan` | Create plans | Admiral |
| `hxo:submit` | Submit plans | Admiral |
| `hxo:abort` | Abort plans | Admiral |
| `hxo:replay` | Replay failed subtrees | Admiral |
| `hxo:view` | View status | Admiral, Captain |
| `hxo:audit` | View audit logs | Admiral, Captain |

---

## TDE-X Integration

HXO becomes the "work engine" behind TDE-X stages:

```python
# TDE-X stage uses HXO for long-running work
stage = HXOStage(
    id="pack_backend",
    kind="deploy.pack",
    slo_ms=120000
)

plan = HXOPlan(
    name="tde_x_deploy",
    stages=[stage]
)

await hxo.submit_plan(plan)
```

TDE-X yields control early (health check passes), HXO continues in background.

---

## Comparison to Other Approaches

| Aspect | Traditional | HXO |
|--------|-------------|-----|
| Timeout risk | High (monolithic) | None (sharded) |
| Resumability | No | Yes (checkpoints) |
| Integrity | Hope | Proof (Merkle) |
| Adaptivity | Manual | Auto (Autonomy) |
| Deduplication | No | Yes (CAS) |

---

## Next Steps

See also:
- [HXO_OPERATIONS.md](./HXO_OPERATIONS.md) - Operating guide
- [HXO_BLUEPRINT_CONTRACT.md](./HXO_BLUEPRINT_CONTRACT.md) - Job kind schemas
- [HXO_GENESIS_TOPICS.md](./HXO_GENESIS_TOPICS.md) - Event matrix
