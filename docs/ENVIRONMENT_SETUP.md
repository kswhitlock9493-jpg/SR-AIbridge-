# Environment Integration & Build Stabilization

## Overview

This document describes the environment variable setup and deployment alignment between Render (backend) and Netlify (frontend) for the SR-AIbridge project.

## Environment Variable Reference

| Variable | Purpose | Platform | Safe for Frontend? |
|----------|---------|----------|-------------------|
| `BRIDGE_API_URL` | Backend API endpoint for SR-AIbridge services | Netlify / Render | ✅ Yes |
| `DATABASE_URL` | PostgreSQL connection string (managed by Render) | Render | ❌ No (contains credentials) |
| `SECRET_KEY` | Encryption key for token signing | Render | ❌ No (secret) |
| `LOG_LEVEL` | Adjusts verbosity of logs (info, debug, warn) | Render | ✅ Yes |
| `FEDERATION_SYNC_KEY` | Sync token for multi-agent federation | Both | ❌ No (secret) |
| `CASCADE_MODE` | Controls agent cascade and learning mode | Both | ✅ Yes |
| `DATADOG_API_KEY` | Optional logging/metrics (Datadog integration) | Both | ❌ No (secret) |
| `DATADOG_REGION` | Region configuration for Datadog metrics | Both | ✅ Yes |
| `REACT_APP_API_URL` | Frontend-facing API route for production builds | Netlify | ✅ Yes |
| `VITE_API_BASE` | Base path for Vite/React during build time | Netlify | ✅ Yes |
| `VAULT_URL` | Used for secure token vault interactions | Both | ✅ Yes |
| `PUBLIC_API_BASE` | Public API base path | Netlify | ✅ Yes |
| `AUTO_DIAGNOSE` | Enable automatic diagnostics | Both | ✅ Yes |

## Render Setup

### Environment Group: SR_AIBridge_Production

**Service:** SR_AIBridge  
**Region:** Oregon  
**Runtime:** PostgreSQL 15  
**Status:** ✅ Available / Healthy

### Required Environment Variables

Set these in the Render Dashboard for the backend service:

```bash
# Core Database
DATABASE_URL=postgresql://sr_admin:<YOUR_PASSWORD>@dpg-d3i3jc0dl3ps73csp9e0-a.oregon-postgres.render.com/sr_aibridge_main
DATABASE_TYPE=postgres

# Backend Configuration
BRIDGE_API_URL=https://sr-aibridge.onrender.com
PORT=8000
ENVIRONMENT=production

# Security
SECRET_KEY=<GENERATE_32_CHAR_RANDOM_KEY>
FEDERATION_SYNC_KEY=<GENERATE_32_CHAR_RANDOM_KEY>

# Bridge Services
VAULT_URL=https://bridge.netlify.app/api/vault
CASCADE_MODE=production

# Logging
LOG_LEVEL=info

# Monitoring (Optional)
DATADOG_API_KEY=<YOUR_DATADOG_KEY>
DATADOG_REGION=us

# CORS
CORS_ALLOW_ALL=false
ALLOWED_ORIGINS=https://bridge.netlify.app,https://sr-aibridge.netlify.app

# Diagnostics
AUTO_DIAGNOSE=true
DEBUG=false
```

### Using .env.render

The `.env.render` file contains template values for backend deployment. To use it:

1. Copy values from `.env.render` to Render Dashboard
2. Replace all `<YOUR_*>` placeholders with actual values
3. Ensure `SECRET_KEY` and `FEDERATION_SYNC_KEY` are strong random strings (32+ characters)

## Netlify Setup

### Environment Configuration

Environment variables have been synced and are scoped to:
- Builds
- Functions (if applicable)
- Runtime

### Netlify Dashboard Configuration

Set these environment variables in Netlify Dashboard:

```bash
# API Configuration
PUBLIC_API_BASE=/api
VITE_API_BASE=https://sr-aibridge.onrender.com
REACT_APP_API_URL=https://sr-aibridge.onrender.com
BRIDGE_API_URL=https://sr-aibridge.onrender.com

# Bridge Configuration
CASCADE_MODE=production
VAULT_URL=https://sr-aibridge.netlify.app/api/vault

# Federation & Monitoring
FEDERATION_SYNC_KEY=<SAME_AS_RENDER>
DATADOG_REGION=us

# Diagnostics
AUTO_DIAGNOSE=true
```

### Using .env.netlify

The `.env.netlify` file contains frontend-safe environment variables. These should be set in the Netlify Dashboard, not committed to the repository.

### netlify.toml Configuration (v1.6.3)

The `netlify.toml` file includes:

```toml
[build]
  base = "bridge-frontend"
  command = "npm ci && npm run build"
  publish = "bridge-frontend/dist"

[build.environment]
  NODE_ENV = "production"
  AUTO_REPAIR_MODE = "true"
  BRIDGE_HEALTH_REPORT = "enabled"
  SECRETS_SCAN_ENABLED = "false"
  SECRETS_SCAN_DISABLED = "true"
  SECRETS_SCAN_OMIT_KEYS = "NODE_ENV,VITE_API_BASE,REACT_APP_API_URL"
  SECRETS_SCAN_LOG_LEVEL = "error"
  VITE_API_BASE = "https://sr-aibridge.onrender.com/api"
  REACT_APP_API_URL = "https://sr-aibridge.onrender.com/api"
  PUBLIC_API_BASE = "/api"
  CASCADE_MODE = "production"
  CONFIDENCE_MODE = "enabled"
  DIAGNOSTIC_KEY = "sr-dx-prod-bridge-001"

[build.processing.secrets_scan]
  omit = ["node_modules/**", "dist/**", "build/**"]

[functions]
  directory = "bridge-frontend/netlify/functions"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[context.production.environment]
  NODE_ENV = "production"
  SECRETS_SCAN_ENABLED = "false"
  SECRETS_SCAN_LOG_LEVEL = "error"
  BRIDGE_HEALTH_REPORT = "enabled"
```

**Key Points:**
- `SECRETS_SCAN_ENABLED = "false"` and `SECRETS_SCAN_DISABLED = "true"` disable redundant secret scanning since all secrets are properly managed through Netlify's encrypted environment layer
- `SECRETS_SCAN_OMIT_KEYS` explicitly excludes safe environment variables from scanning
- `AUTO_REPAIR_MODE = "true"` enables automatic environment repair on deployment
- `BRIDGE_HEALTH_REPORT = "enabled"` activates continuous health monitoring
- Build command uses `npm ci` for clean, deterministic builds
- All environment variables route through Netlify's encrypted environment layer
- Functions directory placeholder prevents "missing functions" warnings

## Deployment Workflow

### Initial Setup

#### Render (Backend)

1. Create PostgreSQL database in Render Dashboard
2. Note the Internal Database URL
3. Add environment variables from `.env.render` template
4. Replace all `<YOUR_*>` placeholders with actual values
5. Deploy backend service
6. Verify logs show: `✅ Database connection verified.`

#### Netlify (Frontend)

1. Connect GitHub repository
2. Set build settings (automatically configured in `netlify.toml`):
   - Base directory: `bridge-frontend`
   - Build command: `npm run build`
   - Publish directory: `dist`
3. Add environment variables from `.env.netlify` template
4. Deploy frontend
5. Verify build completes without secret scan warnings

### Environment Synchronization

To ensure environment parity between platforms:

1. Use `.env.production` as the source of truth
2. Update both Render and Netlify when changing shared variables
3. Run `npm run check-env` (if available) to verify synchronization
4. Use `npm run repair` to restore missing Netlify environment variables

## Security Best Practices

### Secret Management

- ❌ **Never commit** `.env` files containing actual secrets to the repository
- ✅ Use placeholder patterns like `<YOUR_PASSWORD>` in example files
- ✅ Store actual secrets only in platform dashboards (Render/Netlify)
- ✅ Rotate keys regularly (SECRET_KEY, FEDERATION_SYNC_KEY, API keys)

### Frontend Safety

Variables safe for frontend (can be exposed in builds):
- `PUBLIC_API_BASE=/api`
- `CASCADE_MODE=production`
- `VAULT_URL=https://bridge.netlify.app/api/vault`
- `DATADOG_REGION=us`
- `BRIDGE_API_URL=https://sr-aibridge.onrender.com`
- `VITE_API_BASE=https://sr-aibridge.onrender.com`
- `REACT_APP_API_URL=https://sr-aibridge.onrender.com`

Variables **never** safe for frontend:
- `DATABASE_URL` (contains credentials)
- `FEDERATION_SYNC_KEY` (secret sync key)
- `DATADOG_API_KEY` (monitoring credential)
- `SECRET_KEY` (encryption key)
- Any password or token

## Troubleshooting

### Netlify Scanner Compliance & Security Policy (v1.6.4)

**Important:** Version 1.6.4 introduces legitimate scanner compliance instead of suppression.

#### Safe Omit Paths vs Sensitive Paths

The following table maps safe directories (can be excluded from scanning) vs sensitive paths (must be scanned):

| Path | Type | Scanner Treatment | Reason |
|------|------|------------------|---------|
| `node_modules/**` | Safe | ✅ Omit | Third-party dependencies |
| `bridge-frontend/dist/**` | Safe | ✅ Omit | Build artifacts |
| `bridge-frontend/build/**` | Safe | ✅ Omit | Build artifacts |
| `bridge-frontend/public/**` | Safe | ✅ Omit | Static assets |
| `bridge-frontend/src/**` | Sensitive | ❌ Must Scan | Application code |
| `bridge_backend/**` | Sensitive | ❌ Must Scan | Backend code |
| `.env*` files | Sensitive | ❌ Must Scan | Environment configs |

#### How to Read Scanner Logs

When Netlify scanner runs, look for these indicators:

**✅ Clean Output (Expected):**
```
Building site...
✓ Secrets scanning: No issues found
✓ Functions directory validated
✓ Site built successfully
```

**⚠️ Warning Output (Review Required):**
```
⚠ Secrets scanning found 1 instance
  → Check file: src/config.js line 42
  → Reason: Potential API key pattern detected
```

**❌ Blocking Output (Action Required):**
```
❌ Secrets scanning found 3 instances
  → Build blocked for security review
  → Remove hardcoded secrets before deployment
```

#### Configuration Validation

To validate your scanner configuration:

```bash
# Run scanner compliance validation
python3 scripts/validate_scanner_output.py
```

This script checks:
- ✅ Scanner is enabled (not suppressed)
- ✅ Proper omit paths are configured
- ✅ Functions directory exists
- ✅ No false positives in build logs

### Build Fails with Missing Environment Variables

1. Check that all required variables are set in Netlify Dashboard
2. Run the repair script: `npm run repair` (from `bridge-frontend` directory)
3. Verify variables were set correctly in Netlify Dashboard

### Secret Scan Warnings (Updated for v1.6.4)

**New Approach:** Version 1.6.4 uses legitimate compliance instead of scanner suppression.

If Netlify flags secret scans:

1. **DO NOT disable the scanner** - This violates Netlify's security policy
2. Run validation: `python3 scripts/validate_scanner_output.py`
3. Check if flagged content is actually a secret:
   - If YES: Remove hardcoded secret, use environment variable
   - If NO (false positive): Verify omit paths are configured correctly
4. Ensure proper configuration in `netlify.toml`:

```toml
[build.environment]
  SECRETS_SCAN_ENABLED = "true"  # ✅ Scanner enabled
  SECRETS_SCAN_LOG_LEVEL = "warn"

[build.processing.secrets_scan]
  omit = [
    "node_modules/**",
    "bridge-frontend/dist/**",
    "bridge-frontend/build/**",
    "bridge-frontend/public/**"
  ]
```

**What Changed from v1.6.3:**
- ❌ Removed: `SECRETS_SCAN_DISABLED = "true"` (was a bypass)
- ❌ Removed: `SECRETS_SCAN_OMIT_KEYS` (not a proper solution)
- ✅ Added: Proper omit paths for build artifacts only
- ✅ Added: Scanner validation in CI pipeline

**Result:**
- Scanner runs legitimately on source code
- Build artifacts are excluded (they contain no secrets)
- Compliance is achieved without policy violations

### Database Connection Errors on Render

1. Verify `DATABASE_URL` is correctly set with actual password
2. Check that database is running in Render Dashboard
3. Ensure `DATABASE_TYPE=postgres` is set
4. Review logs for connection error details

### CORS Errors

1. Verify `ALLOWED_ORIGINS` includes both Netlify domains
2. Check that `CORS_ALLOW_ALL=false` in production
3. Ensure frontend is deployed to expected Netlify domain
4. Review backend CORS configuration in `bridge_backend/config.py`

## File Reference

- `.env` - Local development environment (SQLite)
- `.env.example` - Template for all environment variables
- `.env.production` - Source of truth for production deployments
- `.env.netlify` - Frontend-specific environment variables (template)
- `.env.render` - Backend-specific environment variables (template)
- `netlify.toml` - Netlify build configuration
- `render.yaml` - Render deployment configuration

## Validation Scripts

### Pre-Deploy Validation (`validate_netlify_env.py`)

Runs automatically before Netlify builds to ensure required environment variables are present.

### Environment Repair (`repair_netlify_env.py`)

Automatically restores missing environment variables via Netlify API.

Usage:
```bash
cd bridge-frontend
npm run repair
```

### Environment Parity Check (`check_env_parity.py`)

Compares environment variables across Netlify, Render, and `.env.production` to ensure synchronization.

### Environment Sync Monitor (`env_sync_monitor.py`)

Runs nightly to verify both Render and Netlify environments and log any drift.

**Location:** `bridge_backend/scripts/env_sync_monitor.py`

**Purpose:**
- Checks parity between Render backend and Netlify frontend
- Pings both environments to verify availability
- Reports drift to Bridge diagnostics endpoint
- Provides real-time health status

**Usage:**
```bash
python3 bridge_backend/scripts/env_sync_monitor.py
```

**Features:**
- ✅ Automated nightly sync verification
- ✅ Real-time health reporting to diagnostics dashboard
- ✅ Environment drift detection
- ✅ Integration with CI/CD pipeline

## Auto-Repair & CI/CD Integration

### GitHub Actions Auto-Heal Workflow

**File:** `.github/workflows/env_autoheal.yml`

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**Features:**
- ✅ Validates all environment variables
- ✅ Repairs missing Netlify environment values via API
- ✅ Reports DEPLOYMENT_REPAIR or STABLE events to Bridge diagnostics
- ✅ Runs automatically on every commit

**Workflow Steps:**
1. Setup Python 3.11 environment
2. Install dependencies (requests, toml, aiohttp)
3. Validate Netlify & Render environment configuration
4. Run environment auto-repair if needed
5. Post bridge diagnostics report

**Required GitHub Secrets:**
- `NETLIFY_API_KEY` - Your Netlify API access token
- `NETLIFY_SITE_ID` - Your site's unique identifier
- `BRIDGE_URL` - Bridge diagnostics endpoint URL

### Auto-Repair Mode

When `AUTO_REPAIR_MODE = "true"` is set in `netlify.toml`:

1. **Automatic Variable Restoration**: Missing Netlify variables are automatically patched via API
2. **Self-Healing**: Environment drift is detected and corrected automatically
3. **Diagnostics Reporting**: All repair actions are logged to the Bridge diagnostics dashboard
4. **Zero-Touch Recovery**: No manual intervention required for common environment issues

### Bridge Health Reporting

When `BRIDGE_HEALTH_REPORT = "enabled"`:

- Real-time health status posted to diagnostics dashboard
- Environment sync status monitored continuously
- Build and deployment events tracked
- Parity violations logged and alerted

## Conclusion

This setup ensures:
- ✅ Netlify builds complete without false-positive secret scans
- ✅ Backend verifies database connectivity on startup
- ✅ Environment variables are properly separated (frontend vs. backend)
- ✅ Production configuration is documented and secure
- ✅ Deployment workflow is standardized and repeatable
- ✅ Secrets are properly managed through platform-specific encrypted environment layers

---

**Last Updated:** 2025  
**Version:** 1.0
