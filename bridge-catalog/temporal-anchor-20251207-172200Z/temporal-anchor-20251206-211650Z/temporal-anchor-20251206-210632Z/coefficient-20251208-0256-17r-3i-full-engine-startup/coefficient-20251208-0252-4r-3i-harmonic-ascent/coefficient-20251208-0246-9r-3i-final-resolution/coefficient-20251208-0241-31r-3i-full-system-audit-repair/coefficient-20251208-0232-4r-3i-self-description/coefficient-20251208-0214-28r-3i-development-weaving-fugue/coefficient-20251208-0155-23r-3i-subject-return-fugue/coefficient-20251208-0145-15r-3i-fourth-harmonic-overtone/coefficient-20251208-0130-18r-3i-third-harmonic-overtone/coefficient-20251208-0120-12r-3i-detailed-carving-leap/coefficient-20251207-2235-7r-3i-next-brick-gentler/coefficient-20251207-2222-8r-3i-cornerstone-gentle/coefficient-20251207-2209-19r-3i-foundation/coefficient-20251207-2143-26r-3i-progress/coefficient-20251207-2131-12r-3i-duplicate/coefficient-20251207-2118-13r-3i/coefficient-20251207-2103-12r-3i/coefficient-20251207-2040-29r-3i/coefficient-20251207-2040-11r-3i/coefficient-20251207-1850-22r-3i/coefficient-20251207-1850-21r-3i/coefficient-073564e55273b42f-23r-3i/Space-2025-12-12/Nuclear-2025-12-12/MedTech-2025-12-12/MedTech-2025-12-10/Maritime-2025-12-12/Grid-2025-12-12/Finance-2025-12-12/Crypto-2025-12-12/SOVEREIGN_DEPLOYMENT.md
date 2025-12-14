# Sovereign Deployment Mode

## Overview

SR-AIbridge now operates in **sovereign deployment mode** by default, eliminating hardcoded dependencies on Render.com and enabling deployment to any backend infrastructure. This document explains the changes made and how to configure your deployment.

## What Changed

### 1. Environment Variable Strategy

All hardcoded Render.com URLs have been replaced with configurable environment variables:

**Primary Variables:**
- `BACKEND_URL` - Your backend API base URL (e.g., `https://your-backend.com`)
- `BRIDGE_URL` - Alternative backend URL variable
- `BRIDGE_BASE_URL` - Used in some workflows for consistency

**Legacy Variables (Optional):**
- `RENDER_API_KEY` - Only needed if using Render.com
- `RENDER_SERVICE_ID` - Only needed if using Render.com

**Default Behavior:**
- If no environment variables are set, the system defaults to `https://bridge.sr-aibridge.com`
- This represents the sovereign infrastructure endpoint

### 2. Files Modified (33 total)

#### Network Policies (2 files)
- `network_policies/firewall_config_export.json` - Removed Render from critical domains
- `network_policies/sovereign_allowlist.yaml` - Vendor-neutral allowlist

#### GitHub Workflows (18 files)
All deployment and monitoring workflows now use environment variables:
- `deploy.yml` - Frontend deployment with configurable backend
- `healer_net.yml` - Health monitoring with fallback
- `bridge_autodeploy.yml` - Non-blocking health checks
- `self-test.yml` - Configurable test endpoints
- `endpoint-deepscan.yml` - Environment-based endpoint testing
- And 13 more triage/federation workflows

#### Python Scripts (10 files)
- `scripts/firewall_watchdog.py` - Configurable bridge URL
- `scripts/integrity_audit.py` - Vendor-neutral endpoints
- `scripts/env_sync_monitor.py` - Generic backend health
- `scripts/generate_sync_badge.py` - Configurable backend
- `scripts/check_env_parity.py` - Optional backend env check
- And 5 more deployment/diagnostic scripts

#### Firewall & Network Tools (3 files)
- `bridge_backend/tools/firewall_sovereignty/firewall_config_manager.py`
- `bridge_backend/tools/firewall_intel/analyze_firewall_findings.py`
- `bridge_backend/tools/network_diagnostics/check_copilot_access.py`

## How to Deploy

### Option 1: Sovereign Mode (Recommended)

Deploy without any legacy cloud provider:

```bash
# Set your backend URL
export BACKEND_URL="https://your-backend.example.com"

# Or use GitHub Secrets for workflows
gh secret set BACKEND_URL --body "https://your-backend.example.com"

# Deploy
git push origin main
```

**No other configuration needed!** The system will:
- Use your `BACKEND_URL` for all health checks
- Skip Render API calls gracefully
- Operate in fully sovereign mode

### Option 2: With Legacy Render Support

If you still need Render.com integration:

```bash
# Set backend URL
export BACKEND_URL="https://your-app.onrender.com"

# Optional: Set Render API credentials for advanced features
export RENDER_API_KEY="your_render_api_key"
export RENDER_SERVICE_ID="your_service_id"

# Deploy
git push origin main
```

The system will:
- Use Render API for deployment diagnostics
- Fetch environment variables via Render API
- Maintain full Render.com compatibility

### Option 3: Custom Backend Provider

Use any backend provider (AWS, GCP, Azure, self-hosted):

```bash
# GitHub Secrets
gh secret set BACKEND_URL --body "https://api.mycompany.com"
gh secret set BRIDGE_URL --body "https://bridge.mycompany.com"

# Optional: Custom API credentials
gh secret set BACKEND_API_KEY --body "your_api_key"
gh secret set BACKEND_SERVICE_ID --body "your_service_id"
```

## Migration Guide

### From Render.com to Sovereign

1. **Set Backend URL**
   ```bash
   gh secret set BACKEND_URL --body "https://bridge.sr-aibridge.com"
   ```

2. **Remove Render Secrets (Optional)**
   ```bash
   gh secret delete RENDER_API_KEY
   gh secret delete RENDER_SERVICE_ID
   ```

3. **Deploy**
   ```bash
   git push origin main
   ```

4. **Verify**
   - Check workflow logs show your `BACKEND_URL`
   - Confirm health checks use sovereign endpoint
   - Verify no Render API errors

### From Legacy Setup to Environment Variables

1. **Identify Hardcoded URLs**
   - Search your custom scripts for hardcoded URLs
   - Replace with `os.getenv("BACKEND_URL", "default")`

2. **Update Local Development**
   ```bash
   # .env.local
   BACKEND_URL=http://localhost:8000
   VITE_API_BASE=http://localhost:8000/api
   ```

3. **Update Production**
   ```bash
   # Netlify
   netlify env:set BACKEND_URL https://bridge.sr-aibridge.com

   # GitHub
   gh secret set BACKEND_URL --body "https://bridge.sr-aibridge.com"
   ```

## Backward Compatibility

All changes maintain full backward compatibility:

✅ **Render.com Still Works**
- Set `RENDER_API_KEY` and `RENDER_SERVICE_ID` to enable Render features
- EnvSync provider automatically detects Render credentials
- Deploy diagnostics fetch Render logs when configured

✅ **Legacy Workflows**
- Old environment variables still respected
- Fallback chain: `BACKEND_URL` → `BRIDGE_URL` → sovereign default
- No breaking changes to existing deployments

✅ **Gradual Migration**
- Can run both sovereign and Render modes simultaneously
- Test sovereign mode before removing Render
- Rollback by restoring Render secrets

## Verification

### Check Your Configuration

```bash
# List current secrets
gh secret list

# Expected for sovereign mode:
# - BACKEND_URL (or uses default)
# - NETLIFY_AUTH_TOKEN
# - FORGE_DOMINION_ROOT

# Not required:
# - RENDER_API_KEY ✗
# - RENDER_SERVICE_ID ✗
```

### Test Deployment

```bash
# Trigger deploy workflow
gh workflow run deploy.yml

# Monitor logs
gh run watch

# Look for:
# ✅ Backend URL: https://bridge.sr-aibridge.com (or your custom URL)
# ✅ Health checks passing
# ✅ No Render API errors
```

### Verify Health Checks

```bash
# Test backend health
curl https://bridge.sr-aibridge.com/api/health

# Test frontend
curl https://sr-aibridge.netlify.app/.netlify/functions/health

# Check sync status
curl https://sr-aibridge.netlify.app/bridge_sync_badge.json
```

## Benefits

### 🎯 Vendor Independence
- No lock-in to Render.com or any specific provider
- Deploy to any infrastructure
- Maintain control of your runtime

### 🔒 Security
- No hardcoded credentials
- Environment-based configuration
- Secrets managed via GitHub/Netlify

### 💰 Cost Optimization
- Choose the most cost-effective provider
- Avoid vendor-specific pricing
- Self-host if desired

### 🚀 Flexibility
- Switch providers without code changes
- Multi-cloud deployments
- Hybrid cloud/on-prem setups

## Troubleshooting

### Health Checks Failing

**Problem:** Workflows show backend health check failures

**Solution:**
```bash
# Check your BACKEND_URL is set correctly
gh secret list | grep BACKEND

# Update if needed
gh secret set BACKEND_URL --body "https://your-correct-url.com"

# Verify endpoint is accessible
curl https://your-backend.com/api/health
```

### Environment Variables Not Working

**Problem:** Workflows still using old Render URLs

**Solution:**
```bash
# Clear browser/workflow cache
gh workflow disable deploy.yml
gh workflow enable deploy.yml

# Force new run
gh workflow run deploy.yml
```

### Render Features Not Working

**Problem:** Need Render API integration but it's not working

**Solution:**
```bash
# Ensure Render credentials are set
gh secret set RENDER_API_KEY --body "your_api_key"
gh secret set RENDER_SERVICE_ID --body "srv-xxxxx"

# Set backend URL to Render
gh secret set BACKEND_URL --body "https://your-app.onrender.com"
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   GitHub Actions                         │
│  (Workflows with $BACKEND_URL environment variable)     │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  Netlify (CDN)   │    │  Sovereign       │
│  - Frontend      │    │  Backend         │
│  - Functions     │◄───┤  - Configurable  │
│  - Edge          │    │  - Vendor-free   │
└──────────────────┘    └──────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
         Optional Legacy Providers
         (Render.com via API when configured)
```

## References

- [Bridge Runtime Handler (BRH)](BRH_GUIDE.md) - Sovereign runtime deployment
- [Forge Dominion](FORGE_DOMINION_DEPLOYMENT_GUIDE.md) - Ephemeral token management
- [Environment Setup](docs/ENVIRONMENT_SETUP.md) - Detailed configuration guide

## Support

For issues or questions:
1. Check GitHub Actions logs for specific errors
2. Review environment variable configuration
3. Consult workflow files for expected variable names
4. Open an issue with logs and configuration details

---

**Status:** ✅ Sovereign mode active
**Last Updated:** 2024-11-05
**Version:** 1.0.0
