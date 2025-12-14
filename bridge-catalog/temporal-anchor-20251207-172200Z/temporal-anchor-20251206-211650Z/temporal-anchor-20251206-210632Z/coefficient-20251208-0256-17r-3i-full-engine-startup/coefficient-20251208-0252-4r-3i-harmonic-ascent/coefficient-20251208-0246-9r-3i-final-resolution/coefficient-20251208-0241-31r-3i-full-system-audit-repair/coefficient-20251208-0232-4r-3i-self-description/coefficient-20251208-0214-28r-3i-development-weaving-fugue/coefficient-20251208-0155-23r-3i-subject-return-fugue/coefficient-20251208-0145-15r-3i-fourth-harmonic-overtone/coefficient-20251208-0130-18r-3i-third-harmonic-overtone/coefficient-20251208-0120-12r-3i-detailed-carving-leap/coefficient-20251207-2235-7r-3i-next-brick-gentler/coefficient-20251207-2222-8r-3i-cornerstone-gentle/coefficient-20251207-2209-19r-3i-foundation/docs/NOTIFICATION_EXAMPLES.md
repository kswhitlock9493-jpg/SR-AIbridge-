# Example Slack/Discord Notifications

This document shows what the webhook notifications look like in Slack or Discord.

## Notification Format

All notifications follow this format:
```
*EVENT_TYPE* — `status`
Optional message with details.
```

## Example Notifications

### Deployment Success ✅
```
*DEPLOYMENT_SUCCESS* — `success`
Deploy completed successfully.
```

### Deployment Failure ❌
```
*DEPLOYMENT_FAILURE* — `failed`
Deploy failed during Netlify publish.
```

### Build Failure 🧱
```
*BUILD_FAILURE* — `failed`
Build failed during npm run build.
```

### Environment Repair 🔧
```
*DEPLOYMENT_REPAIR* — `auto-healed`
Environment repaired automatically.
```

### Automatic Rollback ♻️
```
*DEPLOYMENT_ROLLBACK* — `success`
Rolled back to deploy `66e44fc1a9f149...`
```

### Manual Rollback (from Dashboard) 🎮
```
*DEPLOYMENT_ROLLBACK* — `success`
Manual rollback triggered from Bridge Dashboard. Restored deploy `66e44fc1a9f149...`
```

### Diagnostic Cleanup 🧹
```
Deleted 14 old Bridge diagnostics.
```

## Setting Up Webhook

### For Slack

1. Go to your Slack workspace settings
2. Navigate to "Apps" → "Incoming Webhooks"
3. Click "Add New Webhook to Workspace"
4. Select the channel where notifications should appear
5. Copy the webhook URL (looks like: `https://hooks.slack.com/services/...`)
6. Add it as `BRIDGE_SLACK_WEBHOOK` secret in GitHub

### For Discord

1. Open your Discord server
2. Go to Server Settings → Integrations → Webhooks
3. Click "New Webhook"
4. Choose the channel for notifications
5. Copy the webhook URL (looks like: `https://discord.com/api/webhooks/...`)
6. Add it as `BRIDGE_SLACK_WEBHOOK` secret in GitHub

Note: The same secret name (`BRIDGE_SLACK_WEBHOOK`) works for both Slack and Discord webhooks.

## Testing Notifications

You can test the notification system manually:

```bash
# Set the webhook URL
export BRIDGE_SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Test a notification
python3 -c "
from scripts.report_bridge_event import notify_slack
notify_slack('TEST_EVENT', 'success', 'This is a test notification from SR-AIbridge')
"
```

## Disabling Notifications

To temporarily disable notifications:
- Simply remove or don't set the `BRIDGE_SLACK_WEBHOOK` secret
- The system will gracefully skip notification attempts with a warning message in logs

## Notification Schedule

| Event | Trigger | Frequency |
|-------|---------|-----------|
| DEPLOYMENT_SUCCESS | Deploy completes | Per deploy |
| DEPLOYMENT_FAILURE | Deploy fails | Per failed deploy |
| BUILD_FAILURE | Build fails | Per failed build |
| DEPLOYMENT_REPAIR | Env auto-heals | Per repair |
| DEPLOYMENT_ROLLBACK | Rollback triggered | Per rollback |
| DIAGNOSTIC_CLEANUP | Nightly job | Daily at 4 AM UTC |

## Advanced: Custom Notifications

You can add custom notifications by importing the `notify_slack` function:

```python
from scripts.report_bridge_event import notify_slack

# Send a custom notification
notify_slack(
    event_type="CUSTOM_EVENT",
    status="info",
    message="Custom message with additional details"
)
```

## Troubleshooting

**No notifications appearing:**
- Verify `BRIDGE_SLACK_WEBHOOK` secret is set in GitHub
- Check the webhook URL is valid and active
- Review GitHub Actions logs for webhook errors

**Notifications going to wrong channel:**
- Update the webhook to point to the correct channel
- Create a new webhook in the desired channel
- Update the `BRIDGE_SLACK_WEBHOOK` secret

**Rate limiting:**
- Slack/Discord may rate limit webhooks if too many are sent
- Current implementation sends one notification per event
- Consider batching if you have many rapid events
