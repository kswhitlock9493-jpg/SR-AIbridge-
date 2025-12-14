# Runtime Troubleshooting Guide

This guide helps diagnose and fix runtime issues with the SR-AIbridge backend on Render.

## Quick Diagnostics

### Check Runtime Health

```bash
# Run the federation runtime guard locally
python .github/scripts/federation/smoke_backend.py --base https://sr-aibridge.onrender.com

# Run full triage
python .github/scripts/federation/triage_matrix.py --base https://sr-aibridge.onrender.com
```

### Collect Render Diagnostics

```bash
# Set your Render credentials
export RENDER_API_TOKEN="your-token"
export RENDER_SERVICE_ID="your-service-id"

# Collect diagnostics
python .github/scripts/render_collect.py
```

## Common Issues

### 1. Health Check Failing

**Symptoms:**
- `/api/health` returns 5xx or times out
- Render shows service as unhealthy

**Solutions:**

1. Check if database is ready:
   ```bash
   # View Render logs
   # Look for "[wait_for_db] DB not ready" messages
   ```

2. Verify environment variables:
   ```bash
   python .github/scripts/render_env_lint.py
   ```

3. Check start script runs locally:
   ```bash
   PORT=10000 ENVIRONMENT=production bash bridge_backend/runtime/start.sh
   ```

### 2. Database Connection Issues

**Symptoms:**
- "[wait_for_db] DB not ready" in logs
- Timeout after 120s

**Solutions:**

1. Verify DATABASE_URL is set correctly in Render dashboard
2. Check database is running and accessible
3. Verify database credentials are correct

### 3. Egress/Network Issues

**Symptoms:**
- "[egress_canary] Egress blocked to: ..." in logs
- External API calls fail

**Solutions:**

1. Check network connectivity:
   ```bash
   python bridge_backend/runtime/egress_canary.py
   ```

2. Verify Render region and firewall rules
3. Check if specific hosts are blocked

### 4. Version Mismatch

**Symptoms:**
- `/api/version` shows wrong commit
- Stale code deployed

**Solutions:**

1. Verify Render is deploying the correct branch
2. Check RENDER_GIT_COMMIT environment variable
3. Force a new deployment

## Runtime Scripts

### start.sh

Main entry point for Render deployment. Runs:

1. `wait_for_db.py` - Wait for database readiness
2. `run_migrations.py` - Check migrations (safe mode)
3. `egress_canary.py` - Verify network connectivity
4. `health_probe.py` - Warm up health endpoints
5. Launch uvicorn

### wait_for_db.py

Waits for PostgreSQL to be ready before starting the app.

**Usage:**
```bash
python bridge_backend/runtime/wait_for_db.py --timeout 120
```

**Exit codes:**
- 0: Success (DB ready or SQLite)
- 1: Timeout
- 2: DATABASE_URL missing (for PostgreSQL)

### run_migrations.py

Safely checks database connectivity before startup.

**Usage:**
```bash
python bridge_backend/runtime/run_migrations.py --safe
```

**Exit codes:**
- 0: Success
- 1: Migration check failed

### egress_canary.py

Verifies outbound connectivity to critical hosts.

**Usage:**
```bash
python bridge_backend/runtime/egress_canary.py --timeout 6
```

**Exit codes:**
- 0: All hosts reachable
- 1: One or more hosts blocked

### health_probe.py

Prepares health endpoint warmup.

**Usage:**
```bash
python bridge_backend/runtime/health_probe.py --warm
```

## Manual Triage

### Run Full Diagnostics

```bash
# From GitHub Actions
gh workflow run "Federation Runtime Guard"

# Or manually
python .github/scripts/federation/smoke_backend.py --base https://sr-aibridge.onrender.com
python .github/scripts/federation/triage_matrix.py --base https://sr-aibridge.onrender.com
```

### Check Specific Endpoints

```bash
curl https://sr-aibridge.onrender.com/api/health
curl https://sr-aibridge.onrender.com/api/version
curl https://sr-aibridge.onrender.com/api/routes
```

## Environment Variables

Required variables in Render:

- `PORT` - Port to listen on (default: 10000)
- `PYTHON_VERSION` - Python version (3.11.9)
- `ENVIRONMENT` - Environment name (production)
- `DATABASE_URL` - PostgreSQL connection string
- `BRIDGE_API_URL` - Public backend URL
- `SECRET_KEY` - Application secret key
- `LOG_LEVEL` - Logging level (info)

## Workflow Integration

### Federation Runtime Guard

Runs every 6 hours and on push to main. Tests:

- Backend health endpoints
- Version information
- Route availability
- Comprehensive triage matrix

On failure, automatically collects Render diagnostics.

### Render Env Guard

Runs on PR and push. Validates:

- render.yaml configuration
- Start script existence
- Runtime script availability
- Environment variable presence

## Debugging Tips

1. **Enable verbose logging:**
   Set `LOG_LEVEL=debug` in Render

2. **Check recent deployments:**
   View deployment logs in Render dashboard

3. **Test locally:**
   Run start.sh locally to reproduce issues

4. **Review artifacts:**
   Download workflow artifacts for detailed reports

## Getting Help

If issues persist:

1. Run diagnostic collector
2. Download workflow artifacts
3. Review runtime logs in Render
4. Check GitHub workflow run logs
5. Verify all environment variables are set correctly

## Related Documentation

- [Total Stack Triage](./TOTAL_STACK_TRIAGE.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [README](../README.md)
