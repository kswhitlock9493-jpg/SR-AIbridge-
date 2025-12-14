# Upgrade Guide: v1.9.6q

## What's New

### HXO↔Genesis Async-Safe Linkage

v1.9.6q fixes critical boot failures related to HXO adapter registration:

1. **Async-Safe Registration**: Adapters now tolerate both sync and async bus methods
2. **Idempotent Links**: Multiple registration attempts are safe (no more crashes on retry)
3. **Decoupled HXO↔Autonomy**: Uses Genesis signals instead of direct imports
4. **Extended Topic Registry**: New topics for TDE orchestrator and autonomy tuning

## Breaking Changes

**None** - This is a backward-compatible fix.

Legacy function-based APIs (`register_hxo_genesis_link`, `notify_autotune_signal`) are preserved for compatibility.

## Migration Steps

### If You Use the Default Setup

No action needed. The fix is automatic on deployment.

### If You Have Custom HXO Integration

Replace direct adapter calls with the new `register_hxo_links` helper:

**Before:**
```python
from bridge_backend.bridge_core.engines.adapters.hxo_genesis_link import register_hxo_genesis_link
await register_hxo_genesis_link()
```

**After:**
```python
from bridge_backend.bridge_core.engines.adapters.genesis_link import register_hxo_links
await register_hxo_links(genesis_bus, hxo)
```

## New Topics

The following Genesis topics are now available:

- `deploy.tde.orchestrator.completed` - TDE deployment completion
- `deploy.tde.orchestrator.failed` - TDE deployment failure
- `autonomy.tuning.signal` - HXO→Autonomy auto-tuning signals

## Deployment Checklist

1. ✅ Deploy to Render
2. ✅ Monitor logs for: `[HXO Genesis Link] ✅ Registration established`
3. ✅ Monitor logs for: `[HXO-Autonomy Link] ✅ Link established`
4. ❌ No red errors from adapter registration

## Config Changes

**None required** - All changes are backward-compatible.

## Testing

Optional: Emit a test event to verify HXO is consuming TDE signals:

```bash
curl -X POST "$API_BASE/api/genesis/publish" \
  -d '{"topic":"deploy.tde.orchestrator.completed","payload":{"pr":"test"}}' \
  -H 'Content-Type: application/json'
```

You should see HXO consume it cleanly without errors.
