# Umbra Triage Mesh - Migration Guide

## Overview

This guide explains how the existing triage systems (Triage Hospital, HealthNet, and standalone triage scripts) have been unified into the Umbra Triage Mesh.

## What Changed

### Before (v1.9.6 and earlier)

**Fragmented Triage**:
- **Triage Hospital**: Database-backed ticket system for manual issue tracking
- **HealthNet**: Health probe system with separate alerting
- **API Triage**: Standalone scripts in `bridge_backend/scripts/api_triage.py`
- **Endpoint Triage**: Separate `endpoint_triage.py` script
- **Hooks Triage**: Individual `hooks_triage.py` script
- **Deploy Triage**: Scattered across autonomy and chimera engines

Each system had:
- Its own data model
- Separate alerting mechanisms
- Different healing approaches
- No unified correlation

### After (v1.9.7k)

**Unified Triage Mesh**:
- **Single Core**: `UmbraTriageCore` handles all signal ingestion
- **Automatic Correlation**: Related incidents grouped into tickets
- **Unified Healing**: `UmbraHealers` delegates to appropriate engines
- **Genesis Integration**: All events flow through event bus
- **Consolidated Reports**: Single JSON report format

## Migration Path

### Phase 1: Parallel Operation (Recommended)

Run Umbra alongside existing systems to verify behavior:

1. Enable Umbra in intent-only mode:
   ```bash
   UMBRA_ENABLED=true
   UMBRA_ALLOW_HEAL=false
   ```

2. Keep existing triage systems active

3. Compare results:
   - Umbra tickets vs Triage Hospital tickets
   - HealthNet alerts vs Umbra runtime signals
   - Healing recommendations

4. Duration: 1-2 weeks

### Phase 2: Gradual Cutover

Migrate one surface at a time:

1. **Deploy Triage** (Week 1):
   - Configure Netlify/Render webhooks
   - Verify Umbra ingests deploy signals
   - Disable old deploy triage scripts

2. **API/Endpoint Triage** (Week 2):
   - Route HealthNet failures to Umbra
   - Verify API signals correlation
   - Disable `api_triage.py` and `endpoint_triage.py`

3. **Build Triage** (Week 3):
   - Configure GitHub webhook
   - Verify build failure signals
   - Update CI workflows

4. **Runtime Triage** (Week 4):
   - Route HealthNet probes to Umbra
   - Verify runtime signal handling
   - Fully deprecate Triage Hospital

### Phase 3: Enable Autonomous Healing

Once confident in signal processing:

1. Enable healing in dev/staging:
   ```bash
   UMBRA_ALLOW_HEAL=true
   ```

2. Monitor for 1 week

3. Enable in production with strict RBAC:
   ```bash
   UMBRA_ALLOW_HEAL=true
   UMBRA_RBAC_MIN_ROLE=admiral
   UMBRA_PARITY_STRICT=true
   ```

## Data Migration

### Triage Hospital → Umbra

If you have existing Triage Hospital tickets:

```python
# Migration script (example)
from bridge_backend.triage_hospital.models import TriageTicket as OldTicket
from bridge_backend.engines.umbra.core import UmbraTriageCore
from bridge_backend.engines.umbra.models import TriageTicket, Incident, TriageSeverity, TriageKind

async def migrate_tickets():
    umbra = UmbraTriageCore()
    old_tickets = await OldTicket.get_all()
    
    for old_ticket in old_tickets:
        # Create Umbra incident
        signal = {
            "kind": map_kind(old_ticket.category),
            "source": old_ticket.source or "legacy",
            "message": old_ticket.description,
            "severity": map_severity(old_ticket.priority),
            "metadata": {
                "migrated_from": old_ticket.id,
                "original_created_at": old_ticket.created_at.isoformat()
            }
        }
        
        await umbra.ingest_signal(signal)

def map_kind(category: str) -> str:
    mapping = {
        "deploy": "deploy",
        "api": "api",
        "endpoint": "endpoint",
        "runtime": "runtime",
        "build": "build"
    }
    return mapping.get(category, "runtime")

def map_severity(priority: str) -> str:
    mapping = {
        "critical": "critical",
        "high": "high",
        "medium": "warning",
        "low": "info"
    }
    return mapping.get(priority, "info")
```

### HealthNet → Umbra

HealthNet probes can emit directly to Umbra:

```python
# In your health probe code
from bridge_backend.engines.umbra.core import UmbraTriageCore

async def on_health_check_failure(endpoint: str, error: dict):
    umbra = UmbraTriageCore()
    
    signal = {
        "kind": "runtime",
        "source": "healthnet",
        "message": f"Health check failed: {endpoint}",
        "severity": "critical" if error.get("consecutive_failures", 0) > 3 else "warning",
        "metadata": {
            "endpoint": endpoint,
            "error": error,
            "consecutive_failures": error.get("consecutive_failures", 0)
        }
    }
    
    await umbra.ingest_signal(signal)
```

## API Changes

### Deprecated Endpoints

These endpoints are being phased out:

- `/api/triage/tickets` → Use `/api/umbra/tickets`
- `/api/healthnet/alerts` → Now part of Umbra runtime signals
- `/api/deploy/triage` → Use `/webhooks/*` or `/api/umbra/signal`

### New Endpoints

- `POST /api/umbra/signal` - Ingest any signal
- `GET /api/umbra/tickets` - List all tickets
- `POST /api/umbra/run` - Run triage sweep
- `GET /api/umbra/reports` - Get triage reports

### Webhook Routes

New webhook routes for external systems:

- `POST /webhooks/render` - Render deploy events
- `POST /webhooks/netlify` - Netlify deploy events
- `POST /webhooks/github` - GitHub workflow events

## Configuration Changes

### Old Configuration

```bash
# Triage Hospital
TRIAGE_ENABLED=true
TRIAGE_AUTO_REPAIR=true

# HealthNet
HEALTHNET_ENABLED=true
HEALTHNET_ALERT_THRESHOLD=3

# Deploy Triage
DEPLOY_TRIAGE_ENABLED=true
```

### New Configuration

```bash
# Unified Umbra
UMBRA_ENABLED=true
UMBRA_ALLOW_HEAL=false
UMBRA_HEALTH_ERROR_THRESHOLD=5
UMBRA_HEALTH_WARN_THRESHOLD=2
UMBRA_PARITY_STRICT=true
UMBRA_RBAC_MIN_ROLE=admiral

# Webhook secrets
RENDER_WEBHOOK_SECRET=your_secret
NETLIFY_DEPLOY_WEBHOOK_SECRET=your_secret
GITHUB_WEBHOOK_SECRET=your_secret
```

## Code Changes

### Emitting Triage Signals

**Old way** (direct to Triage Hospital):
```python
from bridge_backend.triage_hospital import create_ticket

await create_ticket(
    category="deploy",
    description="Netlify deploy failed",
    priority="critical"
)
```

**New way** (via Umbra):
```python
from bridge_backend.engines.umbra.core import UmbraTriageCore

umbra = UmbraTriageCore()
await umbra.ingest_signal({
    "kind": "deploy",
    "source": "netlify",
    "message": "Deploy failed",
    "severity": "critical",
    "metadata": {"deploy_id": "12345"}
})
```

**Best way** (via Genesis):
```python
from bridge_backend.genesis.bus import genesis_bus

await genesis_bus.publish("triage.signal.deploy", {
    "source": "netlify",
    "message": "Deploy failed",
    "severity": "critical",
    "metadata": {"deploy_id": "12345"}
})
```

## Testing Migration

### Verify Signal Ingestion

```bash
# Send test signal
curl -X POST http://localhost:8000/api/umbra/signal \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "deploy",
    "source": "test",
    "message": "Test signal",
    "severity": "info"
  }'

# Check tickets
curl http://localhost:8000/api/umbra/tickets
```

### Verify Webhook Processing

```bash
# Test Netlify webhook
curl -X POST http://localhost:8000/webhooks/netlify \
  -H "Content-Type: application/json" \
  -d '{
    "name": "deploy-failed",
    "site_name": "test-site",
    "state": "error"
  }'

# Check if incident was created
curl http://localhost:8000/api/umbra/tickets
```

### Verify Heal Plan Generation

```bash
# Run triage sweep
curl -X POST http://localhost:8000/api/umbra/run \
  -H "Content-Type: application/json" \
  -d '{"timeout": 90, "heal": false}'

# Check for heal plans
curl http://localhost:8000/api/umbra/reports/latest
```

## Rollback Plan

If you need to roll back to old systems:

1. Set `UMBRA_ENABLED=false`
2. Re-enable old triage systems:
   ```bash
   TRIAGE_ENABLED=true
   HEALTHNET_ENABLED=true
   ```
3. Restart application
4. Old routes will take over again

**Note**: Umbra routes remain available but return 503 when disabled.

## Common Issues

### Issue: Duplicate Tickets

**Cause**: Both old and new systems creating tickets

**Solution**: Disable old system or run in read-only mode during migration

### Issue: Webhooks Not Working

**Cause**: Missing webhook secrets or HMAC verification failing

**Solution**: 
1. Set webhook secrets in environment
2. Or set `UMBRA_ALLOW_UNVERIFIED_WEBHOOKS=true` (not for prod)

### Issue: No Heal Plans Generated

**Cause**: Umbra doesn't recognize the signal pattern

**Solution**: Check `UmbraTriageCore._generate_heal_plan()` and add your pattern

### Issue: Parity Checks Failing

**Cause**: Strict parity mode enabled but environments differ

**Solution**: Fix environment drift or set `UMBRA_PARITY_STRICT=false` temporarily

## Timeline Summary

**Week 1-2**: Parallel operation, data comparison
**Week 3-4**: Gradual cutover, surface by surface  
**Week 5-6**: Full Umbra operation, intent-only mode
**Week 7+**: Enable autonomous healing with monitoring

## Support

If you encounter issues during migration:

1. Check logs in `bridge_backend/logs/umbra_reports/`
2. Review Genesis events for `triage.*` topics
3. Use `umbractl` CLI for diagnostics
4. Fall back to old systems if needed

## Post-Migration Cleanup

After successful migration (2+ weeks stable):

1. Remove old triage scripts from `bridge_backend/scripts/`
2. Archive Triage Hospital database
3. Remove HealthNet alerting code
4. Update documentation
5. Clean up deprecated API endpoints
