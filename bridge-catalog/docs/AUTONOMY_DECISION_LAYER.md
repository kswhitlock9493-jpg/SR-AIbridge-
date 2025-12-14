# Autonomy Decision Layer Architecture

**Version:** v1.9.6s  
**Component:** Autonomy Governor + Genesis Integration  
**Purpose:** Self-healing CI/CD loop with verifiable safety

---

## Overview

The Autonomy Decision Layer enables the Bridge to automatically detect, decide, fix, certify, redeploy, and learn from production incidents without human intervention. It operates as a closed feedback loop with multiple safety guardrails.

## Architecture

### Components

1. **Autonomy Governor** (`governor.py`)
   - Policy-based decision engine
   - Evaluates incidents and chooses appropriate actions
   - Enforces safety guardrails (rate limiting, cooldown, circuit breaker)

2. **Incident Model** (`models.py`)
   - Structured representation of events requiring autonomous action
   - Fields: `kind`, `source`, `details`, `timestamp`

3. **Decision Model** (`models.py`)
   - Represents the chosen action with reasoning
   - Fields: `action`, `reason`, `targets`, `metadata`

4. **Genesis Adapter** (`autonomy_genesis_link.py`)
   - Subscribes to deployment and environment events
   - Translates events into incidents
   - Publishes heal results back to Genesis bus

5. **REST API** (`routes.py`)
   - `/api/autonomy/incident` - Submit incident for processing
   - `/api/autonomy/trigger` - Manually trigger a decision
   - `/api/autonomy/status` - Get engine status
   - `/api/autonomy/circuit` - Control circuit breaker

---

## Decision Flow

```
Event → Genesis Bus → Autonomy Link → Governor.decide() → Governor.execute() → Truth.certify() → Genesis Event
```

### 1. Event Detection

Events are published to Genesis bus from various sources:
- **GitHub Actions** - CI/CD failures
- **Render** - Deployment events  
- **Netlify** - Preview build failures
- **EnvRecon** - Environment drift detection
- **ARIE** - Code integrity issues

### 2. Decision Making

The Governor evaluates the incident against a policy matrix:

| Incident Kind | Action | Reason |
|--------------|--------|--------|
| `deploy.netlify.preview_failed` | `REPAIR_CONFIG` | Preview build failed, fix config |
| `deploy.render.failed` | `RETRY` | Render deploy failed, retry once |
| `deploy.render.rollback` | `RETRY` | Render rollback detected, retry |
| `envrecon.drift` | `SYNC_ENVS` | Environment drift detected |
| `env.drift.detected` | `SYNC_ENVS` | Legacy drift event |
| `arie.deprecated.detected` | `REPAIR_CODE` | Deprecated code patterns found |
| `code.integrity.deprecated` | `REPAIR_CODE` | Code integrity issue |
| *(unknown)* | `NOOP` | Unrecognized incident kind |

### 3. Action Execution

Available actions:
- **NOOP** - No operation (rate limited, cooldown, or unrecognized)
- **RETRY** - Retry last deployment via Chimera
- **REPAIR_CONFIG** - Heal configuration via Chimera
- **REPAIR_CODE** - Apply safe edits via ARIE
- **SYNC_ENVS** - Sync environments via EnvRecon
- **ROLLBACK** - Rollback via Chimera
- **ESCALATE** - Circuit breaker tripped, requires manual intervention

### 4. Certification

Every action result is certified by the Truth Engine before being considered successful. This ensures:
- Changes are verified
- No unintended side effects
- Audit trail is maintained

---

## Safety Guardrails

### Rate Limiting

**Default:** 6 actions per hour  
**Config:** `AUTONOMY_MAX_ACTIONS_PER_HOUR`

Prevents runaway autonomy by limiting total actions in a sliding 1-hour window.

### Cooldown Period

**Default:** 5 minutes  
**Config:** `AUTONOMY_COOLDOWN_MINUTES`

Enforces minimum time between consecutive actions, preventing rapid thrashing.

### Circuit Breaker

**Default:** Trip after 3 consecutive failures  
**Config:** `AUTONOMY_FAIL_STREAK_TRIP`

When the fail streak reaches the threshold, all future decisions return `ESCALATE` until manually reset. This prevents the system from repeatedly attempting failing operations.

### Truth Certification

Every execution result is certified by the Truth Engine. If certification fails, the fail streak increments. After enough failures, the circuit breaker trips.

---

## Event Topics

### Subscriptions (Incoming)

- `deploy.netlify.preview_failed` - Netlify preview build failure
- `deploy.render.failed` - Render deployment failure
- `envrecon.drift` - Environment drift detected
- `arie.deprecated.detected` - Deprecated code patterns found

### Publications (Outgoing)

- `autonomy.heal.applied` - Healing action successfully applied
- `autonomy.heal.error` - Healing action failed
- `autonomy.circuit.open` - Circuit breaker opened
- `autonomy.circuit.closed` - Circuit breaker closed

---

## Engine Integration

### Chimera (Config & Deployment)

- `REPAIR_CONFIG` → `ChimeraEngine.heal_config()`
- `RETRY` → `ChimeraEngine.retry_last_deploy()`
- `ROLLBACK` → `ChimeraEngine.rollback()`

### ARIE (Code Integrity)

- `REPAIR_CODE` → `ARIEEngine.apply(policy="SAFE_EDIT")`

### EnvRecon (Environment Sync)

- `SYNC_ENVS` → `EnvReconEngine.sync(intent_only=False)`

### Truth (Certification)

- All actions → `TruthEngine.certify(report)`

---

## Configuration

### Environment Variables

```bash
# Core Settings
AUTONOMY_ENABLED=true                    # Enable/disable autonomy engine

# Safety Guardrails
AUTONOMY_MAX_ACTIONS_PER_HOUR=6          # Rate limit
AUTONOMY_COOLDOWN_MINUTES=5              # Cooldown period
AUTONOMY_FAIL_STREAK_TRIP=3              # Circuit breaker threshold

# Integration
PUBLIC_API_BASE=https://your-api.com     # API base URL for webhooks
AUTONOMY_API_TOKEN=<secret>              # API token for CI integration
```

---

## RBAC

All autonomy endpoints are gated behind `autonomy:operate` permission, which is **admiral-only** by default.

### Permission Scopes

- `autonomy:operate` - Submit incidents, trigger decisions, view status
- `autonomy:configure` - Modify autonomy settings (future)

---

## Deployment

### Render (Backend)

The autonomy engine runs automatically when `AUTONOMY_ENABLED=true`. Add to `render.yaml`:

```yaml
envVars:
  - key: AUTONOMY_ENABLED
    value: "true"
  - key: AUTONOMY_MAX_ACTIONS_PER_HOUR
    value: "6"
```

### GitHub Actions (CI)

Add incident emission on failure:

```yaml
jobs:
  emit-incidents-on-fail:
    if: ${{ failure() }}
    runs-on: ubuntu-latest
    steps:
      - name: Emit incident
        run: |
          curl -X POST "$API_BASE/api/autonomy/incident" \
            -H "Authorization: Bearer $AUTONOMY_API_TOKEN" \
            -d '{"kind":"deploy.netlify.preview_failed","source":"github"}'
```

---

## Logging & Observability

All actions are logged with structured metadata:

```python
logger.info("[Governor] Decision: REPAIR_CONFIG (preview_failed)")
logger.info("[Governor] Execution: applied, certified=True")
```

Genesis events provide full audit trail:
- Incident received
- Decision made
- Action executed
- Result certified

---

## Future Enhancements

- **HXO Signal Integration** - Use Hypshard-X signals to inform decisions
- **Persistent Circuit State** - Store circuit state in database
- **Learning Loop** - Improve policy matrix based on past outcomes
- **Multi-stage Healing** - Chain multiple actions for complex incidents
- **Custom Policies** - User-defined incident → action mappings
