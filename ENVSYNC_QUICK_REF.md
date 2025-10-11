# EnvSync Seed Manifest - Quick Reference

## 🎯 What Is This?

The **EnvSync Seed Manifest** (Genesis v2.0.1a) is a single file that defines all environment variables shared between Render (backend) and Netlify (frontend). Changes to this file automatically propagate to both platforms.

## 📁 Location

```
bridge_backend/.genesis/envsync_seed_manifest.env
```

## 🚀 Quick Start

### 1. Enable EnvSync (in platform dashboards)

**Render & Netlify Environment Variables:**
```bash
ENVSYNC_ENABLED=true
ENVSYNC_CANONICAL_SOURCE=file
ENVSYNC_MODE=enforce
ENVSYNC_SCHEDULE=@hourly
```

### 2. Set Platform Credentials

**Render:**
```bash
RENDER_API_TOKEN=<your-render-api-token>
RENDER_SERVICE_ID=<your-service-id>
```

**Netlify:**
```bash
NETLIFY_API_TOKEN=<your-netlify-token>
NETLIFY_SITE_ID=<your-site-id>
```

### 3. Deploy and Verify

```bash
# Check EnvSync status
curl https://sr-aibridge.onrender.com/envsync/health

# Trigger manual sync
curl -X POST https://sr-aibridge.onrender.com/envsync/apply-all
```

## 📝 How It Works

```
┌─────────────────────────────────────┐
│  EnvSync Seed Manifest              │
│  (Single Source of Truth)           │
│  bridge_backend/.genesis/           │
│    envsync_seed_manifest.env        │
└────────────┬────────────────────────┘
             │
             ├──> Genesis Orchestration
             │      │
             │      ├──> Drift Detection
             │      └──> Auto-Correction
             │
    ┌────────┴─────────┐
    ▼                  ▼
┌────────┐      ┌──────────┐
│ Render │      │ Netlify  │
│ Backend│◄────►│ Frontend │
└────────┘      └──────────┘
  Synced          Synced
```

## 🔧 Common Tasks

### Add a New Variable

1. Edit `bridge_backend/.genesis/envsync_seed_manifest.env`
2. Add your variable:
   ```bash
   # My new feature
   MY_NEW_VAR=value
   ```
3. Validate:
   ```bash
   python3 scripts/validate_envsync_manifest.py
   ```
4. Commit and deploy

### Preview Changes Before Applying

```bash
# See what would change on Render
curl -X POST https://sr-aibridge.onrender.com/envsync/dry-run/render

# See what would change on Netlify
curl -X POST https://sr-aibridge.onrender.com/envsync/dry-run/netlify
```

### Manual Sync

```bash
# Sync to both platforms
curl -X POST https://sr-aibridge.onrender.com/envsync/apply-all

# Sync to one platform only
curl -X POST https://sr-aibridge.onrender.com/envsync/apply/render
curl -X POST https://sr-aibridge.onrender.com/envsync/apply/netlify
```

### Check Sync Status

Genesis bus events will show:
- `envsync.drift` - Drift detected between manifest and platform
- `envsync.complete` - Sync completed successfully
- `deploy.platform.sync` - Platform synchronization propagated

## 🛡️ Security Notes

⚠️ **DO NOT** put secrets in the manifest:
- ❌ API keys
- ❌ Passwords
- ❌ Database URLs with credentials
- ❌ Secret tokens

✅ **DO** put configuration in the manifest:
- ✅ Feature flags (e.g., `BLUEPRINTS_ENABLED=true`)
- ✅ Timeouts and intervals
- ✅ Public endpoints
- ✅ Pool sizes and limits

## 📊 Variables Currently in Manifest

| Category | Variables | Count |
|----------|-----------|-------|
| Engine Controls | `LINK_ENGINES`, `BLUEPRINTS_ENABLED` | 2 |
| Database Config | `DB_*` variables | 6 |
| Health Checks | `HEALTH_*` variables | 4 |
| Federation | `FEDERATION_*` variables | 3 |
| Watchdog | `WATCHDOG_*` variables | 2 |
| Genesis | `GENESIS_*` variables | 3 |
| Runtime | `HOST`, `PREDICTIVE_STABILIZER_ENABLED` | 2 |
| **Total** | | **22** |

## 🔍 Validation

Before deploying changes, always validate:

```bash
python3 scripts/validate_envsync_manifest.py
```

Checks:
- ✅ File format
- ✅ Metadata headers
- ✅ Variable syntax
- ✅ Value types
- ✅ Security issues

## 📚 Full Documentation

- [Complete EnvSync Seed Manifest Guide](docs/ENVSYNC_SEED_MANIFEST.md)
- [EnvSync Engine Documentation](docs/ENVSYNC_ENGINE.md)
- [Environment Setup Guide](docs/ENVIRONMENT_SETUP.md)
- [Genesis v2 Architecture](GENESIS_V2_GUIDE.md)

## 🐛 Troubleshooting

### "Manifest not found"
```bash
# Check file exists
ls -la bridge_backend/.genesis/envsync_seed_manifest.env

# Verify ENVSYNC_CANONICAL_SOURCE is set to "file"
```

### "Variables not syncing"
```bash
# Check EnvSync is enabled
curl https://sr-aibridge.onrender.com/envsync/health

# Check logs for errors
# Look for "EnvSync" in application logs
```

### "Drift keeps appearing"
If drift is detected after you manually changed a platform variable:
1. Either update the manifest to match
2. Or let the next sync restore the manifest value

## 🎓 Examples

### Example 1: Enable a new feature

```bash
# 1. Edit manifest
echo "NEW_FEATURE_ENABLED=true" >> bridge_backend/.genesis/envsync_seed_manifest.env

# 2. Validate
python3 scripts/validate_envsync_manifest.py

# 3. Commit
git add bridge_backend/.genesis/envsync_seed_manifest.env
git commit -m "feat: enable new feature"

# 4. Deploy - sync happens automatically on next cycle
# Or trigger immediately:
curl -X POST https://sr-aibridge.onrender.com/envsync/apply-all
```

### Example 2: Adjust database pool size

```bash
# Edit manifest
# Change: DB_POOL_SIZE=10
# To:     DB_POOL_SIZE=20

# Validate and commit
python3 scripts/validate_envsync_manifest.py
git commit -am "config: increase DB pool size to 20"

# Deploy - sync on next @hourly cycle or trigger manually
```

---

**Version:** Genesis v2.0.1a  
**Last Updated:** 2025-10-11  
**Managed By:** Genesis Orchestration Layer
