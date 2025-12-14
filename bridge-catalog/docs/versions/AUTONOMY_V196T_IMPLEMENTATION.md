# Autonomy v1.9.6t — The Living Bridge

## Overview

Version 1.9.6t builds upon v1.9.6s to create a fully autonomous, self-evolving, and self-healing system that:

1. **Heals itself** - Detects and fixes problems automatically
2. **Learns from experience** - Updates policies based on success/failure
3. **Predicts outcomes** - Uses Leviathan to forecast action success
4. **Certifies actions** - Generates cryptographic proof for every fix
5. **Syncs with GitHub** - Automatically manages secrets and environment variables
6. **Evolves its policies** - Blueprint engine updates decision weights

## Architecture

```
[Incident] 
   ↓
[Genesis Bus] — emits → [Autonomy Governor]
   ↓
[Decision Layer with Reinforcement Scoring]
   ↳ ARIE (Code Fix)
   ↳ Chimera (Config/Deploy Heal)
   ↳ EnvRecon + Steward (Env Sync)
   ↳ GitHubEnvSync (Repo Vars + Secrets)
   ↳ Truth Engine (Certify + Certificate)
   ↳ Blueprint (Predictive Reinforcement)
   ↳ Leviathan (Simulation & Forecast)
```

## New Features

### 1. Reinforcement Scoring

The Governor now scores each action based on:
- Engine success rate (tracked dynamically)
- Cooldown penalty (time since last action)
- Historical performance

```python
score = success_rate(engine) - cooldown_penalty()
```

### 2. New Actions

Three new autonomous actions:

- **CREATE_SECRET** - Automatically creates missing GitHub secrets
- **REGENERATE_CONFIG** - Refreshes platform configurations
- **SYNC_AND_CERTIFY** - Syncs environment and certifies the result

### 3. Leviathan Prediction

Before executing an action, Leviathan predicts success probability:

```python
predicted_success = await _predict_success(decision, report)
if predicted_success < 0.3:
    logger.warning("Low success probability, but proceeding")
```

### 4. Truth Engine Certificates

Every healing action generates a cryptographic certificate:

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

Certificates are stored in `.bridge/logs/certificates/`

### 5. Blueprint Policy Evolution

The Blueprint engine receives feedback after each action and can update decision weights:

```python
await _update_blueprint_policy(decision, success=True)
```

This enables the system to learn which actions work best for specific incident types.

### 6. Engine Success Rate Tracking

The Governor tracks success rates for each engine using exponential moving average:

```python
new_rate = current_rate * 0.9 + (1.0 if success else 0.0) * 0.1
```

## GitHub Workflows

### bridge_autonomy.yml

Triggers self-healing on deployment failures:

```yaml
on:
  workflow_run:
    workflows: ["Build & Deploy"]
    types:
      - completed
  workflow_dispatch:
```

Posts incidents to the Autonomy API when builds fail.

### env_sync.yml

Hourly environment synchronization:

```yaml
on:
  schedule:
    - cron: "0 * * * *"
  workflow_dispatch:
```

Automatically:
1. Audits environment drift
2. Syncs missing variables to GitHub
3. Updates `.github/environment.json`
4. Commits changes back to the repository

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AUTONOMY_ENABLED` | Enables self-healing system | Yes |
| `AUTONOMY_API_TOKEN` | Auth key for API-triggered incidents | Yes |
| `PUBLIC_API_BASE` | API base URL | Yes |
| `GITHUB_TOKEN` | For secret creation | Yes |
| `GITHUB_REPOSITORY` | Owner/repo for GitHub API calls | Yes |
| `FEDERATION_SYNC_KEY` | Cross-engine handshake key | No |
| `BLUEPRINT_MODE` | `predictive` or `adaptive` | No |
| `TRUTH_API_KEY` | Validates certificate authenticity | No |

## Decision Flow

```python
# 1. Check safety guardrails
if fail_streak >= 3:
    return ESCALATE

if rate_limited:
    return NOOP

if in_cooldown:
    return NOOP

# 2. Map incident to action
if incident.kind == "github.secret.missing":
    decision = CREATE_SECRET
elif incident.kind == "config.outdated":
    decision = REGENERATE_CONFIG
elif incident.kind == "deploy.failure":
    decision = SYNC_AND_CERTIFY
# ... etc

# 3. Execute action
report = await execute_action(decision)

# 4. Certify result
certified = await truth.certify(report)
certificate = await generate_certificate(decision, report, certified)

# 5. Predict future success
predicted = await leviathan.predict(decision, report)

# 6. Update policies
await blueprint.update_policy(decision, certified.ok)

# 7. Update engine success rates
await update_engine_success_rate(action, certified.ok)
```

## Testing

All 19 tests pass (10 original + 9 new):

```bash
pytest bridge_backend/tests/test_autonomy_governor.py -v
pytest bridge_backend/tests/test_autonomy_v196t.py -v
```

### Test Coverage

- ✅ Reinforcement scoring initialization
- ✅ Reinforcement score calculation
- ✅ New incident types (CREATE_SECRET, REGENERATE_CONFIG, SYNC_AND_CERTIFY)
- ✅ Engine success rate updates
- ✅ Certificate generation
- ✅ Leviathan prediction integration
- ✅ Blueprint policy updates
- ✅ Backward compatibility with v1.9.6s

## Integration Points

### Genesis Bus

New topics:
- `autonomy.heal.applied` - Enhanced with certificate and prediction data
- `autonomy.heal.error` - Failure notifications

### Engines

- **ARIE** - Code integrity fixes
- **Chimera** - Config repair, retry, rollback, regeneration
- **EnvRecon** - Environment synchronization
- **HubSync** - GitHub secret management
- **Truth** - Result certification and certificate generation
- **Leviathan** - Success prediction
- **Blueprint** - Policy evolution

### GitHub API

- Create/update secrets via HubSync
- Read environment configuration
- Commit updated environment.json

## Files Changed

### Created
- `.github/workflows/bridge_autonomy.yml` - Self-healing workflow
- `.github/workflows/env_sync.yml` - Environment sync workflow
- `.github/environment.json` - Environment variable configuration
- `bridge_backend/tests/test_autonomy_v196t.py` - v1.9.6t tests

### Modified
- `bridge_backend/engines/autonomy/governor.py` - Enhanced with all v1.9.6t features
- `bridge_backend/bridge_core/engines/leviathan/solver.py` - Added prediction function
- `.gitignore` - Added `.bridge/` directory

## Status

✅ **Ready for Merge**

- Version: v1.9.6t
- Tests: 19/19 Passing
- Backwards Compatible: ✅
- Future-Proof Layer: 🧠 Blueprint + Leviathan enabled

## Usage

### Triggering Autonomy Manually

```bash
curl -X POST "$PUBLIC_API_BASE/api/autonomy/incident" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTONOMY_API_TOKEN" \
  -d '{
    "kind": "deploy.failure",
    "source": "manual",
    "details": {"workflow": "test"}
  }'
```

### Viewing Certificates

```bash
ls -la .bridge/logs/certificates/
cat .bridge/logs/certificates/2025-10-12T03-00-00_abc12345.json
```

### Checking Environment Sync

```bash
cat .github/environment.json
```

## What Happens When...

### A deployment fails?
1. GitHub Actions workflow detects failure
2. Posts incident to Autonomy API
3. Governor decides on action (SYNC_AND_CERTIFY)
4. Executes sync + certification
5. Leviathan predicts if retry will succeed
6. Blueprint learns from the outcome
7. Certificate generated as proof
8. Genesis events published

### Environment drift is detected?
1. Hourly workflow runs env audit
2. Detects missing variables
3. Syncs to GitHub via HubSync
4. Updates environment.json
5. Commits back to repository

### An action fails repeatedly?
1. Fail streak increments
2. Engine success rate decreases
3. After 3 failures, circuit breaker trips
4. Action escalated to human operator

## Future Enhancements

- [ ] Machine learning for optimal policy selection
- [ ] Multi-platform secret sync (Render, Netlify)
- [ ] Automatic rollback on low prediction scores
- [ ] Real-time policy optimization
- [ ] Certificate blockchain for audit trail
