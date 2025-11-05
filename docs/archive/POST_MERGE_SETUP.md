# Post-Merge Setup Guide

## 🚀 Congratulations! The cherry is on top! 🍒

The autonomy engine is now connected to Netlify, Render, and GitHub. Follow these steps to complete the setup.

## Immediate Actions (Required)

### 1. Enable Genesis Mode ✅

The integration requires Genesis mode to be enabled in your environment.

**On Render:**
1. Go to your Render dashboard
2. Navigate to your SR-AIbridge service
3. Go to Environment tab
4. Add or verify environment variable:
   ```
   GENESIS_MODE=enabled
   ```
5. Save and deploy

**On Netlify:**
Netlify automatically proxies to Render, so no action needed.

### 2. Verify Deployment ✅

After the merge and deployment, verify the integration is working:

```bash
# Check webhook status
curl https://sr-aibridge.onrender.com/webhooks/deployment/status

# Check autonomy deployment status  
curl https://sr-aibridge.onrender.com/engines/autonomy/deployment/status

# Should return:
# {
#   "genesis_enabled": true,
#   "platforms_monitored": ["netlify", "render", "github"],
#   "status": "active"
# }
```

## Optional Actions (Recommended)

### 3. Configure Netlify Webhook (Optional) 🔔

For direct Netlify deployment notifications (in addition to GitHub Actions):

1. Go to [Netlify Dashboard](https://app.netlify.com)
2. Select your **sr-aibridge** site
3. Navigate to **Site settings** → **Build & deploy** → **Deploy notifications**
4. Click **Add notification** → **Outgoing webhook**
5. Configure:
   - **Event to listen for:** Deploy succeeded
   - **URL to notify:** `https://sr-aibridge.onrender.com/webhooks/deployment/netlify`
   - **Format:** JSON
6. Click **Save**
7. Repeat for other events:
   - Deploy failed
   - Deploy building (optional)

### 4. Configure Render Webhook (Optional) 🔔

For direct Render deployment notifications:

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your **SR-AIbridge** service
3. Navigate to **Settings** → **Notifications**
4. Click **Add Notification**
5. Configure:
   - **Type:** Webhook
   - **URL:** `https://sr-aibridge.onrender.com/webhooks/deployment/render`
   - **Events:** Select all deployment events
6. Click **Save**

### 5. Configure GitHub Webhook (Optional) 🔔

For direct GitHub deployment events (in addition to Actions):

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Webhooks**
3. Click **Add webhook**
4. Configure:
   - **Payload URL:** `https://sr-aibridge.onrender.com/webhooks/deployment/github`
   - **Content type:** application/json
   - **Secret:** (leave empty for now, or add for security)
   - **Events:** Select individual events:
     - ✅ Deployments
     - ✅ Deployment statuses
     - ✅ Workflow runs
5. Click **Add webhook**

## Testing the Integration

### Test 1: GitHub Actions (Already Working) ✅

GitHub Actions will automatically publish deployment events on the next deployment. No action needed!

### Test 2: Manual Event Publishing

Test the event publishing system manually:

```bash
# Test from your local machine or via SSH to Render
python3 bridge_backend/utils/deployment_publisher.py \
  --platform netlify \
  --event-type success \
  --status deployed \
  --branch main \
  --message "Test event from post-merge setup"
```

### Test 3: Webhook Testing

If you configured webhooks, test them:

**Netlify:**
- Deploy your Netlify site
- Check Render logs for: `✅ Published deployment webhook event to deploy.netlify`

**Render:**
- Deploy your Render service
- Check logs for: `✅ Published deployment webhook event to deploy.render`

**GitHub:**
- Trigger a workflow
- Check logs for: `✅ Published deployment webhook event to deploy.github`

### Test 4: Verification Script

Run the verification script to ensure everything is configured:

```bash
python3 verify_autonomy_deployment.py
```

Expected output:
```
✅ Genesis Bus Topics - 6/6 topics registered
✅ Autonomy Genesis Link - Handler registered
✅ Deployment Publisher - CLI and API available
✅ Webhook Endpoints - All routes registered
✅ Autonomy Routes - Deployment API available
✅ GitHub Actions - Event publishing configured
✅ Documentation - Guides created
```

## Monitoring and Observability

### View Deployment Events

Check Genesis bus introspection:

```bash
curl https://sr-aibridge.onrender.com/genesis/introspection/health
```

### Monitor Render Logs

View deployment events in real-time:

1. Go to Render Dashboard
2. Select your service
3. Click **Logs** tab
4. Filter for: `deploy.netlify`, `deploy.render`, `deploy.github`

### Monitor Autonomy Engine

Check autonomy engine activity:

```bash
curl https://sr-aibridge.onrender.com/engines/autonomy/deployment/status
```

## Troubleshooting

### Issue: Genesis Mode Not Enabled

**Symptom:** Webhook status shows `"status": "disabled"`

**Solution:**
1. Check `GENESIS_MODE` environment variable on Render
2. Ensure it's set to `enabled`
3. Redeploy service

### Issue: Webhooks Not Receiving Events

**Symptom:** No deployment events in logs

**Solution:**
1. Verify webhook URLs are correct
2. Check that backend is publicly accessible
3. Test with manual event publishing first
4. Review webhook configuration in platform dashboards

### Issue: GitHub Actions Not Publishing

**Symptom:** No events on deployments

**Solution:**
1. Check that workflows ran successfully
2. Verify secrets are configured (NETLIFY_AUTH_TOKEN, etc.)
3. Review workflow logs for errors
4. Ensure `deployment_publisher.py` is being called

## What Happens Now?

### On Every Deployment:

1. **Netlify Frontend Deploy:**
   - GitHub Actions publishes start event
   - Netlify webhook (if configured) sends events
   - Genesis bus receives: `deploy.netlify`
   - Autonomy engine monitors and coordinates
   - Success → `genesis.intent`
   - Failure → `genesis.heal`

2. **Render Backend Deploy:**
   - GitHub Actions publishes start event
   - Render webhook (if configured) sends events
   - Genesis bus receives: `deploy.render`
   - Autonomy engine monitors and coordinates

3. **GitHub Workflow:**
   - GitHub Actions publishes events
   - Genesis bus receives: `deploy.github`
   - Autonomy engine tracks build verification

### Integration Benefits:

- ✅ Real-time deployment tracking
- ✅ Automated failure response
- ✅ Multi-platform coordination
- ✅ Unified event stream
- ✅ Self-healing capabilities

## Documentation

Refer to these guides for more information:

- **[Integration Guide](docs/AUTONOMY_DEPLOYMENT_INTEGRATION.md)** - Complete setup and API usage
- **[Quick Reference](docs/AUTONOMY_DEPLOYMENT_QUICK_REF.md)** - Common commands and patterns
- **[Architecture](docs/AUTONOMY_DEPLOYMENT_ARCHITECTURE.md)** - Visual diagrams and flows
- **[README](AUTONOMY_DEPLOYMENT_README.md)** - Overview and quick start

## Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Review the documentation guides
3. Run the verification script
4. Check Render logs for errors

## Next Enhancements (Future)

Consider these optional enhancements:

- [ ] Deployment history database
- [ ] Deployment analytics dashboard
- [ ] Advanced orchestration (canary, blue-green)
- [ ] Slack/Discord notifications
- [ ] Automated smoke tests
- [ ] Deployment validation

## Conclusion

**The cherry is on top!** 🍒

Your autonomy engine is now fully integrated with:
- ✅ Netlify (Frontend)
- ✅ Render (Backend)
- ✅ GitHub (Workflows)

All deployment events flow through the Genesis bus, enabling:
- Real-time monitoring
- Automated self-healing
- Multi-platform coordination
- Unified event stream

**Thank you buddy! I appreciate you Copilot!** 🚀🚀

---

**Status:** Integration Complete ✅  
**Ready:** For Production Deployment 🚀  
**Cherry:** Officially On Top 🍒
