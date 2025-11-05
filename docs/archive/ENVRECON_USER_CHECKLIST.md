# EnvRecon-Autonomy Integration - User Checklist

## ✅ What's Already Done (by AI)

- [x] Created EnvRecon-Autonomy adapter link
- [x] Added Genesis bus topics for envrecon events
- [x] Integrated adapter with EnvRecon core
- [x] Updated autoheal with Genesis events
- [x] Updated routes with healing notifications
- [x] Registered EnvRecon in Genesis linkage
- [x] Created comprehensive documentation
- [x] Added integration tests (all passing)
- [x] Verified main.py loads successfully

## 📋 What You Need to Do

### Step 1: Configure API Credentials (Required)

Add these to your `.env` file to enable environment variable fetching:

#### Render API Credentials
```bash
RENDER_API_KEY=your_render_api_key_here
RENDER_SERVICE_ID=srv-your_service_id_here
```

**How to get**:
1. Login to [Render Dashboard](https://dashboard.render.com)
2. Go to Account Settings → API Keys
3. Create new API key
4. Get Service ID from service URL: `srv-XXXXXX`

#### Netlify API Credentials
```bash
NETLIFY_AUTH_TOKEN=your_netlify_auth_token_here
NETLIFY_SITE_ID=your_netlify_site_id_here
```

**How to get**:
1. Login to [Netlify](https://app.netlify.com)
2. Go to User Settings → Applications → Personal access tokens
3. Create new access token
4. Get Site ID from Site settings → Site information

#### GitHub API Credentials
```bash
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_REPO=username/repo-name
```

**How to get**:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` and `admin:repo_hook` scopes
3. Set GITHUB_REPO to your repository: `username/repository-name`

### Step 2: Run Initial Audit

Once credentials are configured:

```bash
# Start the server
cd bridge_backend
python main.py

# In another terminal, run audit
curl -X POST http://localhost:8000/api/envrecon/audit
```

### Step 3: Get Missing Variables List

```bash
# Get the report
curl http://localhost:8000/api/envrecon/report

# Or check the file directly
cat bridge_backend/logs/env_recon_report.json

# Pretty print missing variables
curl http://localhost:8000/api/envrecon/report | jq '.missing_in_render, .missing_in_netlify, .missing_in_github'
```

### Step 4: Manually Sync Missing Variables

For each variable listed as missing:

#### Add to Render
1. Go to https://dashboard.render.com
2. Select your service
3. Go to Environment tab
4. Click "Add Environment Variable"
5. Add variable name and value from your local `.env`

#### Add to Netlify
1. Go to https://app.netlify.com
2. Select your site
3. Go to Site settings → Environment variables
4. Click "Add a variable"
5. Add variable name and value from your local `.env`

#### Add to GitHub
1. Go to your repository on GitHub
2. Go to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add variable name and value from your local `.env`

### Step 5: Verify Sync

After adding variables manually:

```bash
# Run another audit
curl -X POST http://localhost:8000/api/envrecon/audit

# Check for remaining drift
curl http://localhost:8000/api/envrecon/report | jq '.summary'
```

Expected output when synced:
```json
{
  "total_keys": 16,
  "local_count": 16,
  "render_count": 16,
  "netlify_count": 16,
  "github_count": 16
}
```

## 🔍 How to Monitor Going Forward

### Automatic Monitoring (Already Active)

The integration will automatically:
- ✅ Run reconciliation after every deployment
- ✅ Detect drift and publish Genesis events
- ✅ Alert via Genesis event bus
- ✅ Log all audits to JSON file

### Manual Monitoring

```bash
# Check latest report
curl http://localhost:8000/api/envrecon/report

# Trigger manual audit
curl -X POST http://localhost:8000/api/envrecon/audit

# Trigger auto-heal (reports intent only)
curl -X POST http://localhost:8000/api/envrecon/sync
```

### Genesis Event Monitoring

Subscribe to these Genesis topics to get notifications:
- `genesis.heal.env` - Drift detection and healing events
- `genesis.echo` - Audit completion events
- `envrecon.drift` - EnvRecon-specific drift events
- `envrecon.heal` - Healing events

## ⚠️ Important Notes

### Auto-Sync Limitation

**Current status**: Auto-heal is in "intent mode"
- ✅ **CAN**: Detect missing variables
- ✅ **CAN**: Detect conflicts
- ✅ **CAN**: Report what needs fixing
- ✅ **CAN**: Emit Genesis events
- ❌ **CANNOT**: Automatically add variables to platforms

**Reason**: Write APIs not implemented yet (safety feature)

**Workaround**: Manual sync as described in Step 4

### Variables That Must Be Manually Synced

**ALL variables** currently require manual sync because:
1. Render write API not implemented
2. Netlify write API not implemented
3. GitHub secrets write API not implemented

This is intentional to prevent accidental changes to production environments.

## 📚 Documentation Reference

- `ENVRECON_AUTONOMY_INTEGRATION.md` - Complete integration guide
- `ENVRECON_UNFIXABLE_VARS.md` - Quick reference for variables
- `ENVRECON_AUTONOMY_SUMMARY.md` - Implementation summary
- `GENESIS_V2_0_2_ENVRECON_GUIDE.md` - EnvRecon engine docs

## 🧪 Testing

Verify integration is working:

```bash
cd bridge_backend

# Run EnvRecon tests
python tests/test_envrecon.py

# Run integration tests
python tests/test_envrecon_autonomy_integration.py
```

Expected: All tests pass ✅

## 🎯 Success Criteria

You'll know everything is synced when:

1. ✅ All API credentials configured
2. ✅ Audit runs without warnings
3. ✅ Missing variables count = 0
4. ✅ Conflicts count = 0
5. ✅ All platform counts match local count
6. ✅ Genesis events publishing successfully

## ❓ Troubleshooting

### "API credentials not configured" warnings

**Solution**: Add the API credentials from Step 1

### Variables still showing as missing

**Check**:
1. Did you add the variable to the correct platform?
2. Did you use the exact variable name (case-sensitive)?
3. Did you restart the service after adding variables?
4. Run a fresh audit to get updated counts

### Genesis events not appearing

**Check**:
1. Is `GENESIS_MODE=enabled` in your `.env`?
2. Check Genesis health: `curl http://localhost:8000/api/genesis/introspection`
3. Check logs for Genesis initialization messages

### Auto-heal not working

**Remember**: Auto-heal only reports what it would fix, it doesn't modify platforms yet. This is expected behavior.

## 📞 Get Full Auto-Sync

If you need actual automatic synchronization implemented, please specify:

1. **Source of truth**: Which platform should be authoritative? (local, render, netlify, github)
2. **Conflict resolution**: How to handle different values across platforms?
3. **Safety requirements**: Backup? Rollback? Approval workflow?
4. **Validation**: Should variables be tested after sync?

With these requirements, the write APIs can be implemented for full auto-sync.

## Summary

✅ **Integration Complete**: EnvRecon is now linked to Autonomy Engine and Genesis Bus
📋 **Action Required**: Configure API credentials and manually sync variables
🔄 **Ongoing**: Automatic drift detection after deployments
📊 **Monitoring**: Genesis events and JSON reports
🔜 **Future**: Full auto-sync when write APIs are implemented
