# Umbra Lattice Memory - Schema Reference

**v1.9.7g — Graph Schema & Normalization Rules**

## Graph Schema

### Node Types

#### `engine`

Represents an engine instance or action.

**Attributes**:
- `name` - Engine name (e.g., "chimera", "arie", "truth")
- `action` - Action performed (e.g., "heal", "deploy", "certify")
- `status` - Status (e.g., "success", "failed", "running")

**Example**:
```json
{
  "id": "engine:chimera:20251012T211130Z",
  "kind": "engine",
  "attrs": {
    "name": "chimera",
    "action": "deploy",
    "status": "success"
  }
}
```

#### `change`

Represents a code or configuration change.

**Attributes**:
- `file` - File path
- `author` - Author/actor
- `lines_changed` - Total lines modified

**Example**:
```json
{
  "id": "change:netlify.toml:20251012T211130Z",
  "kind": "change",
  "attrs": {
    "file": "netlify.toml",
    "author": "Admiral",
    "lines_changed": "15"
  }
}
```

#### `deploy`

Represents a deployment event.

**Attributes**:
- `service` - Platform (e.g., "netlify", "render", "github")
- `status` - Deploy status (e.g., "success", "failed", "pending")
- `commit` - Git commit SHA

**Example**:
```json
{
  "id": "deploy:render:20251012T211130Z",
  "kind": "deploy",
  "attrs": {
    "service": "render",
    "status": "success",
    "commit": "abc123def456"
  }
}
```

#### `heal`

Represents a repair or healing action.

**Attributes**:
- `action` - Repair action (e.g., "fix_env", "restart_service", "patch_config")
- `target` - Target system/file
- `status` - Outcome (e.g., "applied", "failed", "rolled_back")

**Example**:
```json
{
  "id": "heal:fix_env:20251012T211130Z",
  "kind": "heal",
  "attrs": {
    "action": "fix_env",
    "target": "render",
    "status": "applied"
  }
}
```

#### `drift`

Represents configuration drift detection.

**Attributes**:
- `context` - Drift context (e.g., "env", "config", "schema")
- `missing_keys` - Missing configuration keys
- `drifted_keys` - Keys with different values

**Example**:
```json
{
  "id": "drift:env:20251012T211130Z",
  "kind": "drift",
  "attrs": {
    "context": "env",
    "missing_keys": "['SECRET_KEY', 'API_TOKEN']",
    "drifted_keys": "['DATABASE_URL']"
  }
}
```

#### `var`

Represents environment variable changes.

**Attributes**:
- `key` - Variable name
- `source` - Source platform
- `action` - Action (e.g., "added", "removed", "updated")

**Example**:
```json
{
  "id": "var:SECRET_KEY:20251012T211130Z",
  "kind": "var",
  "attrs": {
    "key": "SECRET_KEY",
    "source": "render",
    "action": "added"
  }
}
```

#### `commit`

Represents a git commit.

**Attributes**:
- `sha` - Commit SHA
- `author` - Commit author
- `message` - Commit message

**Example**:
```json
{
  "id": "commit:abc123def456",
  "kind": "commit",
  "attrs": {
    "sha": "abc123def456",
    "author": "Admiral",
    "message": "feat: add umbra lattice"
  }
}
```

#### `cert`

Represents a truth certification.

**Attributes**:
- `cert_id` - Certificate ID
- `certified` - Certification status (true/false)
- `reason` - Certification reason

**Example**:
```json
{
  "id": "cert:xyz789:20251012T211130Z",
  "kind": "cert",
  "attrs": {
    "cert_id": "xyz789",
    "certified": "true",
    "reason": "verified_by_truth_engine"
  }
}
```

#### `role`

Represents RBAC role assignments.

**Attributes**:
- `user` - Username
- `role` - Role name (Admiral, Captain, Observer)
- `granted_by` - Grantor

**Example**:
```json
{
  "id": "role:alice:captain:20251012T211130Z",
  "kind": "role",
  "attrs": {
    "user": "alice",
    "role": "Captain",
    "granted_by": "Admiral"
  }
}
```

---

### Edge Types

#### `caused_by`

Indicates a causal relationship (X caused Y).

**Direction**: Cause → Effect

**Example**:
```json
{
  "src": "commit:abc123",
  "dst": "deploy:render:xyz",
  "kind": "caused_by"
}
```

Meaning: "Commit abc123 caused deploy render:xyz"

#### `fixes`

Indicates a repair relationship (X fixes Y).

**Direction**: Fix → Problem

**Example**:
```json
{
  "src": "heal:fix_env:123",
  "dst": "drift:env:456",
  "kind": "fixes"
}
```

Meaning: "Heal fix_env:123 fixes drift env:456"

#### `certified_by`

Indicates truth certification (X certified by Y).

**Direction**: Certified Entity → Certificate

**Example**:
```json
{
  "src": "cert:xyz789",
  "dst": "heal:fix_env:123",
  "kind": "certified_by"
}
```

Meaning: "Certificate xyz789 certified heal fix_env:123"

#### `approved_by`

Indicates RBAC approval (X approved by Y).

**Direction**: Approver → Approved Action

**Example**:
```json
{
  "src": "role:admiral:user1",
  "dst": "deploy:render:xyz",
  "kind": "approved_by"
}
```

Meaning: "Admiral user1 approved deploy render:xyz"

#### `emitted`

Indicates event emission (X emitted Y).

**Direction**: Emitter → Event

**Example**:
```json
{
  "src": "deploy:render:xyz",
  "dst": "drift:env:456",
  "kind": "emitted"
}
```

Meaning: "Deploy render:xyz emitted drift env:456"

#### `touches`

Indicates modification relationship (X touches/affects Y).

**Direction**: Modifier → Modified

**Example**:
```json
{
  "src": "change:netlify.toml:123",
  "dst": "deploy:netlify:xyz",
  "kind": "touches"
}
```

Meaning: "Change to netlify.toml touches deploy netlify:xyz"

#### `supersedes`

Indicates replacement (X supersedes Y).

**Direction**: New → Old

**Example**:
```json
{
  "src": "deploy:render:new",
  "dst": "deploy:render:old",
  "kind": "supersedes"
}
```

Meaning: "New deploy supersedes old deploy"

---

## Event Normalization Rules

### Deploy Events

**Input**:
```json
{
  "type": "deploy_success",
  "service": "render",
  "status": "success",
  "commit": "abc123",
  "ts": "2025-10-12T21:11:30Z"
}
```

**Normalized Output**:
- **Nodes**:
  - `deploy:render:2025-10-12T21:11:30Z` (deploy)
  - `commit:abc123` (commit)
- **Edges**:
  - `commit:abc123` --[caused_by]--> `deploy:render:2025-10-12T21:11:30Z`

### Drift Events

**Input**:
```json
{
  "type": "envrecon_drift",
  "context": "env",
  "missing": ["KEY1", "KEY2"],
  "drifted": ["KEY3"],
  "ts": "2025-10-12T21:11:30Z"
}
```

**Normalized Output**:
- **Nodes**:
  - `drift:env:2025-10-12T21:11:30Z` (drift)
- **Edges**: None (unless linked to deploy/heal)

### Heal Events

**Input**:
```json
{
  "type": "arie_heal",
  "action": "fix_env",
  "target": "render",
  "status": "applied",
  "fixes_drift": "drift:env:xyz",
  "ts": "2025-10-12T21:11:30Z"
}
```

**Normalized Output**:
- **Nodes**:
  - `heal:fix_env:2025-10-12T21:11:30Z` (heal)
- **Edges**:
  - `heal:fix_env:2025-10-12T21:11:30Z` --[fixes]--> `drift:env:xyz`

### Change Events

**Input**:
```json
{
  "type": "code_change",
  "file": "netlify.toml",
  "author": "Admiral",
  "lines_changed": 15,
  "ts": "2025-10-12T21:11:30Z"
}
```

**Normalized Output**:
- **Nodes**:
  - `change:netlify.toml:2025-10-12T21:11:30Z` (change)
- **Edges**: None (unless linked to commit)

### Certification Events

**Input**:
```json
{
  "type": "truth_certified",
  "cert_id": "xyz789",
  "certified": true,
  "certifies": "heal:fix_env:123",
  "ts": "2025-10-12T21:11:30Z"
}
```

**Normalized Output**:
- **Nodes**:
  - `cert:xyz789:2025-10-12T21:11:30Z` (cert)
- **Edges**:
  - `cert:xyz789:2025-10-12T21:11:30Z` --[certified_by]--> `heal:fix_env:123`

---

## Query Patterns

### Find All Deploys in Last 7 Days

```python
nodes = await storage.get_nodes(
    kind="deploy",
    since=datetime.now(timezone.utc) - timedelta(days=7),
    limit=100
)
```

### Find All Fixes for a Drift

```python
edges = await storage.get_edges(
    kind="fixes",
    dst="drift:env:xyz",
    limit=50
)
```

### Find What Caused a Deploy

```python
edges = await storage.get_edges(
    kind="caused_by",
    dst="deploy:render:xyz",
    limit=10
)
```

### Find All Certified Actions

```python
# Get all certification edges
cert_edges = await storage.get_edges(
    kind="certified_by",
    limit=1000
)

# Extract certified node IDs
certified_ids = [edge.dst for edge in cert_edges]
```

---

## Time Windows

Supported formats:
- `1h` - 1 hour
- `24h` - 24 hours
- `7d` - 7 days
- `1w` - 1 week
- `30d` - 30 days

Examples:
```bash
# API
GET /api/umbra/lattice/summary?since=7d

# CLI
python3 -m bridge_backend.cli.umbra lattice report --since 24h
```

---

## Snapshot Format

**JSON Structure**:
```json
{
  "nodes": [
    {
      "id": "deploy:render:20251012T211130Z",
      "kind": "deploy",
      "ts": "2025-10-12T21:11:30Z",
      "attrs": {
        "service": "render",
        "status": "success"
      }
    }
  ],
  "edges": [
    {
      "src": "commit:abc123",
      "dst": "deploy:render:20251012T211130Z",
      "kind": "caused_by",
      "ts": "2025-10-12T21:11:30Z",
      "attrs": {}
    }
  ],
  "summary": {
    "nodes": 128,
    "edges": 311,
    "node_kinds": {
      "deploy": 42,
      "commit": 38,
      "heal": 24
    },
    "edge_kinds": {
      "caused_by": 150,
      "fixes": 80
    }
  },
  "ts": "2025-10-12T21:11:30Z"
}
```

---

## Best Practices

### Node IDs

Format: `{kind}:{identifier}:{timestamp}`

Examples:
- `deploy:render:20251012T211130Z`
- `commit:abc123def456`
- `drift:env:20251012T211130Z`

### Edge Attribution

Always include relevant context in `attrs`:
```json
{
  "src": "heal:fix_env:123",
  "dst": "drift:env:456",
  "kind": "fixes",
  "attrs": {
    "confidence": "high",
    "method": "automated",
    "duration_ms": "1250"
  }
}
```

### Certification

All records should be truth-certified:
- Set `UMBRA_STRICT_TRUTH=true` for production
- Use pending queue for uncertified records
- Regularly review pending queue

### Snapshots

Create periodic snapshots:
- Daily: `python3 -m bridge_backend.cli.umbra lattice export`
- Keep at least 7 days of snapshots
- Store snapshots in version control for critical changes
