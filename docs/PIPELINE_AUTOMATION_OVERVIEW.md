# SR-AIbridge Automated Deployment Pipeline

## Overview
This setup ensures stable, self-healing deployments between Netlify (frontend) and Render (backend).

### Components
- **validate_netlify_env.py** → Checks env vars before build
- **repair_netlify_env.py** → Restores missing vars via Netlify API
- **deploy_diagnose.py** → Verifies Render + Vault + Database health

### Workflow
1. Validator runs automatically before Netlify build
2. If failure → Repair script can auto-patch Netlify
3. Successful deploy triggers `deploy_diagnose.py`
4. Diagnostic summary sent to logs or webhook

### Benefits
✅ Self-healing environment  
✅ Consistent Render/Netlify sync  
✅ Reduced human intervention  
✅ Security-hardened pipeline

## Pre-Deploy Validation

The `validate_netlify_env.py` script ensures all required environment variables are present before the build starts.

### Required Environment Variables
- `PUBLIC_API_BASE` - Frontend API base path
- `VITE_API_BASE` - Vite-specific API base URL
- `REACT_APP_API_URL` - React app API URL
- `CASCADE_MODE` - Deployment mode (e.g., production)
- `VAULT_URL` - Vault service endpoint

### Usage
The validation script runs automatically as a `prebuild` hook in `package.json`:

```json
"prebuild": "python3 ../scripts/validate_netlify_env.py"
```

If validation fails, the build will stop immediately with a clear error message indicating which variables are missing.

## Auto-Repair Script

The `repair_netlify_env.py` script can automatically restore missing environment variables via the Netlify API.

### Prerequisites
The repair script requires the following credentials:
- `NETLIFY_API_KEY` - Your Netlify API access token
- `NETLIFY_SITE_ID` - Your site's unique identifier

### Usage
Run manually when needed:

```bash
npm run repair
```

Or directly:

```bash
python3 scripts/repair_netlify_env.py
```

### Default Environment Values
The script will set these defaults if variables are missing:

| Variable | Default Value |
|----------|--------------|
| PUBLIC_API_BASE | `/api` |
| VITE_API_BASE | `https://sr-aibridge.onrender.com/api` |
| REACT_APP_API_URL | `https://sr-aibridge.onrender.com/api` |
| CASCADE_MODE | `production` |
| VAULT_URL | `https://sr-aibridge.netlify.app/api/vault` |

## Post-Deploy Verification Checklist

After merging and redeploying, open the Netlify build logs and confirm these:

| Stage | Expected Log Line | Meaning |
|-------|------------------|---------|
| Pre-deploy | ✅ All required environment variables present and valid. | Validator passed |
| Build | Netlify Build completed successfully | No TOML parse errors |
| Render Diagnose | ✅ Database connection verified. | Backend healthy |
| Bridge Log | 🧩 Auto-diagnose active. Running deploy_diagnose.py | Auto-diagnose active |
| Completion | 📡 Diagnostic summary sent via webhook. | End-to-end verification complete |

## Netlify Configuration

The `netlify.toml` file is configured with:

### Build Settings
- **Base directory**: `bridge-frontend`
- **Publish directory**: `bridge-frontend/build`
- **Build command**: `npm run build`

### Security Headers
All responses include security-hardened headers:
- Content Security Policy (CSP)
- Referrer Policy
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection

### Redirects
All routes redirect to `index.html` for SPA routing (status 200).

## Troubleshooting

### Build Fails with Missing Environment Variables
1. Check that all required variables are set in Netlify dashboard
2. Run the repair script to restore defaults: `npm run repair`
3. Verify the variables were set correctly

### Validation Script Fails Locally
The validation script requires environment variables to be set. For local development, create a `.env` file or set the variables in your shell.

### Repair Script Cannot Connect to Netlify
Ensure `NETLIFY_API_KEY` and `NETLIFY_SITE_ID` are correctly set in your environment. Generate a new API token from Netlify if needed.

## Security Notes

- Never commit `.env` files containing secrets
- Keep API keys secure and rotate them regularly
- The validation script does not expose sensitive values in logs
- CSP headers restrict script execution to trusted sources only
