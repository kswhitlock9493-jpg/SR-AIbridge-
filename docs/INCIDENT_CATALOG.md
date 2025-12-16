# Incident Catalog

**Version:** v1.9.6s  
**Purpose:** Reference for all incident kinds handled by Autonomy Decision Layer

---

## Incident Structure

```json
{
  "kind": "string",       // Incident type identifier
  "source": "string",     // Source system (github, render, netlify, etc.)
  "details": {},          // Optional metadata
  "timestamp": "string"   // ISO 8601 timestamp (optional)
}
```

---

## Deployment Incidents

### `deploy.netlify.preview_failed`

**Source:** GitHub Actions, Netlify webhooks  
**Action:** `REPAIR_CONFIG`  
**Reason:** `preview_failed`  
**Targets:** `["netlify"]`

**Description:**  
Netlify preview build failed. Autonomy will attempt to repair Netlify configuration (netlify.toml, _headers, _redirects) and retry the build.

**Example:**
```json
{
  "kind": "deploy.netlify.preview_failed",
  "source": "github",
  "details": {
    "run_id": "1234567890",
    "commit": "abc123def456",
    "pr_number": 42
  }
}
```

**Expected Action:**
1. Chimera inspects Netlify config files
2. Applies fixes for common issues (missing redirects, invalid headers, etc.)
3. Triggers preview rebuild via Netlify API
4. Truth certifies the result

---

### `deploy.render.failed`

**Source:** Render webhooks, monitoring  
**Action:** `RETRY`  
**Reason:** `render_retry_once`

**Description:**  
Render deployment failed. Autonomy will retry the deployment once, as Render failures are often transient (timeouts, resource limits, etc.).

**Example:**
```json
{
  "kind": "deploy.render.failed",
  "source": "render",
  "details": {
    "deploy_id": "dep-xyz789",
    "service": "sr-aibridge",
    "error": "Build timeout"
  }
}
```

**Expected Action:**
1. Chimera triggers deployment retry via Render API
2. Truth monitors deployment progress
3. On success, fail streak resets
4. On failure, fail streak increments

---

### `deploy.render.rollback`

**Source:** Render webhooks  
**Action:** `RETRY`  
**Reason:** `render_retry_once`

**Description:**  
Render automatically rolled back a deployment. Autonomy will attempt to redeploy with fixes.

**Example:**
```json
{
  "kind": "deploy.render.rollback",
  "source": "render",
  "details": {
    "deploy_id": "dep-rollback-123",
    "reason": "Health check failed"
  }
}
```

---

## Environment Incidents

### `envrecon.drift`

**Source:** EnvRecon engine  
**Action:** `SYNC_ENVS`  
**Reason:** `envrecon_drift`

**Description:**  
EnvRecon detected environment variable drift between platforms (Render, Netlify, local .env). Autonomy will sync variables to achieve parity.

**Example:**
```json
{
  "kind": "envrecon.drift",
  "source": "envrecon",
  "details": {
    "drift_count": 3,
    "missing_vars": ["AUTONOMY_ENABLED", "GENESIS_MODE"],
    "mismatched_vars": ["DATABASE_URL"],
    "platforms": ["render", "netlify"]
  }
}
```

**Expected Action:**
1. EnvRecon generates sync plan
2. Applies missing/drifted variables to target platforms
3. Re-audits to verify parity
4. Truth certifies the sync

---

### `env.drift.detected`

**Source:** Legacy environment monitoring  
**Action:** `SYNC_ENVS`  
**Reason:** `env_drift`

**Description:**  
Legacy incident kind for environment drift. Handled same as `envrecon.drift`.

---

## Code Integrity Incidents

### `arie.deprecated.detected`

**Source:** ARIE engine  
**Action:** `REPAIR_CODE`  
**Reason:** `arie_safe_edit`

**Description:**  
ARIE detected deprecated code patterns or integrity issues. Autonomy will apply safe edits to modernize the code.

**Example:**
```json
{
  "kind": "arie.deprecated.detected",
  "source": "arie",
  "details": {
    "deprecated_count": 5,
    "files": [
      "bridge_backend/old_module.py",
      "bridge_backend/legacy_utils.py"
    ],
    "patterns": ["old_import_style", "deprecated_function"]
  }
}
```

**Expected Action:**
1. ARIE applies safe edits (policy="SAFE_EDIT")
2. Runs tests to verify no breakage
3. Truth certifies the changes
4. If certified, commits the fixes

---

### `code.integrity.deprecated`

**Source:** Legacy code scanners  
**Action:** `REPAIR_CODE`  
**Reason:** `arie_safe_edit`

**Description:**  
Legacy incident kind for code integrity issues. Handled same as `arie.deprecated.detected`.

---

## Generic Incidents

### `*` (Unknown/Unrecognized)

**Source:** Any  
**Action:** `NOOP`  
**Reason:** `unrecognized_incident`

**Description:**  
Incident kind not in the policy matrix. Governor logs a warning and takes no action.

**Example:**
```json
{
  "kind": "custom.incident.type",
  "source": "custom_monitor",
  "details": {}
}
```

**Expected Action:**
- Log warning
- Return `NOOP` decision
- No execution, no fail streak change

---

## Adding New Incident Kinds

To add support for a new incident kind:

### 1. Update Governor Policy Matrix

In `bridge_backend/engines/autonomy/governor.py`, add a new condition in the `decide()` method:

```python
if incident.kind == "your.new.incident":
    return Decision(action="YOUR_ACTION", reason="your_reason", targets=["target"])
```

### 2. Update Genesis Topics (if needed)

If the incident comes from a new event source, add the topic to `bridge_backend/genesis/bus.py`:

```python
self._valid_topics = {
    # ... existing topics
    "your.new.topic",
}
```

### 3. Create Genesis Subscription (if needed)

If the incident is event-driven, create a handler in `autonomy_genesis_link.py`:

```python
async def on_your_new_event(event: Dict[str, Any]):
    incident = Incident(
        kind="your.new.incident",
        source="your_source",
        details=event
    )
    gov = AutonomyGovernor()
    decision = await gov.decide(incident)
    result = await gov.execute(decision)
```

And register it:

```python
genesis_bus.subscribe("your.new.topic", on_your_new_event)
```

### 4. Update This Catalog

Add the new incident kind to this document with:
- Description
- Expected action
- Example JSON
- Integration notes

### 5. Add Test Coverage

In `bridge_backend/tests/test_autonomy_governor.py`:

```python
@pytest.mark.asyncio
async def test_decide_your_new_incident(self):
    gov = AutonomyGovernor()
    incident = Incident(kind="your.new.incident", source="test")
    decision = await gov.decide(incident)
    assert decision.action == "YOUR_ACTION"
    assert decision.reason == "your_reason"
```

---

## Action Reference

| Action | Description | Engine |
|--------|-------------|--------|
| `NOOP` | No operation (skip, rate limited, cooldown) | None |
| `RETRY` | Retry last deployment | Chimera |
| `REPAIR_CONFIG` | Repair configuration files | Chimera |
| `REPAIR_CODE` | Apply safe code edits | ARIE |
| `SYNC_ENVS` | Sync environment variables | EnvRecon |
| `ROLLBACK` | Rollback to previous deployment | Chimera |
| `ESCALATE` | Circuit breaker tripped, manual intervention required | None |

---

## Event Flow Examples

### Example 1: Netlify Preview Failure → Auto-Fix

```
1. GitHub Actions job fails
2. Workflow step emits incident via API:
   POST /api/autonomy/incident
   {"kind":"deploy.netlify.preview_failed","source":"github"}

3. Governor decides: REPAIR_CONFIG
4. Chimera heals netlify.toml, _headers, _redirects
5. Chimera triggers new preview build
6. Truth certifies the result
7. Genesis publishes: autonomy.heal.applied
```

### Example 2: Environment Drift → Auto-Sync

```
1. EnvRecon audit detects drift
2. EnvRecon publishes: envrecon.drift
3. Autonomy Genesis link receives event
4. Governor decides: SYNC_ENVS
5. EnvRecon syncs missing/drifted vars
6. Truth certifies the sync
7. Genesis publishes: autonomy.heal.applied
```

### Example 3: Repeated Failures → Circuit Breaker

```
1. First incident: Governor executes, Truth fails cert (fail_streak=1)
2. Second incident (after cooldown): Governor executes, Truth fails cert (fail_streak=2)
3. Third incident (after cooldown): Governor executes, Truth fails cert (fail_streak=3)
4. Fourth incident: Governor returns ESCALATE (circuit_breaker_tripped)
5. All future incidents: ESCALATE until circuit manually closed
```

---

## See Also

- [AUTONOMY_DECISION_LAYER.md](AUTONOMY_DECISION_LAYER.md) - Architecture details
- [AUTONOMY_OPERATIONS.md](AUTONOMY_OPERATIONS.md) - Operator guide
- [CHIMERA_README.md](CHIMERA_README.md) - Chimera deployment engine
- [ARIE_README.md](ARIE_README.md) - ARIE code integrity engine
- [ENVRECON_QUICK_REF.md](ENVRECON_QUICK_REF.md) - EnvRecon reconciliation
