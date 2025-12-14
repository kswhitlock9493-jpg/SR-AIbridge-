# GitHub Environment Sync Guide

**Component:** EnvSync + HubSync Integration  
**Version:** v1.9.6L  
**Purpose:** Synchronize environment variables from Render to GitHub Secrets

---

## 🎯 Purpose

This guide explains how to synchronize environment variables from Render (verified canonical source) to GitHub Actions Secrets, ensuring your CI/CD workflows have access to the latest configuration.

---

## 🚀 Quick Sync

### Command Line

```bash
# Sync from Render to GitHub
python3 -m bridge_backend.cli.genesisctl env sync --target github --from render

# Export snapshot for audit
python3 -m bridge_backend.cli.genesisctl env export --target github --source render

# Verify sync succeeded
python3 -m bridge_backend.diagnostics.verify_env_sync
```

### GitHub Actions

The sync runs automatically on every push to `main`:

```yaml
# .github/workflows/env-sync.yml
name: 🔁 Bridge Env Sync
on:
  push:
    branches: [ main ]
  workflow_dispatch:
```

Manual trigger: Go to Actions → Bridge Env Sync → Run workflow

---

## 🔐 Required Secrets

### In GitHub Repository Secrets

Set these in **Settings → Secrets and variables → Actions**:

| Secret Name | Description | How to Get |
|------------|-------------|------------|
| `RENDER_API_KEY` | Render API authentication | Render Dashboard → Account Settings → API Keys |
| `RENDER_SERVICE_ID` | Service identifier | Render Dashboard → Service → Settings (in URL) |
| `GITHUB_TOKEN` | Automatic (provided by Actions) | No setup needed |

### In Render Environment

Set these in **Render Dashboard → Service → Environment**:

| Variable | Value |
|----------|-------|
| `GITHUB_TOKEN` | Personal access token (for bi-directional sync) |
| `GITHUB_REPO` | `owner/repository-name` |

---

## 📊 How It Works

### 1. Fetch Phase

```
EnvRecon Engine → Render API
                ↓
        Fetch all env vars
                ↓
        Filter by prefix rules
```

### 2. Compare Phase

```
GitHub Secrets API → List existing secrets
                   ↓
            Compare with Render
                   ↓
        Identify missing/changed
```

### 3. Sync Phase

```
For each missing variable:
    ↓
Get GitHub public key
    ↓
Encrypt variable value
    ↓
PUT to GitHub Secrets API
    ↓
Verify creation
```

### 4. Verify Phase

```
Run verify_env_sync.py
    ↓
Check all platforms
    ↓
Generate parity report
    ↓
Publish to Genesis Bus
```

---

## 🔍 Understanding the Output

### Successful Sync

```
🔄 Syncing to GitHub from Render...
✅ Fetched 45 variables from Render
📊 Sync Analysis:
  Variables to sync: 5

  Missing in GitHub:
    - AUTO_DIAGNOSE
    - CORS_ALLOW_ALL
    - REACT_APP_API_URL
    - ALLOWED_ORIGINS
    - DEBUG

✅ Synced 5/5 variables to GitHub
📤 Exporting environment sync snapshot...
✅ Exported 45 variables from render
📄 Snapshot saved to: bridge_backend/config/.env.sync.json
```

### Drift Detected

```
⚠️ Environment drift detected!
   Missing (Render): 0
   Missing (Netlify): 2
   Missing (GitHub): 5
   Conflicts: 1

📄 Report saved to: bridge_backend/logs/env_parity_check.json
```

---

## 📄 Generated Artifacts

### .env.sync.json

**Location:** `bridge_backend/config/.env.sync.json`

Machine-readable snapshot of the sync operation:

```json
{
  "provider": "github",
  "source": "render",
  "synced_at": "2025-10-11T22:43:00Z",
  "variables": {
    "AUTO_DIAGNOSE": "true",
    "CORS_ALLOW_ALL": "true"
  }
}
```

### env_parity_check.json

**Location:** `bridge_backend/logs/env_parity_check.json`

Detailed drift analysis:

```json
{
  "verified_at": "2025-10-11T22:45:00Z",
  "has_drift": false,
  "missing_in_render": [],
  "missing_in_netlify": [],
  "missing_in_github": [],
  "conflicts": {},
  "summary": {
    "total_keys": 45,
    "local_count": 45,
    "render_count": 45,
    "netlify_count": 43,
    "github_count": 45
  }
}
```

### GITHUB_ENV_AUDIT.md

**Location:** `docs/audit/GITHUB_ENV_AUDIT.md`

Human-readable audit log:

```markdown
# GitHub Environment Sync Log

**Sync Date:** 2025-10-11 22:43:00 UTC
**Workflow:** env-sync
**Run ID:** 1234567890

## Sync Report

**Source:** render
**Target:** github
**Variables Exported:** 45

## Parity Verification

**Status:** ✅ No Drift
**Verified At:** 2025-10-11T22:45:00Z
```

---

## 🔧 Advanced Configuration

### Filtering Variables

Control which variables are synced:

**In `bridge_backend/bridge_core/engines/envsync/config.py`:**

```python
ENVSYNC_INCLUDE_PREFIXES = ["REACT_APP_", "API_", "DATABASE_"]
ENVSYNC_EXCLUDE_PREFIXES = ["SECRET_", "PRIVATE_"]
```

### Dry Run Mode

Test sync without making changes:

```bash
HUBSYNC_DRYRUN=true python3 -m bridge_backend.cli.genesisctl env sync --target github --from render
```

### Custom Canonical Source

Use EnvSync Seed Manifest instead of Render:

**In environment:**
```bash
ENVSYNC_CANONICAL_SOURCE=file
```

**Location:** `bridge_backend/.genesis/envsync_seed_manifest.env`

---

## 🧪 Testing

### Test Connection

```bash
# Test Render API connectivity
python3 -c "
import asyncio
import sys
sys.path.insert(0, 'bridge_backend')
from engines.envrecon.core import EnvReconEngine

async def test():
    engine = EnvReconEngine()
    vars = await engine.fetch_render_env()
    print(f'✅ Connected to Render: {len(vars)} variables')

asyncio.run(test())
"
```

### Test GitHub Secrets API

```bash
# Test GitHub connectivity
python3 -c "
import asyncio
import sys
sys.path.insert(0, 'bridge_backend')
from engines.envrecon.hubsync import hubsync

async def test():
    key = await hubsync.get_public_key()
    if key:
        print('✅ Connected to GitHub Secrets API')
    else:
        print('❌ Failed to connect')

asyncio.run(test())
"
```

---

## 🆘 Troubleshooting

### "GitHub sync not configured"

**Cause:** Missing `GITHUB_TOKEN` or `GITHUB_REPO`  
**Fix:**
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
export GITHUB_REPO="owner/repo-name"
```

### "Failed to fetch Render env"

**Cause:** Invalid or missing Render credentials  
**Fix:**
1. Verify `RENDER_API_KEY` in GitHub Secrets
2. Check `RENDER_SERVICE_ID` matches your service
3. Test: `curl -H "Authorization: Bearer $RENDER_API_KEY" https://api.render.com/v1/services`

### Secrets Not Appearing in GitHub

**Cause:** GitHub API delay or permission issue  
**Fix:**
1. Wait 1-2 minutes for GitHub to process
2. Check Actions → Secrets for new entries
3. Verify token has `repo` and `secrets` scopes

### Variables Keep Showing as Drift

**Cause:** Firewall blocking verification calls  
**Fix:**
1. Check workflow logs for DNS/timeout errors
2. Review firewall allow list
3. Consider running verification from Render instead

---

## 📚 Related Topics

- [Autonomous Environment Synchronization Pipeline](./ENV_SYNC_AUTONOMOUS_PIPELINE.md)
- [EnvSync Seed Manifest](./ENVSYNC_SEED_MANIFEST.md)
- [EnvRecon Autonomy Integration](../ENVRECON_AUTONOMY_INTEGRATION.md)

---

**Last Updated:** October 11, 2025  
**Maintained by:** SR-AIbridge DevOps Team
