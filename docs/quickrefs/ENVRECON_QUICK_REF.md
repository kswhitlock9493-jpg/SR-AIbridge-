# Genesis v2.0.2 EnvRecon - Quick Reference

## CLI Commands

```bash
# Audit all platforms
./genesisctl env audit

# Sync to specific platform
./genesisctl env sync --target=render
./genesisctl env sync --target=netlify
./genesisctl env sync --target=github

# Trigger auto-healing
./genesisctl env heal
```

## API Endpoints

```bash
# Health check
GET /api/envrecon/health

# Get report
GET /api/envrecon/report

# Run audit
POST /api/envrecon/audit

# Sync all
POST /api/envrecon/sync

# Trigger heal
POST /api/envrecon/heal

# Sync GitHub secrets
POST /api/envrecon/sync/github
```

## Inspector Panel

```
Local:  http://localhost:8000/genesis/envrecon
Render: https://bridge.sr-aibridge.com/genesis/envrecon
```

## Environment Variables

```bash
# Required
GITHUB_TOKEN=your_token
GITHUB_REPO=owner/repo
# Legacy RENDER_API_KEY removed=your_key
# Legacy RENDER_SERVICE_ID removed=your_id
NETLIFY_AUTH_TOKEN=your_token
NETLIFY_SITE_ID=your_id

# Optional
GENESIS_AUTOHEAL_ENABLED=true
GENESIS_ECHO_DEPTH_LIMIT=10
HUBSYNC_DRYRUN=false
```

## Report Location

```
bridge_backend/logs/env_recon_report.json
```

## Key Features

- ✅ Cross-platform reconciliation
- ✅ GitHub Secrets sync (HubSync)
- ✅ Auto-healing with recursion control
- ✅ Visual Inspector Panel
- ✅ CLI commands
- ✅ REST API
- ✅ Genesis event bus integration

## Status Indicators

- ✅ Green - Variable present
- ❌ Red - Variable missing
- ⚠️ Orange - Conflict detected
- 🔧 Blue - Auto-fixed

## Testing

```bash
cd bridge_backend
python3 tests/test_envrecon.py
python3 tests/test_hubsync.py
python3 tests/test_inspector_ui.py
```

---

For detailed documentation, see: `GENESIS_V2_0_2_ENVRECON_GUIDE.md`
