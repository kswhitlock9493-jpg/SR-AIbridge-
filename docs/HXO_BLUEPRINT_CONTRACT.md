# HXO Blueprint Contract

**Version:** 1.9.6n  
**Purpose:** Job kind schemas, policies, and safety contracts

---

## Overview

Blueprint defines the contract between HXO and job executors. Each job kind has:

1. **Description**: What the job does
2. **Allowed Partitioners**: How work can be split
3. **Allowed Executors**: What can execute the work
4. **Safety Policy**: Idempotency and dry-run requirements
5. **Result Schema**: Expected output structure

---

## Job Kinds

### `deploy.pack`

**Description**: Pack backend files for deployment (build, bundle, compress)

**Allowed Partitioners**:
- `by_filesize`: Split by file size thresholds
- `by_module`: Split by module/package structure

**Allowed Executors**:
- `pack_backend`: Idempotent file packing executor

**Safety Policy**:
```json
{
  "allow_non_idempotent": false,
  "require_dry_run": false
}
```

**Default SLO**: 120000ms (2 minutes)

**Input Schema**:
```json
{
  "partition_id": "integer",
  "file_range_start": "integer",
  "file_range_end": "integer",
  "chunk_size_mb": "integer"
}
```

**Output Schema**:
```json
{
  "status": "packed",
  "partition_id": "integer",
  "files_processed": "integer"
}
```

---

### `deploy.migrate`

**Description**: Execute database migrations in batches

**Allowed Partitioners**:
- `by_sql_batch`: Split into SQL batch operations

**Allowed Executors**:
- `sql_migrate`: Batch SQL migration executor

**Safety Policy**:
```json
{
  "allow_non_idempotent": true,
  "require_dry_run": true
}
```

**Default SLO**: 30000ms (30 seconds)

**Input Schema**:
```json
{
  "batch_id": "integer",
  "offset": "integer",
  "limit": "integer",
  "stage_kind": "string"
}
```

**Output Schema**:
```json
{
  "status": "migrated",
  "batch_id": "integer",
  "rows_affected": "integer"
}
```

**Special Notes**:
- Requires `hxo:force-merge` capability if non-idempotent
- Must run dry-run first before applying

---

### `deploy.prime`

**Description**: Prime registry and caches for application startup

**Allowed Partitioners**:
- `by_module`: Split by module structure
- `by_dag_depth`: Split by dependency depth

**Allowed Executors**:
- `warm_registry`: Registry warming executor
- `prime_caches`: Cache priming executor

**Safety Policy**:
```json
{
  "allow_non_idempotent": false,
  "require_dry_run": false
}
```

**Default SLO**: 45000ms (45 seconds)

**Input Schema**:
```json
{
  "module": "string",
  "stage_kind": "string"
}
```

**Output Schema**:
```json
{
  "status": "warmed",
  "module": "string",
  "cache_entries": "integer"
}
```

---

### `assets.index`

**Description**: Index assets for search and retrieval

**Allowed Partitioners**:
- `by_asset_bucket`: Split by asset category
- `by_filesize`: Split by file size

**Allowed Executors**:
- `index_assets`: Asset indexing executor

**Safety Policy**:
```json
{
  "allow_non_idempotent": false,
  "require_dry_run": false
}
```

**Default SLO**: 60000ms (1 minute)

**Input Schema**:
```json
{
  "bucket": "string",
  "stage_kind": "string"
}
```

**Output Schema**:
```json
{
  "status": "indexed",
  "bucket": "string",
  "assets_indexed": "integer"
}
```

---

### `assets.stage`

**Description**: Stage assets for deployment (upload, CDN sync)

**Allowed Partitioners**:
- `by_asset_bucket`: Split by asset category
- `by_filesize`: Split by file size

**Allowed Executors**:
- `index_assets`: Asset staging executor (reuses indexing logic)

**Safety Policy**:
```json
{
  "allow_non_idempotent": false,
  "require_dry_run": false
}
```

**Default SLO**: 60000ms (1 minute)

---

### `docs.index`

**Description**: Index documentation for search

**Allowed Partitioners**:
- `by_route_map`: Split by route/endpoint

**Allowed Executors**:
- `docs_index`: Documentation indexing executor

**Safety Policy**:
```json
{
  "allow_non_idempotent": false,
  "require_dry_run": false
}
```

**Default SLO**: 30000ms (30 seconds)

**Input Schema**:
```json
{
  "route": "string",
  "stage_kind": "string"
}
```

**Output Schema**:
```json
{
  "status": "indexed",
  "route": "string",
  "docs_indexed": "integer"
}
```

---

## Validation Rules

### Stage Validation

Blueprint validates stages before submission:

1. **Job kind exists**: Must be a registered job kind
2. **Partitioner allowed**: Must be in job kind's allowed partitioners
3. **Executor allowed**: Must be in job kind's allowed executors
4. **Safety policy respected**: Non-idempotent operations require special permission

### Example Validation

Valid stage:
```json
{
  "id": "pack_backend",
  "kind": "deploy.pack",
  "partitioner": "by_filesize",
  "executor": "pack_backend"
}
```
✅ Valid: All constraints satisfied

Invalid stage:
```json
{
  "id": "pack_backend",
  "kind": "deploy.pack",
  "partitioner": "by_sql_batch",  // ❌ Not allowed for deploy.pack
  "executor": "pack_backend"
}
```
❌ Invalid: Partitioner not allowed

---

## Adding New Job Kinds

To add a new job kind:

1. **Define Schema**: Create entry in `hxo_blueprint_link.py`
2. **Implement Partitioner**: Add to `partitioners.py`
3. **Implement Executor**: Add to `executors.py`
4. **Test**: Create test in `test_hxo_planner.py`
5. **Document**: Add to this file

Example:

```python
# In hxo_blueprint_link.py
HXO_JOB_KINDS["custom.job"] = {
    "description": "Custom job description",
    "partitioners": ["by_custom"],
    "executors": ["custom_executor"],
    "safety_policy": {
        "allow_non_idempotent": False,
        "require_dry_run": False
    }
}

# In partitioners.py
class ByCustomPartitioner(Partitioner):
    async def partition(self, stage: HXOStage) -> List[Dict[str, Any]]:
        # Implementation
        pass

# In executors.py
class CustomExecutor(Executor):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
        pass
```

---

## Safety Policies

### `allow_non_idempotent`

**Default**: `false`

When `true`, allows operations that may have side effects if executed multiple times.

**Use cases**:
- Database migrations (can't be safely re-run)
- External API calls with non-idempotent effects
- File deletions

**Requirements**:
- User must have `hxo:force-merge` capability
- Stage must set `non_idempotent: true` explicitly

### `require_dry_run`

**Default**: `false`

When `true`, requires a dry-run validation before executing.

**Use cases**:
- Database schema changes
- Destructive operations
- Complex transformations

**Workflow**:
1. Submit plan with `dry_run: true`
2. Review dry-run results
3. Submit plan with `dry_run: false` to apply

---

## Result Schemas

All executors must return:

```json
{
  "status": "string",  // Required: success indicator
  // ...custom fields
}
```

Common status values:
- `"packed"`, `"migrated"`, `"warmed"`, `"primed"`, `"indexed"`, `"staged"`

Custom fields depend on job kind (see individual schemas above).

---

## Evolution Policy

Blueprint schemas evolve with:

1. **Backward Compatibility**: Old plans continue to work
2. **Versioning**: Schemas include version field
3. **Deprecation**: Old job kinds marked deprecated, then removed after grace period
4. **Migration**: Automated tools to migrate old plans to new schemas

---

## Appendix: Full Job Kind Registry

| Job Kind | Partitioners | Executors | Non-Idempotent | Dry-Run |
|----------|--------------|-----------|----------------|---------|
| `deploy.pack` | by_filesize, by_module | pack_backend | No | No |
| `deploy.migrate` | by_sql_batch | sql_migrate | Yes | Yes |
| `deploy.prime` | by_module, by_dag_depth | warm_registry, prime_caches | No | No |
| `assets.index` | by_asset_bucket, by_filesize | index_assets | No | No |
| `assets.stage` | by_asset_bucket, by_filesize | index_assets | No | No |
| `docs.index` | by_route_map | docs_index | No | No |
