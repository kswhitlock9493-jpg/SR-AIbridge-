# Self-Test Healing Auto-Trigger

## v1.9.7j — Auto-Heal Trigger Logic

The Auto-Heal Trigger coordinates automated repairs when self-test failures are detected.

## Trigger Flow

```
Self-Test Failure
    ↓
Publish selftest.autoheal.trigger
    ↓
Select Healing Strategy
    ↓
Execute Repair (ARIE/Chimera/Cascade)
    ↓
Request Truth Certification
    ↓
Retry if not certified (max 3 attempts)
    ↓
Publish selftest.autoheal.complete
```

## Healing Strategies

### ARIE Strategy

**Engines:** EnvRecon, EnvScribe, Firewall

**Actions:**
- Configuration repair
- Environment variable healing
- Policy enforcement

**Example:**
```python
result = await autoheal._heal_with_arie("EnvRecon", test_result)
# Returns: {"strategy": "arie", "action": "config_repaired"}
```

### Chimera Strategy

**Engines:** Chimera, Leviathan, Federation

**Actions:**
- Deployment repair
- Build configuration healing
- Platform integration fixes

**Example:**
```python
result = await autoheal._heal_with_chimera("Chimera", test_result)
# Returns: {"strategy": "chimera", "action": "deployment_repaired"}
```

### Cascade Strategy

**Engines:** Truth, Cascade, Genesis, HXO

**Actions:**
- System recovery
- State restoration
- Critical subsystem repair

**Example:**
```python
result = await autoheal._heal_with_cascade("Truth", test_result)
# Returns: {"strategy": "cascade", "action": "system_recovered"}
```

### Generic Strategy

**Engines:** All other engines

**Actions:**
- Engine reinitialization
- Basic health checks
- Default recovery procedures

## Retry Logic

### Configuration

- `AUTOHEAL_MAX_RETRIES`: Maximum retry attempts (default: 3)
- `AUTOHEAL_RETRY_DELAY`: Delay between retries in seconds (default: 1.0)

### Behavior

1. **Attempt 1**: Execute healing strategy
2. **Truth Check**: Request certification
3. **If Failed**: Wait `AUTOHEAL_RETRY_DELAY` seconds
4. **Attempt 2**: Retry healing
5. **Repeat**: Up to `AUTOHEAL_MAX_RETRIES` times
6. **Exhausted**: Mark as failed if all attempts fail

## Truth Certification

All healing results must be certified by the Truth Engine before being marked as successful.

### Certification Process

```python
certified = await autoheal._certify_with_truth(engine_name, heal_result)
if certified:
    # Healing successful
    publish("selftest.autoheal.complete", {...})
else:
    # Retry or fail
    continue
```

### Certification Criteria

- Module hashes verified
- Test matrix passed
- No security violations
- RBAC permissions validated

## Event Topics

### selftest.autoheal.trigger

Published when healing is initiated.

**Payload:**
```json
{
  "engine": "EnvRecon",
  "timestamp": "2024-10-12T12:34:56.789Z",
  "test_result": {
    "engine": "EnvRecon",
    "action": "health_check",
    "result": "⚠️ auto-heal launched",
    "error": "Configuration drift detected"
  }
}
```

### selftest.autoheal.complete

Published when healing completes successfully.

**Payload:**
```json
{
  "engine": "EnvRecon",
  "timestamp": "2024-10-12T12:34:58.123Z",
  "certified": true,
  "attempts": 1
}
```

## Healing Result Schema

```json
{
  "engine": "EnvRecon",
  "action": "repair_patch_applied",
  "result": "✅ certified",
  "strategy": "arie",
  "attempts": 1,
  "duration_seconds": 1.234
}
```

## Error Handling

### Healing Failure

If all retry attempts fail:

```json
{
  "engine": "EnvRecon",
  "action": "auto_heal_exhausted",
  "result": "❌ healing failed",
  "attempts": 3
}
```

### Disabled Auto-Heal

If `AUTO_HEAL_ON=false`:

```json
{
  "engine": "EnvRecon",
  "action": "auto_heal_skipped",
  "result": "❌ auto-heal disabled"
}
```

## Integration Examples

### Manual Trigger

```python
from bridge_backend.engines.selftest.autoheal_trigger import AutoHealTrigger

autoheal = AutoHealTrigger()
result = await autoheal.heal_engine("EnvRecon", test_result)
```

### Genesis Bus Integration

```python
from bridge_backend.genesis.bus import genesis_bus

# Subscribe to autoheal events
@genesis_bus.subscribe("selftest.autoheal.trigger")
async def on_autoheal_trigger(event):
    logger.info(f"Healing triggered for {event['engine']}")

@genesis_bus.subscribe("selftest.autoheal.complete")
async def on_autoheal_complete(event):
    logger.info(f"Healing completed for {event['engine']}")
```

## Monitoring

All healing activities are logged to:
- Genesis event bus
- Steward metrics system
- Self-test reports directory

Reports available at:
```
bridge_backend/logs/selftest_reports/latest.json
```

## Security

- All healing actions require Admiral role
- Truth certification required before applying changes
- RBAC enforcement at every step
- Audit trail in Genesis ledger
