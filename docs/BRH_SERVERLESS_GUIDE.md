# BRH FastAPI Serverless Backend - Deployment Guide

## Overview

This guide covers the deployment of the new BRH FastAPI serverless backend that was added to the project. This is different from the existing BRH Docker-based orchestration system documented in `BRH_DEPLOYMENT_GUIDE.md`.

## What Was Implemented

### New Backend (`brh/app.py`)

A lightweight FastAPI application designed for serverless deployment with these endpoints:

- **GET `/health`** - Health check with uptime tracking and environment status
- **POST `/workflows/execute`** - Execute workflows with background task support
- **POST `/genesis/heartbeat`** - Confirm backend is alive (no placeholders)
- **POST `/triage/self-heal`** - Trigger self-healing operations

### Netlify Function Integration

- **`netlify/functions/brh.py`** - Mangum wrapper for AWS Lambda compatibility
- **`netlify/functions/brh_cron.py`** - Optional scheduled task handler
- **`netlify/functions/requirements.txt`** - Python dependencies (mangum, fastapi, pydantic)

### Frontend Integration

- **`bridge-frontend/src/api/brh.js`** - BRH API client with helper functions
- **`bridge-frontend/src/hooks/useBackendHealth.js`** - Health check utilities
- Updated `bridge-frontend/src/api.js` to export BRH functions
- Updated `bridge-frontend/.env.production` to route to BRH function

### Infrastructure Updates

- Updated `netlify.toml` with API redirects and build configuration
- Added `mangum==0.17.0` to `requirements-dev.txt`

## Deployment to Netlify

### 1. Set Environment Variables

In Netlify Dashboard → Site Settings → Environment Variables:

```
FORGE_DOMINION_ROOT=dominion://sovereign.bridge
DOMINION_SEAL=your-signature-here
```

### 2. Deploy

Push to your main branch:

```bash
git push origin main
```

Netlify will automatically:
1. Install Python dependencies from `netlify/functions/requirements.txt`
2. Build the frontend
3. Deploy BRH function to `/.netlify/functions/brh`

### 3. Verify

Test the deployed endpoints:

```bash
# Health check
curl https://YOUR-SITE.netlify.app/.netlify/functions/brh/health

# Expected: {"status":"ok","uptime_s":1.23,"mode":"serverless","env":{...}}

# Genesis heartbeat
curl -X POST https://YOUR-SITE.netlify.app/.netlify/functions/brh/genesis/heartbeat

# Expected: {"bridge":"alive","brh":"ready"}
```

## Local Development

### Run BRH Backend Locally

```bash
pip install fastapi uvicorn mangum pydantic
python -m uvicorn brh.app:app --reload --port 8000
```

### Run with Netlify CLI

```bash
npm install -g netlify-cli
netlify dev
```

Access at: `http://localhost:8888/.netlify/functions/brh/health`

## API Usage Examples

### Check Backend Health

```javascript
import { ensureLiveBackend } from './api/brh';

const isHealthy = await ensureLiveBackend();
if (isHealthy) {
  // Enable production features
} else {
  // Show offline banner
}
```

### Execute Workflow

```javascript
import { executeWorkflow } from './api/brh';

await executeWorkflow('deploy_sync', {
  source: 'netlify',
  timestamp: Date.now()
});
```

### App Initialization

```javascript
import { initializeApp } from './hooks/useBackendHealth';

const { healthy, mode, message } = await initializeApp();
```

## Testing

```bash
pip install pytest httpx
pytest brh/test_app.py -v
```

All 11 tests should pass.

## Troubleshooting

### Backend Returns 500 Error

Check Netlify function logs:
- Netlify → Functions → brh → View logs
- Common issues: missing env vars, import errors

### Frontend Can't Connect

1. Verify `VITE_API_BASE=/.netlify/functions/brh` in `.env.production`
2. Check redirects in `netlify.toml`
3. Test backend directly

## Next Steps

1. Replace mock workflow execution with real engine calls
2. Add authentication for sensitive endpoints
3. Add monitoring and rate limiting
4. Extend workflow system

## Related Documentation

- Main BRH Docker orchestration: `BRH_DEPLOYMENT_GUIDE.md`
- Netlify Functions: https://docs.netlify.com/functions/overview/
- FastAPI: https://fastapi.tiangolo.com/
- Mangum: https://mangum.io/
