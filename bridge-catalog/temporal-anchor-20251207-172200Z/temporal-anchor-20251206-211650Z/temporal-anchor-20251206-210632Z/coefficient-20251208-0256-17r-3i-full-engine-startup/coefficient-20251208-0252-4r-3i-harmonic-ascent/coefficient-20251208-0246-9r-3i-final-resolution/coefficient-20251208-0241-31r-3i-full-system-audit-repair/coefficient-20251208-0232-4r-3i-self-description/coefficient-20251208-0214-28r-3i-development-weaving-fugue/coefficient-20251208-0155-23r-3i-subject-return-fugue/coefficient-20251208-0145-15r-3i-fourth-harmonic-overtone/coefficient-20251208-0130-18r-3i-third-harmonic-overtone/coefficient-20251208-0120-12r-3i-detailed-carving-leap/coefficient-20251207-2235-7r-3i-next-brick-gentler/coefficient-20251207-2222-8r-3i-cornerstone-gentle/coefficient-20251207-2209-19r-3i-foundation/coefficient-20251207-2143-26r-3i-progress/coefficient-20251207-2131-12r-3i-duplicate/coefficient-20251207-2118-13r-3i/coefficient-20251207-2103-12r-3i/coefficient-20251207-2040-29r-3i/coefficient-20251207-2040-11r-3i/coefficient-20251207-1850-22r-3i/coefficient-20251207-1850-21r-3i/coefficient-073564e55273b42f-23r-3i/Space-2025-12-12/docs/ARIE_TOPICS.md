# ARIE Genesis Topics Reference

## Overview

ARIE publishes to and subscribes from the Genesis Event Bus for full system integration and observability.

## Subscribed Topics

### deploy.platform.success

**Purpose**: Trigger post-deploy integrity scan

**Event Structure**:
```json
{
  "platform": "render|netlify|github",
  "deployment_id": "string",
  "timestamp": "ISO 8601",
  "status": "success"
}
```

**ARIE Action**:
1. Run scan in LINT_ONLY mode
2. Publish results to `arie.audit`
3. If `ARIE_AUTO_FIX_ON_DEPLOY_SUCCESS=true` and permission granted:
   - Apply SAFE_EDIT fixes
   - Publish to `arie.fix.applied`
   - Request Truth certification

**Example**:
```python
await bus.publish("deploy.platform.success", {
    "platform": "render",
    "deployment_id": "dep_abc123",
    "timestamp": "2025-10-11T20:30:00Z",
    "status": "success"
})
```

---

### genesis.heal

**Purpose**: Apply planned fixes on demand

**Event Structure**:
```json
{
  "category": "repo_integrity",
  "policy": "LINT_ONLY|SAFE_EDIT|REFACTOR|ARCHIVE",
  "requester": "string",
  "timestamp": "ISO 8601"
}
```

**ARIE Action**:
1. Verify category is `repo_integrity`
2. Check `arie:fix` permission
3. Run fixes with specified policy
4. Publish results

**Example**:
```python
await bus.publish("genesis.heal", {
    "category": "repo_integrity",
    "policy": "SAFE_EDIT",
    "requester": "admiral_kyle",
    "timestamp": "2025-10-11T20:30:00Z"
})
```

---

## Published Topics

### arie.audit

**Purpose**: Report scan results

**Event Structure**:
```json
{
  "run_id": "string",
  "timestamp": "ISO 8601",
  "findings_count": "integer",
  "by_severity": {
    "critical": "integer",
    "high": "integer",
    "medium": "integer",
    "low": "integer",
    "info": "integer"
  },
  "by_category": {
    "deprecated": "integer",
    "stub": "integer",
    "import_health": "integer",
    "route_integrity": "integer",
    "config_smell": "integer",
    "duplicate": "integer",
    "dead_file": "integer",
    "unused_import": "integer"
  },
  "policy": "string",
  "findings": [
    {
      "id": "string",
      "severity": "string",
      "category": "string",
      "file_path": "string",
      "description": "string"
    }
  ]
}
```

**Subscribers**: 
- Monitoring dashboards
- Alerting systems
- Compliance trackers

**Example**:
```python
bus.subscribe("arie.audit", async def on_audit(evt):
    if evt["findings_count"] > 100:
        await send_alert("High finding count in ARIE scan")
)
```

---

### arie.fix.intent

**Purpose**: Announce planned fixes before applying

**Event Structure**:
```json
{
  "plan_id": "string",
  "timestamp": "ISO 8601",
  "policy": "string",
  "actions_count": "integer",
  "estimated_impact": "string"
}
```

**Subscribers**:
- Approval workflows
- Audit logs
- Change management

**Example**:
```python
bus.subscribe("arie.fix.intent", async def on_intent(evt):
    if evt["policy"] in ["REFACTOR", "ARCHIVE"]:
        await request_approval(evt["plan_id"])
)
```

---

### arie.fix.applied

**Purpose**: Report successfully applied fixes

**Event Structure**:
```json
{
  "run_id": "string",
  "timestamp": "ISO 8601",
  "fixes_applied": "integer",
  "files_modified": "integer",
  "patches": [
    {
      "id": "string",
      "plan_id": "string",
      "files_modified": ["string"],
      "certified": "boolean",
      "certificate_id": "string|null"
    }
  ]
}
```

**Subscribers**:
- Truth Engine (for certification)
- Cascade Engine (for post-fix flows)
- Blueprint Registry (for structural updates)
- EnvRecon (for config changes)

**Example**:
```python
bus.subscribe("arie.fix.applied", async def on_applied(evt):
    for patch in evt["patches"]:
        await truth_engine.certify(patch)
        await cascade_engine.run_tests(patch["files_modified"])
)
```

---

### arie.fix.rollback

**Purpose**: Report rollback operations

**Event Structure**:
```json
{
  "rollback_id": "string",
  "patch_id": "string",
  "timestamp": "ISO 8601",
  "success": "boolean",
  "restored_files": ["string"],
  "error": "string|null"
}
```

**Subscribers**:
- Incident tracking
- Audit logs
- Monitoring

**Example**:
```python
bus.subscribe("arie.fix.rollback", async def on_rollback(evt):
    if not evt["success"]:
        await create_incident({
            "type": "arie_rollback_failed",
            "patch_id": evt["patch_id"],
            "error": evt["error"]
        })
)
```

---

### arie.alert

**Purpose**: Critical issues or failures

**Event Structure**:
```json
{
  "type": "string",  // deploy_scan_failed, heal_failed, certification_failed, etc.
  "message": "string",
  "timestamp": "ISO 8601",
  "severity": "high|critical"
}
```

**Subscribers**:
- Alert management
- On-call systems
- Incident response

**Example**:
```python
bus.subscribe("arie.alert", async def on_alert(evt):
    if evt["severity"] == "critical":
        await page_oncall(evt["message"])
)
```

---

### arie.schedule.tick

**Purpose**: Signal scheduled ARIE run (v1.9.6o)

**Event Structure**:
```json
{
  "timestamp": "ISO 8601",
  "interval_hours": "integer"
}
```

**Subscribers**:
- Monitoring systems
- Genesis introspection
- Audit logs

**Example**:
```python
bus.subscribe("arie.schedule.tick", async def on_tick(evt):
    logger.info(f"ARIE scheduled run started at {evt['timestamp']}")
)
```

---

### arie.schedule.summary

**Purpose**: Report summary of scheduled ARIE run (v1.9.6o)

**Event Structure**:
```json
{
  "run_id": "string",
  "timestamp": "ISO 8601",
  "findings_count": "integer",
  "fixes_applied": "integer",
  "fixes_failed": "integer",
  "certification_status": "string|null",
  "duration_seconds": "float"
}
```

**Subscribers**:
- Monitoring dashboards
- Trend analysis
- Genesis introspection

**Example**:
```python
bus.subscribe("arie.schedule.summary", async def on_summary(evt):
    metrics.record("arie.scheduled_run", {
        "findings": evt["findings_count"],
        "fixes": evt["fixes_applied"],
        "duration": evt["duration_seconds"]
    })
)
```

---

### arie.schedule.manual

**Purpose**: Report manually triggered ARIE run (v1.9.6o)

**Event Structure**:
```json
{
  "timestamp": "ISO 8601",
  "requester": "string",
  "run_id": "string",
  "success": "boolean"
}
```

**Subscribers**:
- Audit logs
- Access tracking

**Example**:
```python
bus.subscribe("arie.schedule.manual", async def on_manual(evt):
    audit_log.record("arie_manual_trigger", {
        "requester": evt["requester"],
        "run_id": evt["run_id"]
    })
)
```

---

## Integration Patterns

### Post-Deploy Flow (v1.9.6o)

```
deploy.platform.success
    ↓
arie.scan (SAFE_EDIT policy)
    ↓
arie.audit (scan results)
    ↓
arie.fix.applied (if fixes made)
    ↓
truth.certify (certification request)
    ↓
  ├─ success → arie.audit (certified)
  └─ failure → arie.fix.rollback → arie.alert
    ↓
cascade.notify (post-certification)
```

### Autonomous Scheduled Flow (v1.9.6o)

```
RRULE:FREQ=HOURLY;INTERVAL=12 (Genesis internal timer)
    ↓
arie.schedule.tick
    ↓
arie.scan (SAFE_EDIT policy)
    ↓
arie.audit
    ↓
arie.fix.applied (if fixes made)
    ↓
truth.certify
    ↓
  ├─ success → commit results
  └─ failure → auto-rollback & alert
    ↓
arie.schedule.summary
```

### Manual Heal Flow

```
genesis.heal (category: repo_integrity)
    ↓
arie.fix.intent
    ↓
arie.fix.applied
    ↓
truth.verify
```

### Failed Certification Flow (v1.9.6o)

```
truth.failed (certification failed)
    ↓
arie.fix.rollback (auto-rollback if ARIE_TRUTH_MANDATORY=true)
    ↓
arie.alert (notify failure)
```

---

## Monitoring Examples

### Count Findings by Severity

```python
severity_counts = defaultdict(int)

bus.subscribe("arie.audit", lambda evt:
    severity_counts.update(evt["by_severity"])
)
```

### Track Fix Success Rate

```python
fix_stats = {"applied": 0, "rollback": 0}

bus.subscribe("arie.fix.applied", lambda evt:
    fix_stats["applied"] += evt["fixes_applied"]
)

bus.subscribe("arie.fix.rollback", lambda evt:
    fix_stats["rollback"] += len(evt["restored_files"])
)
```

### Alert on Critical Issues

```python
bus.subscribe("arie.audit", async def on_audit(evt):
    critical = evt["by_severity"].get("critical", 0)
    if critical > 0:
        await bus.publish("arie.alert", {
            "type": "critical_findings",
            "message": f"{critical} critical issues found",
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "severity": "high"
        })
)
```

---

## Event Retention

ARIE events are stored in:
- Genesis event history (configurable retention)
- Patch journal (`bridge_backend/.arie/patchlog/*.json`)
- Summary reports (in-memory, last run)

Configure retention:
```bash
GENESIS_EVENT_RETENTION_DAYS=30
ARIE_MAX_PATCH_BACKLOG=50
```

---

## Testing Events

Manually trigger events for testing:

```python
from bridge_backend.genesis.bus import bus

# Trigger deploy success
await bus.publish("deploy.platform.success", {
    "platform": "test",
    "deployment_id": "test_123",
    "timestamp": datetime.now(UTC).isoformat() + "Z",
    "status": "success"
})

# Trigger heal request
await bus.publish("genesis.heal", {
    "category": "repo_integrity",
    "policy": "SAFE_EDIT",
    "requester": "test_admin",
    "timestamp": datetime.now(UTC).isoformat() + "Z"
})
```
