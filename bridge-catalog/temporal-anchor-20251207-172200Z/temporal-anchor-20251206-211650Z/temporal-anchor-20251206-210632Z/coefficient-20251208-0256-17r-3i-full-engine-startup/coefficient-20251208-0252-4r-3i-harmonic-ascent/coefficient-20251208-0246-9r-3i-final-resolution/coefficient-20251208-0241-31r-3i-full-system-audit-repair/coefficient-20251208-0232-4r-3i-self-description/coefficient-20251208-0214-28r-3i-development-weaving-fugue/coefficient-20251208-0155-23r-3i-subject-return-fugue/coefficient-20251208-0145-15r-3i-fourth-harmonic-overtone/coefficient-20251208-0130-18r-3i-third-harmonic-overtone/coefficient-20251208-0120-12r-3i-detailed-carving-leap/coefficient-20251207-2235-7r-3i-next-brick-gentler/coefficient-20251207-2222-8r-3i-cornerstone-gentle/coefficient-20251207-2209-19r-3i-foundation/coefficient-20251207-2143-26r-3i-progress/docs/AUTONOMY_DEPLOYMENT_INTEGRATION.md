# Autonomy Engine Deployment Integration

## Overview

The Autonomy Engine is now directly connected to **Netlify**, **Render**, and **GitHub** for real-time deployment monitoring and coordination. This integration enables the autonomy engine to:

- Track deployment lifecycle events across all platforms
- Coordinate self-healing actions during deployment failures
- Publish deployment telemetry to the Genesis event bus
- Enable distributed deployment orchestration

## Architecture

### Event Flow

```
Netlify/Render/GitHub → Webhook Endpoint → Genesis Bus → Autonomy Engine
                           ↓
                    Deployment Events
                           ↓
                    Platform Topics:
                    - deploy.netlify
                    - deploy.render
                    - deploy.github
                           ↓
                    Generic Topics:
                    - deploy.platform.start
                    - deploy.platform.success
                    - deploy.platform.failure
                           ↓
                    Autonomy Handler
                    - genesis.intent (success)
                    - genesis.heal (failure)
```

## Integration Points

### 1. GitHub Actions Integration

GitHub Actions workflows automatically publish deployment events:

**Workflow: `deploy.yml`**
- Netlify deployment start/success/failure events
- Render deployment trigger events
- Build verification events

**Workflow: `bridge_autodeploy.yml`**
- Auto-deployment notifications
- Deployment status tracking

**Event Publisher:**
```bash
python3 bridge_backend/utils/deployment_publisher.py \
  --platform netlify \
  --event-type success \
  --status deployed \
  --branch main \
  --commit-sha $GITHUB_SHA \
  --deploy-url "https://sr-aibridge.netlify.app"
```

### 2. Webhook Endpoints

Direct webhook integration for platform-initiated events:

**Netlify Webhook:**
- Endpoint: `POST /webhooks/deployment/netlify`
- Events: `deploy-building`, `deploy-succeeded`, `deploy-failed`
- Headers: `X-Netlify-Event`

**Render Webhook:**
- Endpoint: `POST /webhooks/deployment/render`
- Events: `build_in_progress`, `live`, `build_failed`
- Payload: `{service: {...}, deploy: {...}, status: "..."}`

**GitHub Webhook:**
- Endpoint: `POST /webhooks/deployment/github`
- Events: `deployment`, `deployment_status`, `workflow_run`
- Headers: `X-GitHub-Event`, `X-Hub-Signature-256`

**Status Endpoint:**
- Endpoint: `GET /webhooks/deployment/status`
- Returns webhook configuration and Genesis bus status

### 3. Autonomy Engine API

Direct API integration for programmatic event publishing:

**Deployment Event Endpoint:**
```
POST /engines/autonomy/deployment/event
{
  "platform": "netlify",
  "event_type": "success",
  "status": "deployed",
  "metadata": {
    "commit_sha": "abc123",
    "branch": "main",
    "deploy_url": "https://..."
  }
}
```

**Deployment Status Endpoint:**
```
GET /engines/autonomy/deployment/status
```

Returns:
```json
{
  "genesis_enabled": true,
  "platforms_monitored": ["netlify", "render", "github"],
  "topics": [
    "deploy.netlify",
    "deploy.render",
    "deploy.github",
    "deploy.platform.start",
    "deploy.platform.success",
    "deploy.platform.failure"
  ],
  "status": "active"
}
```

## Genesis Bus Topics

### Platform-Specific Topics

- **`deploy.netlify`** - All Netlify deployment events
- **`deploy.render`** - All Render deployment events
- **`deploy.github`** - All GitHub deployment/workflow events

### Generic Deployment Topics

- **`deploy.platform.start`** - Deployment initiated on any platform
- **`deploy.platform.success`** - Deployment succeeded on any platform
- **`deploy.platform.failure`** - Deployment failed on any platform

### Autonomy Response Topics

- **`genesis.intent`** - Successful deployments trigger coordination events
- **`genesis.heal`** - Failed deployments trigger self-healing actions

## Event Payload Structure

```json
{
  "platform": "netlify|render|github",
  "event_type": "start|success|failure|progress",
  "status": "deploying|deployed|failed|...",
  "timestamp": "2025-10-11T08:40:20.557Z",
  "metadata": {
    "commit_sha": "abc123",
    "branch": "main",
    "deploy_url": "https://...",
    "deploy_id": "...",
    "message": "...",
    // Platform-specific fields
  }
}
```

## Configuration

### Environment Variables

**Genesis Mode (required):**
```bash
GENESIS_MODE=enabled
```

**Strict Policy (optional):**
```bash
GENESIS_STRICT_POLICY=true  # Enforce topic validation
```

### GitHub Actions Secrets

Required secrets for webhook functionality:
- `NETLIFY_AUTH_TOKEN` - Netlify API token
- `NETLIFY_SITE_ID` - Netlify site identifier
- `RENDER_DEPLOY_HOOK` - Render webhook URL (optional)

## Setup Instructions

### 1. Configure Netlify Webhooks

1. Go to Netlify site settings
2. Navigate to **Build & deploy** → **Deploy notifications**
3. Add outgoing webhook:
   - **Event**: Deploy succeeded / Deploy failed / Deploy building
   - **URL**: `https://sr-aibridge.onrender.com/webhooks/deployment/netlify`
   - **Format**: JSON

### 2. Configure Render Webhooks

1. Go to Render service settings
2. Navigate to **Settings** → **Notifications**
3. Add webhook:
   - **Event**: Deploy started / Deploy succeeded / Deploy failed
   - **URL**: `https://sr-aibridge.onrender.com/webhooks/deployment/render`

### 3. Configure GitHub Webhooks

1. Go to repository settings
2. Navigate to **Webhooks**
3. Add webhook:
   - **Payload URL**: `https://sr-aibridge.onrender.com/webhooks/deployment/github`
   - **Content type**: application/json
   - **Events**: Deployments, Deployment statuses, Workflow runs
   - **Secret**: (optional, for signature verification)

## Usage Examples

### Manual Event Publishing (CLI)

```bash
# Publish deployment start event
python3 bridge_backend/utils/deployment_publisher.py \
  --platform netlify \
  --event-type start \
  --status deploying \
  --branch main \
  --message "Deployment initiated"

# Publish deployment success
python3 bridge_backend/utils/deployment_publisher.py \
  --platform render \
  --event-type success \
  --status deployed \
  --deploy-url "https://sr-aibridge.onrender.com" \
  --commit-sha "abc123def"

# Publish deployment failure
python3 bridge_backend/utils/deployment_publisher.py \
  --platform github \
  --event-type failure \
  --status failed \
  --message "Build verification failed"
```

### Programmatic Event Publishing (Python)

```python
from bridge_backend.utils.deployment_publisher import publish_deployment_event_sync

# Publish deployment event
publish_deployment_event_sync(
    platform="netlify",
    event_type="success",
    status="deployed",
    metadata={
        "commit_sha": "abc123",
        "branch": "main",
        "deploy_url": "https://sr-aibridge.netlify.app"
    }
)
```

### API Event Publishing (cURL)

```bash
# Via autonomy engine API
curl -X POST https://sr-aibridge.onrender.com/engines/autonomy/deployment/event \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "netlify",
    "event_type": "success",
    "status": "deployed",
    "metadata": {
      "commit_sha": "abc123",
      "branch": "main"
    }
  }'
```

## Monitoring

### Check Webhook Status

```bash
curl https://sr-aibridge.onrender.com/webhooks/deployment/status
```

### Check Autonomy Deployment Status

```bash
curl https://sr-aibridge.onrender.com/engines/autonomy/deployment/status
```

### Genesis Bus Introspection

```bash
curl https://sr-aibridge.onrender.com/genesis/introspection/health
```

## Benefits

### 1. Real-Time Deployment Tracking
- Monitor deployments across all platforms from a single point
- Unified event stream for all deployment activities

### 2. Automated Failure Response
- Autonomy engine can trigger self-healing actions on deployment failures
- Automatic rollback or remediation workflows

### 3. Distributed Coordination
- Deploy multiple services in coordinated sequence
- Cross-platform deployment orchestration

### 4. Deployment Analytics
- Track deployment frequency, success rate, and duration
- Identify deployment bottlenecks and patterns

### 5. Integration with Existing Systems
- Works seamlessly with triage, federation, and parity systems
- All deployment events flow through unified Genesis bus

## Troubleshooting

### Events Not Publishing

1. Check Genesis mode is enabled:
```bash
echo $GENESIS_MODE  # Should be "enabled"
```

2. Verify webhook endpoints are registered:
```bash
curl https://sr-aibridge.onrender.com/webhooks/deployment/status
```

3. Check application logs for webhook errors

### Webhook Authentication Failures

- Verify webhook URLs are correct
- Check that backend is publicly accessible
- Review webhook payload format matches expected structure

### Missing Deployment Events

- Ensure GitHub Actions workflows are running
- Verify deployment publisher script is called in workflows
- Check that secrets (NETLIFY_AUTH_TOKEN, etc.) are configured

## Files Changed

### Created (3 files)
1. `bridge_backend/utils/deployment_publisher.py` - CLI/programmatic event publisher
2. `bridge_backend/webhooks/deployment_webhooks.py` - Webhook endpoints
3. `bridge_backend/webhooks/__init__.py` - Package initialization

### Modified (4 files)
1. `bridge_backend/genesis/bus.py` - Added deployment topics
2. `bridge_backend/bridge_core/engines/adapters/genesis_link.py` - Added deployment event handlers
3. `bridge_backend/bridge_core/engines/autonomy/routes.py` - Added deployment API endpoints
4. `bridge_backend/main.py` - Registered webhook routes
5. `.github/workflows/deploy.yml` - Added event publishing
6. `.github/workflows/bridge_autodeploy.yml` - Added event publishing

## Next Steps

### Optional Enhancements

1. **Deployment History Tracking**
   - Store deployment events in database
   - Generate deployment analytics and reports

2. **Advanced Orchestration**
   - Multi-stage deployment coordination
   - Canary deployments with automatic rollback

3. **Notification Integration**
   - Send deployment notifications to Slack/Discord
   - Email alerts for deployment failures

4. **Deployment Validation**
   - Automated smoke tests after deployment
   - Health check validation before marking as successful

## Conclusion

The Autonomy Engine is now fully integrated with Netlify, Render, and GitHub for comprehensive deployment monitoring and coordination. All deployment events flow through the Genesis event bus, enabling unified orchestration across the entire SR-AIbridge platform.

🚀 The cherry is on top! 🚀
