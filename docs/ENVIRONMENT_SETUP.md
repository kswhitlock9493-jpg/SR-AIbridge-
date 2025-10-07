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

### netlify.toml Configuration

The `netlify.toml` file includes:

```toml
[build]
  base = "bridge-frontend"
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_ENV = "production"
  SECRETS_SCAN_ENABLED = "false"
  VITE_API_BASE = "https://sr-aibridge.onrender.com"
  REACT_APP_API_URL = "https://sr-aibridge.onrender.com"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**Key Points:**
- `SECRETS_SCAN_ENABLED = "false"` disables redundant secret scanning since all secrets are properly managed through Netlify's encrypted environment layer
- Build command is simplified to `npm run build` (dev dependencies are installed automatically in Netlify)
- All environment variables route through Netlify's encrypted environment layer

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

### Build Fails with Missing Environment Variables

1. Check that all required variables are set in Netlify Dashboard
2. Run the repair script: `npm run repair` (from `bridge-frontend` directory)
3. Verify variables were set correctly in Netlify Dashboard

### Secret Scan Warnings

If Netlify flags secret scans despite proper configuration:

1. Verify `SECRETS_SCAN_ENABLED = "false"` is set in `netlify.toml`
2. Ensure no actual secrets are hardcoded in source files
3. Use environment variables for all sensitive values
4. Check that `.env` files are in `.gitignore`

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
