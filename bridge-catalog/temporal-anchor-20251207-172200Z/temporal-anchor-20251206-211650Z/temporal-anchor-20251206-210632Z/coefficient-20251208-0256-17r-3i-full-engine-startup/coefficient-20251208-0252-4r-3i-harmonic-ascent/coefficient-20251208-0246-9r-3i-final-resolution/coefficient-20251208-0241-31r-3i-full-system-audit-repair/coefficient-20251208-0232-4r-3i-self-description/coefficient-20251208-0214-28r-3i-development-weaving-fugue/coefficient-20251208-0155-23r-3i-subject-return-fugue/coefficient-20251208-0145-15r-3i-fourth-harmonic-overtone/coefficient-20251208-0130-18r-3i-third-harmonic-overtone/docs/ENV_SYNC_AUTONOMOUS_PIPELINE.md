# Autonomous Environment Synchronization Pipeline

**Version:** v1.9.6L | **Status:** Production Ready  
**Components:** EnvSync, EnvRecon, Steward, Autonomy, Truth, Blueprint, Cascade  
**Integration:** Genesis Event Bus Orchestration

---

## 🧩 Overview

The Autonomous Environment Synchronization Pipeline provides seamless, automated environment variable synchronization across Render, Netlify, and GitHub platforms. This system ensures environment parity through continuous drift detection, automated healing, and comprehensive audit trails.

### Key Features

- **Autonomous Drift Detection**: Continuously monitors environment variable differences across platforms
- **Automated Synchronization**: Safely syncs variables from verified sources to target platforms
- **Versioned Snapshots**: Creates `.env.sync.json` snapshots for audit and rollback
- **Genesis Event Publishing**: Publishes all sync operations to the Genesis Event Bus
- **RBAC Security**: Permission Engine controls write access to environment variables
- **Audit Trail**: Immutable logs through the Truth Engine with Genesis correlation IDs

---

## 🚀 Quick Start

### Manual Sync

Sync environment variables from Render to GitHub:

```bash
python3 -m bridge_backend.cli.genesisctl env sync --target github --from render
```

### Export Snapshot

Create a versioned snapshot:

```bash
python3 -m bridge_backend.cli.genesisctl env export --target github --source render
```

### Verify Parity

Check environment parity across all platforms:

```bash
python3 -m bridge_backend.diagnostics.verify_env_sync
```

---

## 🛠️ Core Components

### 1. EnvSync Engine

**Location:** `bridge_backend/bridge_core/engines/envsync/`

The core synchronization engine that:
- Loads canonical environment from seed manifest or runtime
- Computes diffs between platforms
- Applies changes with permission validation
- Publishes events to Genesis Bus

### 2. EnvRecon Engine

**Location:** `bridge_backend/engines/envrecon/`

Reconciliation layer that:
- Fetches variables from Render, Netlify, GitHub APIs
- Detects missing variables and conflicts
- Generates comprehensive diff reports
- Triggers auto-healing when enabled

### 3. GenesisCtl CLI

**Location:** `bridge_backend/cli/genesisctl.py`

Command-line interface providing:
- `env audit` - Full environment audit
- `env sync` - Platform synchronization
- `env export` - Snapshot generation
- `env heal` - Auto-healing trigger

### 4. Environment Verifier

**Location:** `bridge_backend/diagnostics/verify_env_sync.py`

Post-deployment verification that:
- Validates environment parity
- Generates parity check reports
- Publishes drift/commit events to Genesis
- Returns appropriate exit codes for CI/CD

---

## 📊 GitHub Actions Integration

### Workflow: env-sync.yml

**Location:** `.github/workflows/env-sync.yml`

**Triggers:**
- Manual dispatch via workflow_dispatch
- Automatic on push to `main` branch

**Steps:**
1. Sync variables from Render to GitHub
2. Export sync snapshot
3. Verify environment parity
4. Upload sync and parity reports as artifacts
5. Generate audit documentation

**Artifacts:**
- `env_sync_report` - JSON sync report and snapshot
- `env_sync_audit` - Markdown audit documentation

---

## 🔐 Security & Permissions

### RBAC Integration

The Permission Engine enforces role-based access:

**Admiral-class roles:**
- Full read/write access to all platforms
- Can trigger manual syncs
- Access to audit trails

**Architect roles:**
- Read-only access to reports
- Can verify but not modify

**Other roles:**
- Read-only reporting mode only

### Secret Management

- Secrets are encrypted using platform-specific public keys
- GitHub secrets use NaCl sealed boxes
- Never logged or displayed in plain text
- Audit trails show variable names only, not values

---

## 📄 Sync Snapshot Format

**Location:** `bridge_backend/config/.env.sync.json`

```json
{
  "provider": "github",
  "source": "render",
  "synced_at": "2025-10-11T22:43:00Z",
  "variables": {
    "AUTO_DIAGNOSE": "true",
    "CORS_ALLOW_ALL": "true",
    "REACT_APP_API_URL": "https://sr-aibridge.onrender.com/api",
    "ALLOWED_ORIGINS": "https://sr-aibridge.netlify.app,https://sr-aibridge.onrender.com",
    "DEBUG": "false"
  }
}
```

---

## 🧾 Genesis Event Flow

### Event Topics

**envsync.init** - Sync operation initiated
```json
{
  "type": "sync_init",
  "source": "render",
  "target": "github",
  "timestamp": "2025-10-11T22:43:00Z"
}
```

**envsync.commit** - Sync completed successfully
```json
{
  "verified_at": "2025-10-11T22:45:00Z",
  "has_drift": false,
  "summary": {
    "total_keys": 45,
    "synced": 5
  }
}
```

**envsync.drift** - Drift detected
```json
{
  "verified_at": "2025-10-11T22:43:00Z",
  "has_drift": true,
  "missing_in_github": ["VAR1", "VAR2"],
  "conflicts": {"VAR3": {"render": "value1", "github": "value2"}}
}
```

---

## 🧪 Testing

### Run Tests

```bash
# Test EnvRecon engine
python3 -m bridge_backend.tests.test_envrecon

# Test manual sync (dry-run)
HUBSYNC_DRYRUN=true python3 -m bridge_backend.cli.genesisctl env sync --target github --from render
```

### Expected Exit Codes

- `0` - Success, no drift detected
- `1` - Drift detected or sync issues

---

## 📋 Audit Documentation

### Auto-Generated Audit Log

**Location:** `docs/audit/GITHUB_ENV_AUDIT.md`

Generated automatically after each sync, contains:
- Sync timestamp and workflow details
- Source and target platforms
- Variable counts and changes
- Drift detection results
- Genesis event correlation ID

---

## 🔧 Configuration

### Environment Variables

**Required for GitHub sync:**
- `GITHUB_TOKEN` - Personal access token with repo and secrets scope
- `GITHUB_REPO` - Repository in format `owner/repo`

**Required for Render:**
- `RENDER_API_KEY` - Render API key
- `RENDER_SERVICE_ID` - Service identifier

**Required for Netlify:**
- `NETLIFY_AUTH_TOKEN` - Netlify personal access token
- `NETLIFY_SITE_ID` - Site identifier

**Optional:**
- `HUBSYNC_DRYRUN=true` - Test mode, no actual changes

---

## 🆘 Troubleshooting

### Sync Fails with "Not Configured"

**Issue:** Missing GitHub credentials  
**Solution:** Set `GITHUB_TOKEN` and `GITHUB_REPO` environment variables

### Drift Persists After Sync

**Issue:** Firewall blocking API calls  
**Solution:** Check GitHub Actions logs for DNS/firewall blocks

### Variables Not Syncing

**Issue:** Permission denied or filter exclusion  
**Solution:** 
1. Verify RBAC role has write permissions
2. Check `ENVSYNC_INCLUDE_PREFIXES` and `ENVSYNC_EXCLUDE_PREFIXES`
3. Review EnvSync configuration in `bridge_backend/bridge_core/engines/envsync/config.py`

---

## 📚 Related Documentation

- [EnvRecon Autonomy Integration](../ENVRECON_AUTONOMY_INTEGRATION.md)
- [EnvSync Quick Reference](../ENVSYNC_QUICK_REF.md)
- [Genesis Event Flow](./GENESIS_EVENT_FLOW.md)
- [GitHub Environment Sync Guide](./GITHUB_ENV_SYNC_GUIDE.md)

---

**Maintained by:** Genesis v1.9.6L Integration Team  
**Last Updated:** October 11, 2025
