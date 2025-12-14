# Environment Sync Pipeline - Quick Reference

**Version:** v1.9.6L | **Status:** ✅ Production Ready

---

## 🚀 Quick Commands

### Sync from Render to GitHub
```bash
python3 -m bridge_backend.cli.genesisctl env sync --target github --from render
```

### Export Environment Snapshot
```bash
python3 -m bridge_backend.cli.genesisctl env export --target github --source render
```

### Verify Parity
```bash
python3 -m bridge_backend.diagnostics.verify_env_sync
```

### Run Full Audit
```bash
python3 -m bridge_backend.cli.genesisctl env audit
```

---

## 📊 GitHub Actions

**Workflow:** `.github/workflows/env-sync.yml`

**Trigger manually:**
1. Go to Actions → Bridge Env Sync
2. Click "Run workflow"
3. Select branch and click "Run workflow"

**Auto-runs on:**
- Push to `main` branch

**Artifacts:**
- `env_sync_report` - Sync snapshots and parity checks
- `env_sync_audit` - Generated audit documentation

---

## 🔐 Required Secrets

**GitHub Secrets (Settings → Secrets → Actions):**
- `RENDER_API_KEY` - From Render Dashboard → Account → API Keys
- `RENDER_SERVICE_ID` - From service URL or dashboard
- `NETLIFY_AUTH_TOKEN` - From Netlify User Settings → Applications
- `NETLIFY_SITE_ID` - From site settings
- `GITHUB_TOKEN` - Auto-provided (no setup needed)

---

## 📄 Files & Locations

**Commands:**
- `bridge_backend/cli/genesisctl.py` - CLI tool

**Diagnostics:**
- `bridge_backend/diagnostics/verify_env_sync.py` - Parity verifier

**Reports:**
- `bridge_backend/config/.env.sync.json` - Sync snapshot
- `bridge_backend/logs/env_sync_report.json` - Sync report
- `bridge_backend/logs/env_parity_check.json` - Parity check
- `docs/audit/GITHUB_ENV_AUDIT.md` - Auto-generated audit

**Documentation:**
- `docs/ENV_SYNC_AUTONOMOUS_PIPELINE.md` - Full guide
- `docs/GITHUB_ENV_SYNC_GUIDE.md` - GitHub-specific guide
- `docs/GENESIS_EVENT_FLOW.md` - Event bus integration

---

## 🧾 Genesis Events

| Event Topic | When Published | Subscribers |
|------------|---------------|-------------|
| `envsync.init` | Sync starts | Autonomy, Truth |
| `envsync.commit` | Parity achieved | Truth, Blueprint |
| `envsync.drift` | Drift detected | Autonomy (auto-heal) |

---

## 🔍 Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success, no drift |
| `1` | Drift detected or sync issues |

---

## 🆘 Common Issues

**"GitHub sync not configured"**
→ Set `GITHUB_TOKEN` and `GITHUB_REPO` in environment

**"Failed to fetch Render env"**
→ Verify `RENDER_API_KEY` and `RENDER_SERVICE_ID`

**Secrets not appearing in GitHub**
→ Wait 1-2 minutes, check token has `repo` + `secrets` scopes

**Drift persists after sync**
→ Check workflow logs for firewall/DNS blocks

---

## 🧪 Testing

```bash
# Dry-run mode (no actual changes)
HUBSYNC_DRYRUN=true python3 -m bridge_backend.cli.genesisctl env sync --target github --from render

# Run test suite
python3 bridge_backend/tests/test_envsync_pipeline.py
```

---

## 📚 Full Documentation

- [Autonomous Environment Sync Pipeline](./ENV_SYNC_AUTONOMOUS_PIPELINE.md)
- [GitHub Sync Guide](./GITHUB_ENV_SYNC_GUIDE.md)
- [Genesis Event Flow](./GENESIS_EVENT_FLOW.md)
- [EnvRecon Autonomy Integration](../ENVRECON_AUTONOMY_INTEGRATION.md)

---

**Last Updated:** October 11, 2025
