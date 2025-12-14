# Autonomy Operations Guide

**Version:** v1.9.6s  
**Audience:** Operators, SREs, Admirals

---

## Quick Start

### Check Status

```bash
# Via CLI
python3 -m bridge_backend.cli.autonomyctl status

# Via API
curl https://your-api.com/api/autonomy/status \
  -H "Authorization: Bearer <token>"
```

### Submit Manual Incident

```bash
# Via CLI
python3 -m bridge_backend.cli.autonomyctl incident \
  --kind deploy.netlify.preview_failed \
  --source cli

# Via API
curl -X POST https://your-api.com/api/autonomy/incident \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"kind":"deploy.netlify.preview_failed","source":"manual"}'
```

### Trigger Specific Action

```bash
# Via API
curl -X POST https://your-api.com/api/autonomy/trigger \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"action":"SYNC_ENVS","reason":"manual_sync"}'
```

---

## Circuit Breaker Control

### Open Circuit (Disable Auto-Healing)

```bash
# Via CLI
python3 -m bridge_backend.cli.autonomyctl circuit --open

# Via API
curl -X POST https://your-api.com/api/autonomy/circuit?action=open \
  -H "Authorization: Bearer <token>"
```

This will cause all future decisions to return `ESCALATE` instead of taking autonomous action.

### Close Circuit (Re-enable Auto-Healing)

```bash
# Via CLI
python3 -m bridge_backend.cli.autonomyctl circuit --close

# Via API
curl -X POST https://your-api.com/api/autonomy/circuit?action=close \
  -H "Authorization: Bearer <token>"
```

**Note:** Circuit state is currently in-memory only. Restarting the service will reset the circuit.

---

## Observability

### Check Genesis Event History

```bash
curl https://your-api.com/api/genesis/history?limit=50
```

Look for:
- `autonomy.heal.applied` - Successful healing actions
- `autonomy.heal.error` - Failed healing actions
- `autonomy.circuit.open` - Circuit breaker opened
- `autonomy.circuit.closed` - Circuit breaker closed

### Monitor Logs

```bash
# On Render
render logs -t bridge

# Filter for autonomy events
render logs -t bridge | grep "\\[Governor\\]"
render logs -t bridge | grep "\\[Autonomy Genesis\\]"
```

Key log patterns:
```
[Governor] Decision: REPAIR_CONFIG (preview_failed)
[Governor] Execution: applied, certified=True
[Autonomy Genesis] Netlify preview failed event received
```

---

## Common Scenarios

### Scenario 1: Netlify Preview Keeps Failing

**Symptom:** Repeated `deploy.netlify.preview_failed` incidents

**What Happens:**
1. First failure → `REPAIR_CONFIG` action
2. Second failure (within cooldown) → `NOOP` (cooldown)
3. Third failure (after cooldown) → `REPAIR_CONFIG` again
4. If 3 repairs fail → Circuit breaker trips → All actions become `ESCALATE`

**Operator Action:**
1. Check Chimera logs for config repair attempts
2. Manually inspect `netlify.toml`, `_headers`, `_redirects`
3. If needed, open circuit to prevent further auto-actions
4. Fix root cause manually
5. Close circuit to resume autonomous healing

### Scenario 2: Environment Drift Detected

**Symptom:** `envrecon.drift` event published

**What Happens:**
1. Governor decides `SYNC_ENVS`
2. EnvRecon syncs missing/drifted variables
3. Truth certifies the sync
4. If certified → Fail streak resets
5. If not certified → Fail streak increments

**Operator Action:**
- Check EnvRecon logs to see which vars were synced
- Verify sensitive vars weren't overwritten
- If something broke, manually revert via EnvRecon UI or CLI

### Scenario 3: Rate Limit Reached

**Symptom:** All decisions return `NOOP (rate_limited)`

**What Happens:**
- Governor has taken 6 actions in the last hour
- All new incidents return `NOOP` until window clears

**Operator Action:**
1. Check what's causing so many incidents
2. Fix root cause to stop incident flood
3. If urgent, can manually trigger actions via `/api/autonomy/trigger` (still rate limited)
4. Alternatively, increase `AUTONOMY_MAX_ACTIONS_PER_HOUR` (not recommended in production)

### Scenario 4: Circuit Breaker Tripped

**Symptom:** All decisions return `ESCALATE (circuit_breaker_tripped)`

**What Happens:**
- 3 consecutive healing actions failed certification
- Governor stops taking autonomous actions
- Requires manual intervention

**Operator Action:**
1. Review Genesis event history for the 3 failed heals
2. Identify root cause (broken engine, bad config, etc.)
3. Fix the underlying issue
4. Close the circuit to resume autonomy
5. Monitor next few incidents to ensure healing works

---

## Safety Best Practices

### 1. Monitor Genesis Events

Set up alerts for:
- `autonomy.heal.error` - Something failed
- `autonomy.circuit.open` - Circuit breaker tripped

### 2. Start Conservative

Default limits are intentionally conservative:
- 6 actions/hour prevents runaway healing
- 5-minute cooldown prevents thrashing
- 3-failure circuit prevents repeated bad actions

Only increase these after observing stable autonomous behavior.

### 3. Test in Staging First

Before enabling in production:
1. Deploy to staging with `AUTONOMY_ENABLED=true`
2. Trigger test incidents
3. Verify decisions and actions are correct
4. Confirm Truth certification works

### 4. Manual Override Available

Autonomy never prevents manual intervention. Operators can always:
- Open circuit to disable autonomy
- Manually trigger specific actions
- Directly use Chimera, ARIE, EnvRecon

---

## Troubleshooting

### Problem: Incidents Not Being Handled

**Check:**
1. `AUTONOMY_ENABLED=true` in environment
2. Genesis bus is enabled (`GENESIS_MODE=enabled`)
3. Genesis links registered (check startup logs)
4. Incident `kind` matches policy matrix

**Debug:**
```bash
# Check if autonomy routes are loaded
curl https://your-api.com/api/autonomy/status

# Check Genesis bus status
curl https://your-api.com/api/genesis/health

# Manually submit test incident
python3 -m bridge_backend.cli.autonomyctl incident --kind deploy.netlify.preview_failed
```

### Problem: Actions Not Executing

**Check:**
1. Rate limit not reached (check window size in logs)
2. Not in cooldown period
3. Circuit breaker not tripped
4. Required engine available (Chimera, ARIE, EnvRecon)

**Debug:**
```bash
# Check status
python3 -m bridge_backend.cli.autonomyctl status

# Try manual trigger
curl -X POST https://your-api.com/api/autonomy/trigger \
  -H "Authorization: Bearer <token>" \
  -d '{"action":"NOOP","reason":"test"}'
```

### Problem: Truth Certification Failing

**Check:**
1. Truth engine configured and available
2. Truth has proper permissions
3. Report structure matches Truth expectations

**Debug:**
```bash
# Check Truth engine status
curl https://your-api.com/api/engines/truth/status

# Review Genesis event history for certification failures
curl https://your-api.com/api/genesis/history | grep "certified"
```

---

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTONOMY_ENABLED` | `true` | Enable autonomy engine |
| `AUTONOMY_MAX_ACTIONS_PER_HOUR` | `6` | Rate limit threshold |
| `AUTONOMY_COOLDOWN_MINUTES` | `5` | Cooldown between actions |
| `AUTONOMY_FAIL_STREAK_TRIP` | `3` | Circuit breaker threshold |
| `PUBLIC_API_BASE` | *(required)* | API base URL for webhooks |
| `AUTONOMY_API_TOKEN` | *(required)* | API token for CI integration |

---

## Support

For issues or questions:
1. Check logs for `[Governor]` and `[Autonomy Genesis]` entries
2. Review Genesis event history
3. Consult `AUTONOMY_DECISION_LAYER.md` for architecture details
4. Open GitHub issue with logs and event history
