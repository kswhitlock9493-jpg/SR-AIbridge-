# Genesis v2.0.2 - EnvRecon Implementation Guide

## 🚀 Overview

Genesis v2.0.2 introduces **EnvRecon**, a self-healing, self-auditing environment synchronization ecosystem that unifies Render, Netlify, GitHub, and local configurations into one harmonized, transparent management framework.

### Key Features

- **🔍 Cross-Platform Reconciliation**: Audits and normalizes variables across .env files, Render API, Netlify API, and GitHub Secrets
- **🤝 HubSync Layer**: GitHub Secrets integration with drift detection and auto-sync
- **🩹 Auto-Healing**: Autonomous correction of environment drift via Genesis event bus
- **🧭 Inspector Panel**: Full web dashboard for visual oversight and one-click remediation

---

## 📦 What's New

### Components Added

1. **EnvRecon Engine** (`bridge_backend/engines/envrecon/`)
   - `core.py` - Cross-platform reconciliation engine
   - `hubsync.py` - GitHub Secrets synchronization layer
   - `autoheal.py` - Auto-healing subsystem with Genesis integration
   - `routes.py` - REST API endpoints
   - `ui.py` - Inspector Panel web interface

2. **CLI Commands** (`genesisctl`)
   - `genesisctl env audit` - Run environment audit
   - `genesisctl env sync` - Sync to specific platforms
   - `genesisctl env heal` - Trigger auto-healing

3. **Test Suite**
   - `test_envrecon.py` - Core engine tests
   - `test_hubsync.py` - GitHub integration tests
   - `test_inspector_ui.py` - UI component tests

---

## 🛠️ Installation & Setup

### Prerequisites

```bash
# Required Python packages (already in requirements.txt)
pip install httpx python-dotenv PyNaCl
```

### Environment Variables

Add these to your `.env` or platform configuration:

```bash
# GitHub Integration (for HubSync)
GITHUB_TOKEN=your_github_token
GITHUB_REPO=kswhitlock9493-jpg/SR-AIbridge-

# Render Integration
RENDER_API_KEY=your_render_api_key
RENDER_SERVICE_ID=your_service_id

# Netlify Integration
NETLIFY_AUTH_TOKEN=your_netlify_token
NETLIFY_SITE_ID=your_site_id

# Optional: Auto-Heal Configuration
GENESIS_AUTOHEAL_ENABLED=true
GENESIS_ECHO_DEPTH_LIMIT=10
HUBSYNC_DRYRUN=false
```

---

## 📘 Usage

### CLI Commands

#### 1. Run Environment Audit

Scans all platforms and generates a reconciliation report:

```bash
./genesisctl env audit
```

**Output:**
```
🔍 Running environment audit...

📊 Audit Results:
  Total variables: 42
  Missing in Render: 8
  Missing in Netlify: 5
  Missing in GitHub: 12
  Conflicts: 2

📄 Report saved to: bridge_backend/logs/env_recon_report.json
```

#### 2. Sync Environment Variables

```bash
# Sync to all platforms (runs audit + shows report)
./genesisctl env sync

# Sync to specific platform
./genesisctl env sync --target=render
./genesisctl env sync --target=netlify
./genesisctl env sync --target=github
```

#### 3. Trigger Auto-Healing

```bash
./genesisctl env heal
```

**Output:**
```
🩹 Running auto-heal...

✅ Auto-heal complete
  Healed variables: 8
    - RENDER_API_KEY
    - NETLIFY_AUTH_TOKEN
    - DATABASE_URL
    ...
```

---

### API Endpoints

#### Health Check
```http
GET /api/envrecon/health
```

**Response:**
```json
{
  "status": "healthy",
  "engine": "EnvRecon v2.0.2",
  "features": ["reconciliation", "hubsync", "autoheal", "inspector"]
}
```

#### Get Reconciliation Report
```http
GET /api/envrecon/report
```

**Response:**
```json
{
  "missing_in_render": ["VAR1", "VAR2"],
  "missing_in_netlify": ["VAR3"],
  "missing_in_github": ["VAR4", "VAR5"],
  "conflicts": {
    "DATABASE_URL": {
      "render": "postgres://prod",
      "local": "postgres://dev"
    }
  },
  "autofixed": [],
  "timestamp": "2025-10-11T12:00:00Z",
  "summary": {
    "total_keys": 42,
    "local_count": 40,
    "render_count": 35,
    "netlify_count": 38,
    "github_count": 30
  }
}
```

#### Run Audit
```http
POST /api/envrecon/audit
```

#### Sync All Platforms
```http
POST /api/envrecon/sync
```

#### Trigger Healing
```http
POST /api/envrecon/heal
```

#### Sync GitHub Secrets
```http
POST /api/envrecon/sync/github
Content-Type: application/json

[
  {"name": "SECRET_NAME", "value": "secret_value"},
  {"name": "ANOTHER_SECRET", "value": "another_value"}
]
```

---

### Inspector Panel UI

Access the visual dashboard at:

```
http://localhost:8000/genesis/envrecon
```

or on deployed instances:

```
https://sr-aibridge.onrender.com/genesis/envrecon
```

#### Features:

- **Live Parity Visualization**: See which variables exist on each platform
- **Conflict Detection**: Visual indicators for mismatched values
- **One-Click Actions**:
  - 🔍 Run Audit
  - 🔄 Sync All
  - 🩹 Heal Now
  - 📄 Refresh Report
- **Auto-Refresh**: Real-time updates via periodic polling
- **Color-Coded Status**:
  - ✅ Green - Variable present
  - ❌ Red - Variable missing
  - ⚠️ Orange - Conflict detected
  - 🔧 Blue - Auto-fixed

---

## 🧠 Architecture

```
Local .env Files
     ↓
EnvRecon Engine ←→ Render API
     ↓                ↓
HubSync Layer ←→ Netlify API
     ↓                ↓
Auto-Heal ←────→ GitHub API
     ↓
Genesis Event Bus
     ↓
Inspector Panel (Web UI)
```

### Data Flow

1. **Audit Phase**: EnvRecon fetches variables from all sources
2. **Diff Generation**: Compares values and identifies mismatches
3. **Report Generation**: Creates JSON report with categorized issues
4. **Auto-Heal** (optional): Genesis event bus triggers healing
5. **UI Display**: Inspector Panel visualizes the report

---

## 🧪 Testing

### Run Test Suite

```bash
# Run all EnvRecon tests
cd bridge_backend
python3 tests/test_envrecon.py
python3 tests/test_hubsync.py
python3 tests/test_inspector_ui.py
```

### Expected Output

```
============================================================
EnvRecon Engine - Test Suite v2.0.2
============================================================

✅ PASS: Module Import
✅ PASS: Core Engine Init
✅ PASS: Local ENV Loading
✅ PASS: HubSync Import
✅ PASS: AutoHeal Import
✅ PASS: Routes Import
✅ PASS: UI Import

Total: 7/7 tests passed
```

---

## 🔐 Security Considerations

### GitHub Token Permissions

For HubSync to work, your GitHub token needs:
- `repo` - Full control of private repositories
- `secrets` - Manage GitHub Actions secrets

### Dry-Run Mode

To preview changes without making them:

```bash
export HUBSYNC_DRYRUN=true
./genesisctl env sync --target=github
```

### Secret Masking

- GitHub secret **values** are not accessible via API (only names)
- Conflicts with GitHub secrets show as `<secret>` in reports
- Local values are never logged or exposed in API responses

---

## 🛡️ Guardian Safety & Recursion Control

EnvRecon integrates with Genesis Guardian system:

- **Recursion Depth Limit**: Prevents infinite healing loops (default: 10)
- **Guardian Gate Enforcement**: Blocks unsafe operations
- **Auto-Healing Deferment**: Pauses during heavy deploy conditions

Configure limits:

```bash
GENESIS_ECHO_DEPTH_LIMIT=10
GENESIS_AUTOHEAL_ENABLED=true
```

---

## 📊 Report Schema

The JSON report follows this schema:

```typescript
{
  missing_in_render: string[],
  missing_in_netlify: string[],
  missing_in_github: string[],
  extra_in_render: string[],
  extra_in_netlify: string[],
  conflicts: {
    [key: string]: {
      render?: string,
      netlify?: string,
      github?: string,
      local?: string
    }
  },
  autofixed: string[],
  timestamp: string,
  summary: {
    total_keys: number,
    local_count: number,
    render_count: number,
    netlify_count: number,
    github_count: number
  }
}
```

---

## 🔄 Integration with Existing Systems

### Genesis Event Bus

EnvRecon emits healing events:

```python
await emit_heal(
    topic="genesis.heal.env",
    source="envrecon.autoheal",
    payload={
        "report_summary": {...},
        "timestamp": "2025-10-11T12:00:00Z"
    }
)
```

### TDE-X Deploy Pipeline

Auto-heal runs during post-deploy stages when drift is detected.

### EnvSync v2.0.1a

EnvRecon complements the existing EnvSync engine:
- **EnvSync**: Continuous sync between Render ↔ Netlify
- **EnvRecon**: Comprehensive audit including GitHub + local

---

## 🎯 Best Practices

1. **Run Audits Regularly**: Schedule `genesisctl env audit` in CI/CD
2. **Review Before Sync**: Always check reports before syncing
3. **Use Dry-Run**: Test GitHub sync with `HUBSYNC_DRYRUN=true`
4. **Monitor Auto-Heal**: Watch for recursion depth warnings
5. **Keep Credentials Secure**: Never commit `.env` files

---

## 🐛 Troubleshooting

### "No report available"
Run `genesisctl env audit` first to generate a report.

### GitHub sync fails
- Check `GITHUB_TOKEN` has correct permissions
- Verify `GITHUB_REPO` format: `owner/repo`
- Ensure token hasn't expired

### Auto-heal not working
- Check `GENESIS_AUTOHEAL_ENABLED=true`
- Verify Genesis event bus is running
- Review depth limit: `GENESIS_ECHO_DEPTH_LIMIT`

### UI returns 404
- Ensure app is running: `python3 -m uvicorn bridge_backend.main:app`
- Check logs for router registration: `[ENVRECON] v2.0.2 routes enabled`

---

## 📝 Changelog

### v2.0.2 (2025-10-11)

**Added:**
- EnvRecon cross-platform reconciliation engine
- HubSync GitHub Secrets integration
- Auto-healing subsystem with Genesis integration
- Inspector Panel web UI
- `genesisctl` CLI commands
- Comprehensive test suite

**Integration:**
- Registered routes in `main.py`
- Genesis event bus integration
- Guardian safety enforcement

---

## 🚀 Next Steps

1. **Frontend Integration**: Add Inspector Panel to React dashboard
2. **Scheduled Audits**: Automate periodic reconciliation
3. **Alert System**: Notify on drift detection
4. **Bulk Sync**: Implement one-click sync for all platforms
5. **History Tracking**: Store report history for trend analysis

---

## 📞 Support

For issues or questions:
1. Check logs: `bridge_backend/logs/env_recon_report.json`
2. Run diagnostics: `genesisctl env audit`
3. Review test suite: `python3 tests/test_envrecon.py`

---

**Genesis v2.0.2 - Self-healing environments with zero manual upkeep** ✨
