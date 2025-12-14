# Autonomy Deployment Integration - Quick Reference

## 🚀 The Cherry on Top! 

The Autonomy Engine is now directly connected to **Netlify**, **Render**, and **GitHub** for real-time deployment monitoring and coordination.

## Quick Start

### Enable Genesis Mode
```bash
export GENESIS_MODE=enabled
```

### Test Deployment Event
```bash
python3 bridge_backend/utils/deployment_publisher.py \
  --platform netlify \
  --event-type success \
  --status deployed \
  --branch main
```

### Check Integration Status
```bash
curl https://sr-aibridge.onrender.com/webhooks/deployment/status
curl https://sr-aibridge.onrender.com/engines/autonomy/deployment/status
```

## Webhook Endpoints

| Platform | Endpoint | Events |
|----------|----------|--------|
| **Netlify** | `/webhooks/deployment/netlify` | `deploy-building`, `deploy-succeeded`, `deploy-failed` |
| **Render** | `/webhooks/deployment/render` | `build_in_progress`, `live`, `build_failed` |
| **GitHub** | `/webhooks/deployment/github` | `deployment`, `deployment_status`, `workflow_run` |

## Genesis Bus Topics

### Platform Topics
- `deploy.netlify` - Netlify events
- `deploy.render` - Render events
- `deploy.github` - GitHub events

### Generic Topics
- `deploy.platform.start` - Any deployment started
- `deploy.platform.success` - Any deployment succeeded
- `deploy.platform.failure` - Any deployment failed

### Autonomy Responses
- `genesis.intent` - Coordination on success
- `genesis.heal` - Self-healing on failure

## CLI Usage

```bash
# Netlify deployment
python3 bridge_backend/utils/deployment_publisher.py \
  --platform netlify \
  --event-type success \
  --status deployed \
  --deploy-url "https://sr-aibridge.netlify.app" \
  --commit-sha abc123 \
  --branch main

# Render deployment
python3 bridge_backend/utils/deployment_publisher.py \
  --platform render \
  --event-type start \
  --status deploying \
  --message "Backend deployment started"

# GitHub workflow
python3 bridge_backend/utils/deployment_publisher.py \
  --platform github \
  --event-type success \
  --status verified \
  --message "Build verification passed"
```

## API Usage

```bash
curl -X POST https://sr-aibridge.onrender.com/engines/autonomy/deployment/event \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "netlify",
    "event_type": "success",
    "status": "deployed",
    "metadata": {"commit_sha": "abc123", "branch": "main"}
  }'
```

## Setup Webhooks

### Netlify
1. Site Settings → Build & deploy → Deploy notifications
2. Add webhook: `https://sr-aibridge.onrender.com/webhooks/deployment/netlify`
3. Select events: Deploy succeeded, Deploy failed, Deploy building

### Render
1. Service Settings → Notifications
2. Add webhook: `https://sr-aibridge.onrender.com/webhooks/deployment/render`
3. Select events: Deploy started, Deploy succeeded, Deploy failed

### GitHub
1. Repository Settings → Webhooks
2. Add webhook: `https://sr-aibridge.onrender.com/webhooks/deployment/github`
3. Select events: Deployments, Deployment statuses, Workflow runs

## GitHub Actions Integration

Already configured in:
- `.github/workflows/deploy.yml`
- `.github/workflows/bridge_autodeploy.yml`

Events are automatically published on:
- Deployment start
- Deployment success
- Deployment failure
- Build verification

## Event Flow

```
Platform → Webhook/Action → Genesis Bus → Autonomy Engine → Response
  ↓           ↓                ↓              ↓                ↓
Netlify    HTTP POST     deploy.netlify   Monitor        genesis.intent
Render     HTTP POST     deploy.render    Coordinate     genesis.heal
GitHub     HTTP POST     deploy.github    Auto-fix       genesis.echo
```

## Files Added

1. `bridge_backend/utils/deployment_publisher.py` - Event publisher
2. `bridge_backend/webhooks/deployment_webhooks.py` - Webhook endpoints
3. `docs/AUTONOMY_DEPLOYMENT_INTEGRATION.md` - Full documentation

## Files Modified

1. `bridge_backend/genesis/bus.py` - Added deployment topics
2. `bridge_backend/bridge_core/engines/adapters/genesis_link.py` - Added handlers
3. `bridge_backend/bridge_core/engines/autonomy/routes.py` - Added API endpoints
4. `bridge_backend/main.py` - Registered webhook routes
5. `.github/workflows/deploy.yml` - Added event publishing
6. `.github/workflows/bridge_autodeploy.yml` - Added event publishing

## Monitoring

```bash
# Check webhook status
curl https://sr-aibridge.onrender.com/webhooks/deployment/status

# Check autonomy deployment status
curl https://sr-aibridge.onrender.com/engines/autonomy/deployment/status

# Check Genesis health
curl https://sr-aibridge.onrender.com/genesis/introspection/health
```

## Benefits

✅ Real-time deployment tracking across all platforms  
✅ Automated failure response and self-healing  
✅ Distributed deployment coordination  
✅ Unified event stream for analytics  
✅ Integration with triage, federation, and parity systems  

## Next Steps

- Configure webhooks on Netlify and Render dashboards
- Monitor deployment events in real-time
- Extend autonomy engine with custom deployment logic
- Add deployment analytics and dashboards

---

**Status:** ✅ Integration Complete  
**Platforms:** Netlify, Render, GitHub  
**Event Bus:** Genesis (enabled)  
**Autonomy:** Connected and monitoring  

🚀 **The cherry is officially on top!** 🚀
