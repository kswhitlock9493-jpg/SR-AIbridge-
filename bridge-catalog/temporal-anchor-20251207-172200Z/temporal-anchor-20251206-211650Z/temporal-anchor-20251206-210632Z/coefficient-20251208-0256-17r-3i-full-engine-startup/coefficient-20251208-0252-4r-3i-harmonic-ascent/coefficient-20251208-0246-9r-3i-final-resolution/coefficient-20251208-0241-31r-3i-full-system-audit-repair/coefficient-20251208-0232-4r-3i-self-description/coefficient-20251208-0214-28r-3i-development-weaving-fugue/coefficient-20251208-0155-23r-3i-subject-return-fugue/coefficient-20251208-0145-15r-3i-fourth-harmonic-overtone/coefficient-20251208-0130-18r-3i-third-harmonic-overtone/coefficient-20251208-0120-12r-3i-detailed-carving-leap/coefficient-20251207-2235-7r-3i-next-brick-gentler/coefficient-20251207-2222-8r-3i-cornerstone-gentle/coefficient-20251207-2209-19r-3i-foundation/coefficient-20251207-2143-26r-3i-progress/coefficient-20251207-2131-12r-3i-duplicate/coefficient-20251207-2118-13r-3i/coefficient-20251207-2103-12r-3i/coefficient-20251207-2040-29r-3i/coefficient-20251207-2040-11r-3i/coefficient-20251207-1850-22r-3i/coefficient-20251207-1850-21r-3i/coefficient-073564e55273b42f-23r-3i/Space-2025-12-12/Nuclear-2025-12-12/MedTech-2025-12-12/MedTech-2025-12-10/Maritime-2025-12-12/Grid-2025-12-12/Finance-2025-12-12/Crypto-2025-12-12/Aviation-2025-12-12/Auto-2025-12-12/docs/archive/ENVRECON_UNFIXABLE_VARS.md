# Variables That Cannot Be Auto-Fixed - Quick Reference

## Summary

**Current Status**: EnvRecon-Autonomy integration is active but cannot automatically sync variables to remote platforms yet.

**Reason**: The current implementation is in "intent mode" - it detects drift and reports what needs to be fixed, but doesn't modify remote platforms.

## Categories of Unfixable Variables

### 1. API Credentials (Must Be Configured First)

These credentials are **required** to enable EnvRecon to read variables from platforms:

```bash
# Render API
RENDER_API_KEY=<your-render-api-key>
RENDER_SERVICE_ID=<your-render-service-id>

# Netlify API
NETLIFY_AUTH_TOKEN=<your-netlify-auth-token>
NETLIFY_SITE_ID=<your-netlify-site-id>

# GitHub API
GITHUB_TOKEN=<your-github-token>
GITHUB_REPO=<owner/repo-name>
```

**Where to get them**:
- Render: Dashboard → Account Settings → API Keys
- Netlify: User Settings → Applications → Personal access tokens
- GitHub: Settings → Developer settings → Personal access tokens

### 2. Platform-Specific Variables (Manual Sync Required)

Until full sync is implemented, **all variables** must be manually added to each platform:

#### Add to Render:
1. Go to https://dashboard.render.com
2. Select your service
3. Navigate to Environment tab
4. Click "Add Environment Variable"
5. Add each missing variable

#### Add to Netlify:
1. Go to https://app.netlify.com
2. Select your site
3. Navigate to Site settings → Environment variables
4. Click "Add a variable"
5. Add each missing variable

#### Add to GitHub:
1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each missing variable

## Current Missing Variables Count

Based on latest audit (requires API credentials to be accurate):

- **Missing in Render**: Unknown (API credentials not configured)
- **Missing in Netlify**: Unknown (API credentials not configured)
- **Missing in GitHub**: Unknown (API credentials not configured)

## To Get Accurate Missing Variables List

1. **Configure API credentials** (see section 1 above)

2. **Run audit**:
   ```bash
   curl -X POST http://localhost:PORT/api/envrecon/audit
   ```

3. **View report**:
   ```bash
   curl http://localhost:PORT/api/envrecon/report
   ```

4. **Check the JSON file**:
   ```bash
   cat bridge_backend/logs/env_recon_report.json
   ```

The report will show:
- `missing_in_render[]` - Variables that need to be added to Render
- `missing_in_netlify[]` - Variables that need to be added to Netlify
- `missing_in_github[]` - Variables that need to be added to GitHub
- `conflicts{}` - Variables with different values across platforms

## Auto-Heal Capabilities

### What Auto-Heal Can Do Now:
- ✅ Detect missing variables
- ✅ Detect conflicting values
- ✅ Report drift to Genesis bus
- ✅ Log healing intentions
- ✅ Track what needs to be fixed

### What Auto-Heal Cannot Do Yet:
- ❌ Actually add variables to Render
- ❌ Actually add variables to Netlify
- ❌ Actually add secrets to GitHub
- ❌ Resolve conflicts automatically
- ❌ Backup before changes
- ❌ Rollback failed syncs

## Workaround: Manual Sync Process

Until full auto-sync is implemented, use this process:

1. **Run audit to get missing variables**:
   ```bash
   curl -X POST http://localhost:PORT/api/envrecon/audit
   ```

2. **Get the list of missing variables**:
   ```bash
   curl http://localhost:PORT/api/envrecon/report | jq '.missing_in_render, .missing_in_netlify, .missing_in_github'
   ```

3. **For each missing variable**:
   - Copy the variable name and value from your local `.env` file
   - Add it to the platform(s) where it's missing using the web dashboards

4. **Verify sync**:
   ```bash
   curl -X POST http://localhost:PORT/api/envrecon/audit
   ```

5. **Check for remaining drift**:
   ```bash
   curl http://localhost:PORT/api/envrecon/report | jq '.summary'
   ```

## Genesis Events for Monitoring

Even though auto-fix isn't implemented, you can monitor drift via Genesis events:

- **Subscribe to**: `genesis.heal.env`
- **Event type**: `ENVRECON_DRIFT_DETECTED`
- **Payload includes**: Counts of missing variables per platform

Example event:
```json
{
  "type": "ENVRECON_DRIFT_DETECTED",
  "source": "envrecon.core",
  "missing_in_render": 5,
  "missing_in_netlify": 3,
  "missing_in_github": 8,
  "total_drift": 16
}
```

## Future Enhancement: Full Auto-Sync

To enable actual automatic synchronization, these features need to be implemented:

1. **Render Write API**: POST requests to add/update env vars
2. **Netlify Write API**: POST requests to add/update env vars
3. **GitHub Secrets API**: POST requests to create/update secrets
4. **Conflict Resolution**: Strategy for choosing which value to use
5. **Validation**: Test variables after sync
6. **Rollback**: Restore previous state on failure
7. **Audit Trail**: Log all changes made

## Contact for Implementation

If you need the full auto-sync feature implemented, provide:

1. Your preferred conflict resolution strategy
2. Which platform should be the "source of truth" (local .env, Render, Netlify, or GitHub)
3. Whether to backup before changes
4. Validation requirements (e.g., test database connection after adding DB vars)

## Quick Commands

```bash
# Check if API credentials are configured
env | grep -E "RENDER_API|NETLIFY_AUTH|GITHUB_TOKEN"

# Run audit
curl -X POST http://localhost:PORT/api/envrecon/audit

# Get report
curl http://localhost:PORT/api/envrecon/report

# Trigger auto-heal (reports intent only)
curl -X POST http://localhost:PORT/api/envrecon/sync

# Check Genesis health
curl http://localhost:PORT/api/genesis/introspection
```

## Documentation

For complete details, see:
- `ENVRECON_AUTONOMY_INTEGRATION.md` - Full integration guide
- `GENESIS_V2_0_2_ENVRECON_GUIDE.md` - EnvRecon engine documentation
- `ENVRECON_QUICK_REF.md` - Quick reference
