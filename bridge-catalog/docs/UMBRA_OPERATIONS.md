# Umbra Triage Mesh - Operations Guide

## Operating Modes

### Intent-Only Mode (Default)
- `UMBRA_ALLOW_HEAL=false`
- Generates heal plans but doesn't execute them
- Safe for production without Admiral approval
- Perfect for understanding what Umbra would do

### Autonomous Mode
- `UMBRA_ALLOW_HEAL=true`
- Executes heal plans automatically
- Requires Truth certification
- RBAC-gated (Admiral-only by default)
- Used in CI/CD for self-healing

## RBAC Enforcement

### Role Requirements

**Admiral** (Full Access):
- View all tickets and reports
- Execute heal plans
- Configure Umbra settings
- Access all API endpoints

**Captain** (Read/Report):
- View tickets and reports
- Generate heal plans (intent-only)
- No execution permissions

**Observer** (Read-Only):
- View tickets and reports only
- No modifications allowed

### Endpoint Permissions

```
GET  /api/umbra/status          → All roles
GET  /api/umbra/tickets         → Admiral, Captain, Observer
GET  /api/umbra/tickets/{id}    → Admiral, Captain, Observer
POST /api/umbra/signal          → Admiral, Captain
POST /api/umbra/run             → Admiral only
POST /api/umbra/tickets/{id}/action → Admiral only
GET  /api/umbra/reports         → Admiral, Captain, Observer
```

## Heal Policies

### Standard Policy (Default)
- Truth certification required
- Parity prechecks enforced
- Rollback on failure
- Audit trail maintained

### Relaxed Policy
- Truth certification optional
- Parity warnings (not blocking)
- No automatic rollback
- Use with caution

### Strict Policy
- Multiple Truth certifications
- Strict parity enforcement
- Mandatory rollback testing
- Extended audit trail

## CLI Operations

### Running a Triage Sweep

```bash
# Intent-only mode (generates plans but doesn't execute)
python3 -m bridge_backend.cli.umbractl run --report

# With healing enabled
export UMBRA_ALLOW_HEAL=true
python3 -m bridge_backend.cli.umbractl run --heal --report --timeout 120
```

### Managing Tickets

```bash
# List all tickets
python3 -m bridge_backend.cli.umbractl tickets

# List open tickets only
python3 -m bridge_backend.cli.umbractl tickets --status open

# View specific ticket
python3 -m bridge_backend.cli.umbractl ticket UM-2025-10-12-0001

# Close a ticket
python3 -m bridge_backend.cli.umbractl ticket UM-2025-10-12-0001 --action close

# Heal a ticket
python3 -m bridge_backend.cli.umbractl ticket UM-2025-10-12-0001 --action heal
```

### Viewing Reports

```bash
# View latest report summary
python3 -m bridge_backend.cli.umbractl report --latest

# View all reports as JSON
python3 -m bridge_backend.cli.umbractl report --format json
```

## API Operations

### Ingest a Signal

```bash
curl -X POST http://localhost:8000/api/umbra/signal \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "deploy",
    "source": "netlify",
    "message": "Deploy failed",
    "severity": "critical",
    "metadata": {"deploy_id": "12345"}
  }'
```

### Run Triage Sweep

```bash
curl -X POST http://localhost:8000/api/umbra/run \
  -H "Content-Type: application/json" \
  -d '{
    "timeout": 90,
    "heal": false
  }'
```

### List Tickets

```bash
curl http://localhost:8000/api/umbra/tickets
curl http://localhost:8000/api/umbra/tickets?status=open
```

### Get Ticket Details

```bash
curl http://localhost:8000/api/umbra/tickets/UM-2025-10-12-0001
```

### Execute Heal Action

```bash
curl -X POST http://localhost:8000/api/umbra/tickets/UM-2025-10-12-0001/action \
  -H "Content-Type: application/json" \
  -d '{"action": "heal"}'
```

## Webhook Configuration

### Netlify Webhook

1. In Netlify dashboard, go to Site Settings → Build & Deploy → Deploy notifications
2. Add "Outgoing webhook"
3. Event: Deploy failed, Deploy succeeded, Deploy building
4. URL: `https://your-backend.onrender.com/webhooks/netlify`
5. (Optional) Set webhook secret in environment: `NETLIFY_DEPLOY_WEBHOOK_SECRET`

### Render Webhook

1. In Render dashboard, go to your service → Settings → Webhooks
2. Add webhook
3. URL: `https://your-backend.onrender.com/webhooks/render`
4. Events: Deploy started, Deploy failed, Deploy succeeded
5. (Optional) Set webhook secret in environment: `RENDER_WEBHOOK_SECRET`

### GitHub Webhook

1. In GitHub repo, go to Settings → Webhooks → Add webhook
2. Payload URL: `https://your-backend.onrender.com/webhooks/github`
3. Content type: application/json
4. Events: Workflow runs, Check suites, Deployment statuses
5. (Optional) Set webhook secret in environment: `GITHUB_WEBHOOK_SECRET`

**Note**: If webhook secrets are not configured, set `UMBRA_ALLOW_UNVERIFIED_WEBHOOKS=true` (not recommended for production).

## Rollback Procedures

### Automatic Rollback

Umbra automatically rolls back if:
- Heal action fails
- Parity postchecks fail
- Truth certification fails after execution

Rollback process:
1. Emit `triage.heal.rollback` event
2. Restore previous state (if applicable)
3. Mark ticket as failed
4. Log rollback reason

### Manual Rollback

If you need to manually roll back:

```bash
# Close the failed ticket
python3 -m bridge_backend.cli.umbractl ticket {ticket_id} --action close

# Review the failed actions
python3 -m bridge_backend.cli.umbractl ticket {ticket_id}

# If needed, manually revert changes using Chimera/Cascade/Autonomy
```

## Monitoring & Observability

### Health Metrics

```bash
curl http://localhost:8000/api/umbra/status
```

Returns:
- Total tickets, open tickets
- Total incidents
- Total reports
- Configuration status

### Genesis Events

Monitor Genesis bus for real-time events:
- `triage.ticket.open` - New ticket created
- `triage.ticket.update` - Ticket updated
- `triage.heal.intent` - Heal plan generated
- `triage.heal.applied` - Heal executed successfully
- `triage.heal.rollback` - Heal rolled back
- `triage.alert` - Critical alert
- `triage.report` - Sweep report completed

### Log Files

Reports saved to:
- `bridge_backend/logs/umbra_reports/{report_id}.json`
- `bridge_backend/logs/umbra_reports/latest.json`

## Troubleshooting

### Issue: Webhooks not being ingested

**Solution**:
1. Check webhook secret configuration
2. Verify `UMBRA_ALLOW_UNVERIFIED_WEBHOOKS` if no secret
3. Check logs for signature verification errors
4. Ensure RBAC allows webhook endpoint access

### Issue: Heal plans not executing

**Solution**:
1. Verify `UMBRA_ALLOW_HEAL=true`
2. Check RBAC role (must be Admiral)
3. Review Truth certification logs
4. Check Parity precheck results

### Issue: Tickets not being correlated

**Solution**:
1. Verify signals have matching kind and source
2. Check time window (5 minutes by default)
3. Review correlation logic in logs

### Issue: CI workflow not commenting on PR

**Solution**:
1. Verify workflow has `pull-requests: write` permission
2. Check that summary files are being generated
3. Review GitHub Actions logs
4. Ensure `actions/github-script@v7` is working

## Best Practices

1. **Start in Intent-Only Mode**: Understand what Umbra would do before enabling autonomous healing
2. **Monitor Genesis Events**: Use event bus to track all triage activity
3. **Review Reports Regularly**: Check `latest.json` for trends
4. **Set Appropriate Thresholds**: Tune `ERROR_THRESHOLD` and `WARN_THRESHOLD` for your environment
5. **Use Webhook Secrets**: Always configure webhook secrets in production
6. **Enable Parity Strict**: Keep `UMBRA_PARITY_STRICT=true` for safety
7. **Maintain RBAC**: Keep heal execution Admiral-only
8. **Test Rollbacks**: Periodically verify rollback procedures work
9. **Archive Reports**: Move old reports to long-term storage
10. **Document Custom Heal Actions**: If you extend Umbra, document your actions

## Emergency Procedures

### Disable Umbra Completely

```bash
export UMBRA_ENABLED=false
# Restart application
```

### Disable Only Healing

```bash
export UMBRA_ALLOW_HEAL=false
# Restart application or wait for config reload
```

### Clear All Tickets

```bash
# Use CLI or API to close all tickets
python3 -m bridge_backend.cli.umbractl tickets --status open | \
  grep UM- | \
  xargs -I {} python3 -m bridge_backend.cli.umbractl ticket {} --action close
```

### Force Genesis Re-registration

```bash
# Restart the application
# Genesis links will re-register automatically on startup
```

## Performance Tuning

### Timeout Adjustment

```bash
# For faster environments
export UMBRA_RUN_TIMEOUT=60

# For slower environments
export UMBRA_RUN_TIMEOUT=180
```

### Correlation Window

Currently hardcoded to 5 minutes. To adjust, modify `UmbraTriageCore._is_related()` in `core.py`.

### Batch Processing

For high-volume signal ingestion, consider batching:
1. Collect signals over short period
2. Process in bulk
3. Generate fewer, more comprehensive tickets

## Integration with Other Systems

### Steward
Umbra can emit events to Steward for unified observability.

### ARIE
ARIE repository checks can trigger triage signals.

### EnvRecon
Environment drift can create triage tickets automatically.

### Chimera
Deploy healing delegates to Chimera for config regeneration.
