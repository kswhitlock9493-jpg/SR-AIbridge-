# Autonomy v1.9.6t - Quick Reference

## What's New in v1.9.6t?

**The Living Bridge** - A fully autonomous, self-evolving system that heals, learns, predicts, and certifies its own actions.

### 🆕 New Features

1. **Reinforcement Scoring** - Dynamic policy weights based on engine performance
2. **Leviathan Prediction** - Success probability forecasting before execution
3. **Truth Certificates** - Cryptographic proof for every healing action
4. **Blueprint Evolution** - Automated policy updates based on outcomes
5. **GitHub EnvSync** - Automatic secret and variable management
6. **3 New Actions** - CREATE_SECRET, REGENERATE_CONFIG, SYNC_AND_CERTIFY

## Quick Start

### Enable Autonomy

```bash
export AUTONOMY_ENABLED=true
export AUTONOMY_API_TOKEN=your_token_here
export PUBLIC_API_BASE=https://your-api.com
```

### Trigger Manual Healing

```bash
curl -X POST "$PUBLIC_API_BASE/api/autonomy/incident" \
  -H "Authorization: Bearer $AUTONOMY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"kind":"deploy.failure","source":"manual"}'
```

### View Certificates

```bash
ls .bridge/logs/certificates/
cat .bridge/logs/certificates/*.json | jq
```

## Decision Matrix

| Incident Type | Action | Engine | Certificate |
|---------------|--------|--------|-------------|
| `deploy.netlify.preview_failed` | REPAIR_CONFIG | Chimera | ✅ |
| `deploy.render.failed` | RETRY | Chimera | ✅ |
| `envrecon.drift` | SYNC_ENVS | EnvRecon | ✅ |
| `arie.deprecated.detected` | REPAIR_CODE | ARIE | ✅ |
| `github.secret.missing` | CREATE_SECRET | HubSync | ✅ |
| `config.outdated` | REGENERATE_CONFIG | Chimera | ✅ |
| `deploy.failure` | SYNC_AND_CERTIFY | EnvRecon+Truth | ✅ |

## Safety Guardrails

```python
# Rate Limiting: 6 actions/hour
AUTONOMY_MAX_ACTIONS_PER_HOUR=6

# Cooldown: 5 minutes between actions
AUTONOMY_COOLDOWN_MINUTES=5

# Circuit Breaker: trips after 3 failures
AUTONOMY_FAIL_STREAK_TRIP=3
```

## Reinforcement Scoring

```python
score = success_rate(engine) - cooldown_penalty()

# Example:
# - ARIE success rate: 0.85
# - Cooldown penalty: 0.10 (2 min since last action)
# - Final score: 0.75
```

## Leviathan Prediction

```python
predicted_success = leviathan.predict({
    "action": "REPAIR_CONFIG",
    "fail_streak": 1,
    "report_status": "success"
})

# Returns: 0.0 to 1.0
# Warning threshold: < 0.3
```

## Certificate Format

```json
{
  "timestamp": "2025-10-12T03:00:00Z",
  "action": "REPAIR_CONFIG",
  "reason": "preview_failed",
  "targets": ["netlify"],
  "certified": true,
  "report_hash": "abc123...",
  "certificate_hash": "def456..."
}
```

## GitHub Workflows

### bridge_autonomy.yml
- **Trigger**: Deployment failure
- **Action**: Post incident to API
- **When**: Build & Deploy workflow fails

### env_sync.yml
- **Trigger**: Hourly cron + manual
- **Action**: Audit → Sync → Commit
- **Updates**: `.github/environment.json`

## Environment Config

See `.github/environment.json` for all variables:

```json
{
  "AUTONOMY_ENABLED": "Enables self-healing",
  "AUTONOMY_API_TOKEN": "API auth token",
  "PUBLIC_API_BASE": "API endpoint",
  "GITHUB_TOKEN": "For secret creation",
  "BLUEPRINT_MODE": "predictive or adaptive",
  "TRUTH_API_KEY": "Certificate validation"
}
```

## Integration Flow

```
1. Incident → Genesis Bus
2. Governor → Reinforcement Score
3. Leviathan → Predict Success
4. Engine → Execute Action
5. Truth → Certify + Generate Certificate
6. Blueprint → Update Policy
7. Governor → Update Success Rates
8. Genesis → Publish Events
```

## Engine Success Rates

Tracked dynamically with exponential moving average:

```python
# Initial rates:
ARIE:     0.85
Chimera:  0.90
EnvRecon: 0.95
Truth:    0.99

# Updated after each action:
new_rate = current * 0.9 + (1.0 if success else 0.0) * 0.1
```

## Testing

```bash
# Run all v1.9.6t tests
pytest bridge_backend/tests/test_autonomy_v196t.py -v

# Run original tests (backward compatibility)
pytest bridge_backend/tests/test_autonomy_governor.py -v

# Run all autonomy tests
pytest bridge_backend/tests/test_autonomy*.py -v
```

## API Endpoints

```bash
# Emit incident
POST /api/autonomy/incident
{
  "kind": "deploy.failure",
  "source": "github",
  "details": {"workflow": "build-deploy"}
}

# Get governor status
GET /api/autonomy/status

# Get recent certificates
GET /api/autonomy/certificates
```

## Common Tasks

### Force Environment Sync

```bash
cd bridge_backend
python -m cli.genesisctl env audit
python -m cli.genesisctl env sync --target github --from-platform render
```

### View Predictions

```bash
cat bridge_backend/blueprint/cache/predictions.json
```

### Check Circuit Breaker Status

```python
from bridge_backend.engines.autonomy.governor import AutonomyGovernor

gov = AutonomyGovernor()
print(f"Fail streak: {gov.fail_streak}")
print(f"Circuit breaker will trip at: {gov.fail_streak_trip}")
```

### Reset Governor State

```python
gov.fail_streak = 0
gov.window = []
gov.last_action_at = None
```

## Troubleshooting

### Autonomy not triggering?

1. Check `AUTONOMY_ENABLED=true`
2. Verify `AUTONOMY_API_TOKEN` is set
3. Check Genesis Bus is enabled
4. Review governor logs

### Circuit breaker tripped?

```python
# Check fail streak
if gov.fail_streak >= 3:
    # Manual reset required or wait for cooldown
    gov.fail_streak = 0
```

### Low prediction scores?

- Check recent failures
- Review engine success rates
- Consider manual intervention

### Certificates not generating?

- Ensure `.bridge/logs/certificates/` directory exists
- Check Truth Engine availability
- Review file permissions

## File Locations

```
.bridge/logs/certificates/        # Healing certificates
.github/environment.json          # Environment config
.github/workflows/                # Autonomy workflows
bridge_backend/config/policy/     # Policy weights
bridge_backend/blueprint/cache/   # Predictions
```

## Version Compatibility

- **v1.9.6s** → **v1.9.6t**: ✅ Fully backward compatible
- All existing tests pass
- No breaking changes
- New features are opt-in via incident types

## Next Steps

1. Review certificates after first healing action
2. Monitor engine success rates
3. Adjust policy weights based on prediction accuracy
4. Enable Blueprint adaptive mode
5. Set up alerting for circuit breaker trips

## Resources

- Full docs: `AUTONOMY_V196T_IMPLEMENTATION.md`
- String theory map: `bridge_backend/config/string_theory_map_v196t.json`
- Tests: `bridge_backend/tests/test_autonomy_v196t.py`
- Workflows: `.github/workflows/bridge_autonomy.yml`, `env_sync.yml`
