# Bridge Notifications, Retention, and Rollback System

This document describes the enhanced CI/CD automation features added to SR-AIbridge, including Slack notifications, diagnostic retention, automatic rollback, and Bridge control API.

## Features Overview

### 1. Netlify Build Context Fix ✅
**Problem**: Netlify build was failing with exit code 127 because npm wasn't found in PATH.

**Solution**: Updated `netlify.toml` to use bridge-frontend as base and ensure dev dependencies are installed:
```toml
[build]
  base = "bridge-frontend"
  command = "npm install --include=dev && npm run build"
  publish = "bridge-frontend/dist"
```

### 2. Slack/Discord Webhook Notifications 📡

All major Bridge events now send real-time notifications to Slack or Discord.

**Supported Events**:
- `DEPLOYMENT_SUCCESS` - Deploy completed successfully
- `DEPLOYMENT_FAILURE` - Deploy failed
- `DEPLOYMENT_REPAIR` - Environment auto-healed
- `BUILD_FAILURE` - Build failed
- `DEPLOYMENT_ROLLBACK` - Automatic or manual rollback triggered
- `DIAGNOSTIC_CLEANUP` - Old diagnostics pruned

**Implementation**: 
- Added `notify_slack()` function in `scripts/report_bridge_event.py`
- All event wrappers now call both Bridge API and Slack notifications
- Gracefully handles missing webhook configuration

**Example Notification**:
```
*DEPLOYMENT_SUCCESS* — `success`
Deploy completed successfully.
```

### 3. Diagnostic Retention & Cleanup 🧹

Automatically prunes old Bridge diagnostics to keep the system lightweight.

**Retention Policy**:
- Keeps the most recent 50 diagnostic entries
- Deletes entries older than 30 days
- Runs nightly via GitHub Actions

**Files**:
- `scripts/prune_diagnostics.py` - Pruning logic
- `.github/workflows/diagnostic-retention.yml` - Scheduled workflow

**Workflow**:
```yaml
on:
  schedule:
    - cron: "0 4 * * *"  # Runs at 4 AM UTC daily
  workflow_dispatch:      # Can be triggered manually
```

### 4. Automatic Netlify Rollback ♻️

Automatically reverts to the last successful deployment if a deploy fails.

**How It Works**:
1. Deploy fails during Netlify publish
2. System fetches last successful deployment
3. Restores previous deployment via Netlify API
4. Logs `DEPLOYMENT_ROLLBACK` event to Bridge
5. Sends Slack notification

**Files**:
- `scripts/netlify_rollback.py` - Rollback implementation
- Updated `.github/workflows/build-deploy-triage.yml` - Integrated rollback on failure

**Example Workflow Step**:
```yaml
- name: 🚀 Deploy to Netlify
  run: |
    netlify deploy --dir=bridge-frontend/dist --site=$NETLIFY_SITE_ID --prod || (
      echo "⚠️ Deploy failed — rolling back to previous successful version"
      python3 scripts/report_bridge_event.py report_deploy_failure || true
      python3 scripts/netlify_rollback.py
      exit 1
    )
```

### 5. Bridge Rollback Control API 🎮

Enables secure remote rollback control from Bridge dashboard.

**Endpoint**: `POST /api/control/rollback`

**Authentication**: HMAC signature verification using `BRIDGE_CONTROL_SECRET`

**Features**:
- Secure webhook-based rollback trigger
- HMAC SHA256 signature verification
- Logs rollback events to Bridge diagnostics
- Sends Slack notifications

**Files**:
- `bridge_backend/routes/control.py` - Control API implementation
- Updated `bridge_backend/main.py` - Includes control router

**Example Request**:
```bash
curl -X POST https://sr-aibridge.onrender.com/api/control/rollback \
  -H "X-Bridge-Signature: <computed_hmac>" \
  -H "Content-Type: application/json" \
  -d '{"reason":"manual revert from dashboard"}'
```

**Response**:
```json
{
  "message": "Rollback successful",
  "rollback_id": "66e44fc1a9f149..."
}
```

## Required Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret Name | Description | Required |
|------------|-------------|----------|
| `BRIDGE_URL` | Bridge API endpoint | ✅ Yes |
| `BRIDGE_SLACK_WEBHOOK` | Slack/Discord webhook URL | ⚙️ Optional |
| `NETLIFY_AUTH_TOKEN` | Netlify API key | ✅ Yes |
| `NETLIFY_SITE_ID` | Netlify site ID | ✅ Yes |
| `BRIDGE_CONTROL_SECRET` | HMAC signing key for control API | ⚙️ Optional |

## Event Flow

### Complete Deployment Lifecycle

```
1. Developer pushes to main branch
         ↓
2. GitHub Action: Validate & Auto-Heal Env
   - Check environment parity
   - Auto-repair if needed
   - Send DEPLOYMENT_REPAIR event (if repaired)
         ↓
3. GitHub Action: Build Frontend
   - Run npm ci && npm run build
   - On failure: Send BUILD_FAILURE event → Exit
         ↓
4. GitHub Action: Deploy to Netlify
   - Deploy built files to Netlify
   - On failure:
     a. Send DEPLOYMENT_FAILURE event
     b. Trigger automatic rollback
     c. Send DEPLOYMENT_ROLLBACK event
   - On success: Send DEPLOYMENT_SUCCESS event
         ↓
5. Nightly: Diagnostic Retention
   - Prune old diagnostics
   - Send DIAGNOSTIC_CLEANUP event
```

### Notification Flow

```
Event Occurs
    ↓
notify_bridge() → POST to /api/diagnostics
    ↓
notify_slack() → POST to webhook URL
    ↓
Slack/Discord shows notification
```

## Usage Examples

### Manual Rollback

Trigger a rollback manually:
```bash
cd scripts
python3 netlify_rollback.py
```

### Manual Diagnostic Cleanup

Run pruning manually:
```bash
cd scripts
python3 prune_diagnostics.py
```

### Test Notifications

Test the notification system:
```bash
python3 -c "
from scripts.report_bridge_event import report_deploy_success
report_deploy_success()
"
```

### Trigger Remote Rollback (from Bridge Dashboard)

```javascript
// In Bridge UI
const signature = computeHMAC(secret, body);
const response = await fetch("/api/control/rollback", {
  method: "POST",
  headers: {
    "X-Bridge-Signature": signature,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ reason: "Manual restore requested" }),
});
```

## Testing

All core functionality has been tested:

✅ Slack notification with/without webhook  
✅ Event wrapper functions  
✅ Import paths for all modules  
✅ Control router integration  
✅ Script executability  
✅ YAML syntax validation  

## Troubleshooting

### Slack Notifications Not Appearing

1. Verify `BRIDGE_SLACK_WEBHOOK` secret is set
2. Check webhook URL is valid
3. Review workflow logs for notification errors

### Rollback Not Triggering

1. Ensure `NETLIFY_AUTH_TOKEN` and `NETLIFY_SITE_ID` are set
2. Verify there's a previous successful deployment
3. Check workflow logs for rollback errors

### Control API Returns 401

1. Verify `BRIDGE_CONTROL_SECRET` is set in environment
2. Ensure HMAC signature is computed correctly
3. Check request headers include `X-Bridge-Signature`

## File Changes Summary

**Modified Files**:
- `netlify.toml` - Fixed build context
- `scripts/report_bridge_event.py` - Added Slack notifications
- `scripts/prune_diagnostics.py` - Added Slack notifications
- `.github/workflows/build-deploy-triage.yml` - Added rollback logic
- `.github/workflows/diagnostic-retention.yml` - Added webhook secret
- `bridge_backend/main.py` - Included control router

**New Files**:
- `scripts/netlify_rollback.py` - Rollback implementation
- `bridge_backend/routes/control.py` - Control API
- `bridge_backend/routes/__init__.py` - Routes package init

## Benefits

🎯 **Self-Healing**: Automatic environment repair and rollback  
📊 **Visibility**: Real-time notifications for all events  
🧹 **Maintenance**: Automatic cleanup of old diagnostics  
🔒 **Security**: HMAC-verified remote control  
⚡ **Reliability**: Instant rollback on deployment failures  

## Next Steps

1. Configure `BRIDGE_SLACK_WEBHOOK` secret in GitHub
2. Test deployment pipeline with a push to main
3. Verify notifications appear in Slack/Discord
4. (Optional) Set up `BRIDGE_CONTROL_SECRET` for remote rollback control
5. Monitor nightly retention workflow

---

**Status**: ✅ Fully Implemented and Tested  
**Version**: 1.0  
**Last Updated**: 2024-10-07
