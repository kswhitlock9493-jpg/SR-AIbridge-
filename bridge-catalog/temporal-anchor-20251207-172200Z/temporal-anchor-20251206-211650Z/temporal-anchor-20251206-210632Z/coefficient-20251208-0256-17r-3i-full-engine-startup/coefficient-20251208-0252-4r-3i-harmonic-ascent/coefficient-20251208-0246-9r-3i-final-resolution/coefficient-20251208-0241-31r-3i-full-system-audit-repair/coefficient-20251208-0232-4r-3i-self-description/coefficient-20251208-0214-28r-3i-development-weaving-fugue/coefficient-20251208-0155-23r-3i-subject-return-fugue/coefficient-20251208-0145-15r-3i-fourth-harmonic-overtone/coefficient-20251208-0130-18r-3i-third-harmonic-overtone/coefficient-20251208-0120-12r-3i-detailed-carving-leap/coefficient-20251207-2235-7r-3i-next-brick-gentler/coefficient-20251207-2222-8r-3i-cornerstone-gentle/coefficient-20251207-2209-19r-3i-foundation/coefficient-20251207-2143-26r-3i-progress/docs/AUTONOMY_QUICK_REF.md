# Autonomy Decision Layer v1.9.6s - Quick Reference

## What Is It?

The Autonomy Decision Layer enables SR-AIbridge to automatically detect, decide, fix, certify, redeploy, and learn from production incidents. It's a self-healing CI/CD loop with safety guardrails.

## Key Features

- **Policy-based decision making** - Maps incidents to appropriate actions
- **Safety guardrails** - Rate limiting, cooldown, circuit breaker
- **Truth certification** - Every action verified before being marked successful
- **Genesis integration** - Event-driven architecture with full audit trail
- **RBAC protected** - Admiral-only access by default

## Quick Commands

### CLI

```bash
# Check status
python3 -m bridge_backend.cli.autonomyctl status

# Submit incident
python3 -m bridge_backend.cli.autonomyctl incident \
  --kind deploy.netlify.preview_failed

# Control circuit
python3 -m bridge_backend.cli.autonomyctl circuit --open
python3 -m bridge_backend.cli.autonomyctl circuit --close
```

### API

```bash
# Get status
curl https://your-api.com/api/autonomy/status \
  -H "Authorization: Bearer <token>"

# Submit incident
curl -X POST https://your-api.com/api/autonomy/incident \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"kind":"deploy.netlify.preview_failed","source":"manual"}'

# Trigger specific action
curl -X POST https://your-api.com/api/autonomy/trigger \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"action":"SYNC_ENVS","reason":"manual_sync"}'
```

## Incident Kinds → Actions

| Incident | Action | Engine |
|----------|--------|--------|
| `deploy.netlify.preview_failed` | `REPAIR_CONFIG` | Chimera |
| `deploy.render.failed` | `RETRY` | Chimera |
| `envrecon.drift` | `SYNC_ENVS` | EnvRecon |
| `arie.deprecated.detected` | `REPAIR_CODE` | ARIE |
| *(unknown)* | `NOOP` | - |

## Configuration

```bash
# Enable/disable
AUTONOMY_ENABLED=true

# Safety limits
AUTONOMY_MAX_ACTIONS_PER_HOUR=6      # Rate limit
AUTONOMY_COOLDOWN_MINUTES=5          # Cooldown between actions
AUTONOMY_FAIL_STREAK_TRIP=3          # Circuit breaker threshold

# Integration
PUBLIC_API_BASE=https://your-api.com
AUTONOMY_API_TOKEN=<secret>
```

## Decision Flow

```
Incident → Governor.decide() → Action → Execute → Truth.certify() → Genesis Event
```

## Safety Guardrails

1. **Rate Limiting** - Max 6 actions/hour (configurable)
2. **Cooldown** - 5 minutes between actions (configurable)
3. **Circuit Breaker** - Trips after 3 consecutive failures
4. **Truth Certification** - All actions must be certified

## Genesis Events

**Subscriptions** (incoming):
- `deploy.netlify.preview_failed`
- `deploy.render.failed`
- `envrecon.drift`
- `arie.deprecated.detected`

**Publications** (outgoing):
- `autonomy.heal.applied` - Successful healing
- `autonomy.heal.error` - Healing failed
- `autonomy.circuit.open` - Circuit breaker opened
- `autonomy.circuit.closed` - Circuit breaker closed

## Files

```
bridge_backend/engines/autonomy/
├── __init__.py
├── models.py                      # Incident, Decision models
├── governor.py                    # Policy brain & execution
└── routes.py                      # REST API

bridge_backend/bridge_core/engines/adapters/
└── autonomy_genesis_link.py       # Genesis event subscriptions

bridge_backend/cli/
└── autonomyctl.py                 # CLI tool

bridge_backend/tests/
├── test_autonomy_governor.py      # Governor tests
├── test_autonomy_routes.py        # API tests
└── test_autonomy_genesis_link.py  # Genesis integration tests

docs/
├── AUTONOMY_DECISION_LAYER.md     # Architecture
├── AUTONOMY_OPERATIONS.md         # Operations guide
└── INCIDENT_CATALOG.md            # Incident reference
```

## Permissions

All endpoints require `autonomy:operate` permission (admiral-only by default).

## GitHub Actions Integration

Add to workflow:

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

## Render Integration

In `render.yaml`:

```yaml
envVars:
  - key: AUTONOMY_ENABLED
    value: "true"
postDeployCommand: "python3 -m bridge_backend.engines.envrecon.cli audit --emit"
```

## Common Issues

**Q: Actions not executing?**  
A: Check rate limit (6/hour), cooldown (5 min), circuit breaker status.

**Q: Circuit breaker tripped?**  
A: 3 consecutive failures. Close circuit after fixing root cause.

**Q: How to disable autonomy?**  
A: Set `AUTONOMY_ENABLED=false` or open circuit breaker.

## See Also

- [AUTONOMY_DECISION_LAYER.md](AUTONOMY_DECISION_LAYER.md) - Full architecture
- [AUTONOMY_OPERATIONS.md](AUTONOMY_OPERATIONS.md) - Operations guide
- [INCIDENT_CATALOG.md](INCIDENT_CATALOG.md) - All incident kinds
