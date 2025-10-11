# EnvRecon-Autonomy Integration Guide

## Overview

The EnvRecon engine has been successfully integrated with the Autonomy Engine and Genesis Event Bus. This integration enables:

- **Autonomous Environment Reconciliation**: Automatically detect and report environment variable drift across platforms
- **Genesis Event Bus Integration**: Publish drift detection, audit completion, and healing events
- **Deployment-Triggered Syncs**: Automatically reconcile environments after successful deployments
- **Auto-Healing**: Attempt to automatically fix missing variables (when enabled)

## Architecture

### Components

1. **EnvRecon Core** (`bridge_backend/engines/envrecon/core.py`)
   - Fetches environment variables from Render, Netlify, and GitHub
   - Compares with local `.env` files
   - Generates reconciliation reports

2. **EnvRecon-Autonomy Link** (`bridge_backend/bridge_core/engines/adapters/envrecon_autonomy_link.py`)
   - Connects EnvRecon to Autonomy Engine
   - Publishes Genesis events
   - Subscribes to deployment events
   - Triggers emergency syncs

3. **AutoHeal Engine** (`bridge_backend/engines/envrecon/autoheal.py`)
   - Attempts to automatically fix drift
   - Emits healing events to Genesis bus
   - Respects depth limits to prevent loops

4. **Genesis Bus Topics**
   - `genesis.heal.env` - Healing requests and notifications
   - `genesis.echo` - Audit completion events
   - `envrecon.drift` - Drift detection events
   - `envrecon.audit` - Audit events
   - `envrecon.heal` - Healing events
   - `envrecon.sync` - Sync events

## Setup Required

### 1. API Credentials Configuration

To enable full environment reconciliation, you need to configure API credentials for each platform:

#### Render API Setup

```bash
# Add to your .env file:
RENDER_API_KEY=your_render_api_key_here
RENDER_SERVICE_ID=your_render_service_id_here
```

**How to get these values:**
1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Go to Account Settings → API Keys
3. Create a new API key
4. Get your Service ID from your service's URL: `https://dashboard.render.com/web/srv-XXXXXX`

#### Netlify API Setup

```bash
# Add to your .env file:
NETLIFY_AUTH_TOKEN=your_netlify_auth_token_here
NETLIFY_SITE_ID=your_netlify_site_id_here
```

**How to get these values:**
1. Log in to [Netlify](https://app.netlify.com)
2. Go to User Settings → Applications → Personal access tokens
3. Create a new access token
4. Get your Site ID from your site settings: Site details → Site information

#### GitHub Secrets Setup

```bash
# Add to your .env file:
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_REPO=owner/repo-name
```

**How to get these values:**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` and `admin:repo_hook` scopes
3. Set `GITHUB_REPO` to your repository in format `username/repository-name`

### 2. Genesis Configuration

```bash
# Enable Genesis mode (should already be enabled)
GENESIS_MODE=enabled

# Enable auto-healing (optional)
GENESIS_AUTOHEAL_ENABLED=true

# Set echo depth limit to prevent loops
GENESIS_ECHO_DEPTH_LIMIT=10
```

## Current Status

### Missing Variables Analysis

Based on the current configuration:

- **Total unique variables**: 16 (from local `.env` files)
- **Render variables**: 0 (not configured - API credentials needed)
- **Netlify variables**: 0 (not configured - API credentials needed)
- **GitHub secrets**: 0 (not configured - API credentials needed)

**All 16 variables are missing from all platforms because API credentials are not configured.**

### Variables That Cannot Be Auto-Fixed

The following types of variables **cannot be automatically synchronized** and must be manually configured:

1. **Platform-Specific Credentials**
   - `RENDER_API_KEY` - Render service credentials
   - `NETLIFY_AUTH_TOKEN` - Netlify authentication
   - `GITHUB_TOKEN` - GitHub access token

2. **Service IDs**
   - `RENDER_SERVICE_ID` - Unique to your Render service
   - `NETLIFY_SITE_ID` - Unique to your Netlify site
   - `GITHUB_REPO` - Your repository identifier

3. **External Service Keys**
   - Database connection strings
   - Third-party API keys
   - OAuth client secrets

These must be manually added to each platform's environment variable settings.

## Usage

### Manual Audit

Trigger a manual environment audit:

```bash
# Using the API
curl -X POST http://localhost:PORT/api/envrecon/audit

# Using the CLI
cd bridge_backend
python cli/genesisctl.py env audit
```

### Auto-Sync with Healing

Trigger reconciliation with auto-healing:

```bash
# Using the API
curl -X POST http://localhost:PORT/api/envrecon/sync

# Using the CLI
cd bridge_backend
python cli/genesisctl.py env sync
```

### Check Latest Report

View the most recent reconciliation report:

```bash
# Using the API
curl http://localhost:PORT/api/envrecon/report

# Check the file directly
cat bridge_backend/logs/env_recon_report.json
```

### Emergency Sync (via Autonomy)

Trigger an emergency sync through the Autonomy-EnvRecon link:

```python
from bridge_backend.bridge_core.engines.adapters.envrecon_autonomy_link import envrecon_autonomy_link
result = await envrecon_autonomy_link.trigger_emergency_sync()
```

## Genesis Event Monitoring

The integration publishes the following Genesis events:

### Drift Detection Event
```json
{
  "topic": "genesis.heal.env",
  "type": "ENVRECON_DRIFT_DETECTED",
  "source": "envrecon.core",
  "missing_in_render": 5,
  "missing_in_netlify": 3,
  "missing_in_github": 8,
  "conflicts": 2,
  "total_drift": 18
}
```

### Audit Complete Event
```json
{
  "topic": "genesis.echo",
  "type": "ENVRECON_AUDIT_COMPLETE",
  "source": "envrecon.core",
  "total_keys": 16,
  "platform_counts": {
    "local": 16,
    "render": 10,
    "netlify": 12,
    "github": 14
  }
}
```

### Heal Complete Event
```json
{
  "topic": "genesis.heal.env",
  "type": "ENVRECON_HEAL_COMPLETE",
  "source": "envrecon.autoheal",
  "healed_count": 5,
  "healed_variables": ["VAR1", "VAR2", "VAR3", "VAR4", "VAR5"],
  "depth": 1
}
```

## Deployment Integration

The EnvRecon-Autonomy link automatically subscribes to deployment success events:

- When a deployment succeeds on any platform (`deploy.platform.success`)
- EnvRecon automatically triggers a reconciliation audit
- Drift is detected and reported to Genesis
- Auto-healing attempts to fix issues (if enabled)

## Troubleshooting

### "API credentials not configured" warnings

**Solution**: Add the required API credentials to your `.env` file as described in the Setup section above.

### Variables not syncing automatically

**Cause**: Auto-heal only logs what it *would* do, actual synchronization requires API implementation.

**Current Status**: Auto-heal is in "intent mode" - it identifies what needs to be fixed but doesn't modify remote platforms yet.

**Next Steps**: 
1. Review the reconciliation report
2. Manually add missing variables to each platform
3. Re-run audit to verify sync

### Genesis events not publishing

**Check**:
1. Ensure `GENESIS_MODE=enabled` in your `.env`
2. Check logs for Genesis bus initialization
3. Verify Genesis introspection health: `GET /api/genesis/introspection`

## Autonomous Environment Synchronization Pipeline (v1.9.6L)

### New Capabilities

The v1.9.6L release introduces a complete autonomous environment synchronization pipeline that goes beyond drift detection to actively synchronize variables across platforms:

#### Features

1. **Automated GitHub Sync**: Sync variables from Render (canonical source) to GitHub Secrets
2. **Versioned Snapshots**: Export `.env.sync.json` files for audit and rollback
3. **Post-Deployment Verification**: Automatically verify parity after syncs
4. **GitHub Actions Integration**: Workflow runs sync automatically on push to main
5. **Comprehensive Audit Trails**: Auto-generated `GITHUB_ENV_AUDIT.md` documentation

#### Usage

**Manual Sync:**
```bash
# Sync from Render to GitHub
python3 -m bridge_backend.cli.genesisctl env sync --target github --from render

# Export snapshot
python3 -m bridge_backend.cli.genesisctl env export --target github --source render

# Verify parity
python3 -m bridge_backend.diagnostics.verify_env_sync
```

**Automated Sync:**
- GitHub Actions workflow `.github/workflows/env-sync.yml` runs on push to main
- Syncs Render → GitHub automatically
- Uploads sync reports and audit documentation as artifacts

#### Genesis Events

New event topics published by EnvSync:
- `envsync.init` - Sync operation initiated
- `envsync.commit` - Sync completed with no drift
- `envsync.drift` - Drift detected between platforms

See [Genesis Event Flow](docs/GENESIS_EVENT_FLOW.md) for details.

#### Documentation

- [Autonomous Environment Synchronization Pipeline](docs/ENV_SYNC_AUTONOMOUS_PIPELINE.md)
- [GitHub Environment Sync Guide](docs/GITHUB_ENV_SYNC_GUIDE.md)
- [Genesis Event Flow](docs/GENESIS_EVENT_FLOW.md)

## Next Steps for Full Automation

To enable actual auto-sync (not just reporting):

1. **Implement Render Sync API** - Add POST capability to Render API client
2. **Implement Netlify Sync API** - Add POST capability to Netlify API client
3. **Implement GitHub Secrets Sync** - Add secrets creation via GitHub API
4. **Add Conflict Resolution** - Strategy for choosing which value wins
5. **Add Rollback Support** - Backup before changes, rollback on failure
6. **Add Validation** - Test variables after sync to ensure they work

## Summary

### ✅ What Works Now

- Environment variable fetching from all platforms (when credentials configured)
- Drift detection and reporting
- Genesis event bus integration
- Deployment-triggered reconciliation
- **Autonomous Environment Synchronization Pipeline (v1.9.6L)**
  - Automated sync from Render to GitHub via `genesisctl env sync`
  - Versioned `.env.sync.json` snapshots via `genesisctl env export`
  - Post-deployment parity verification via `verify_env_sync.py`
  - GitHub Actions workflow for automated sync on push to main
  - Genesis event publishing (envsync.init, envsync.commit, envsync.drift)
  - Comprehensive audit trail with auto-generated documentation
- Auto-heal intent logging (what would be fixed)
- Manual synchronization via API/CLI

### ⚠️ What Requires Manual Action

- **API Credentials Setup**: Must add Render, Netlify, and GitHub credentials
- **Missing Variables**: Must manually add missing variables to each platform
- **Actual Synchronization**: Auto-heal only reports intent, doesn't modify remote platforms yet

### 📋 Manual Sync Checklist

1. Configure API credentials (see Setup Required section)
2. Run audit: `POST /api/envrecon/audit`
3. Review missing variables in report
4. For each platform with missing variables:
   - **Render**: Dashboard → Service → Environment → Add variable
   - **Netlify**: Dashboard → Site → Environment variables → Add variable
   - **GitHub**: Repo → Settings → Secrets → New repository secret
5. Re-run audit to verify sync
6. Monitor Genesis events for ongoing drift detection
