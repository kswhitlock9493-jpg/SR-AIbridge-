# Safe Placeholder Mode

## Overview

Safe Placeholder Mode is a feature that allows the SR-AIbridge system to operate gracefully when external services are not yet deployed or configured. This prevents workflow failures and false alarms during development, testing, and initial setup phases.

## What is Safe Placeholder Mode?

Safe Placeholder Mode is an operational state where:

1. **External connectivity checks are skipped** - The system doesn't attempt to reach federation endpoints or backend services that may not exist yet
2. **Workflows succeed without errors** - GitHub Actions workflows complete successfully even when external services are unavailable
3. **Reports are generated** - Diagnostic scripts still produce valid output indicating they're in safe mode
4. **No false failure alerts** - Users don't receive error emails for expected unavailability

## Important Distinction

**Safe Placeholder Mode** (script/workflow behavior) is different from **ENGINE_SAFE_MODE**:

- `ENGINE_SAFE_MODE=true` - A **security feature** that should always be enabled in production. It enforces RBAC, truth certification, and safe engine operations.
- `SAFE_PLACEHOLDER_MODE=true` - A **testing/development feature** that allows scripts to skip external connectivity checks when services aren't deployed yet.

## When is Safe Placeholder Mode Used?

Safe Placeholder Mode is automatically enabled in these scenarios:

1. **No Backend URL Configured** - When `BACKEND_URL` secret is not set in GitHub repository settings
2. **Development Environment** - During local development before external services are deployed
3. **Testing** - When running CI/CD tests that shouldn't depend on external services

## Affected Workflows

The following workflows respect Safe Placeholder Mode:

### 1. Federation Runtime Guard v2 (`federation_runtime_guard.yml`)

- **Smoke Backend Test** - Validates backend health endpoints
- **Triage Matrix** - Comprehensive endpoint validation
- **Behavior**: Skips external checks when `BACKEND_URL` secret is not configured

### 2. Federation Deep-Seek (`federation_deepseek.yml`)

- **Deep-Seek + Auto-Repair** - Federation endpoint validation and repair
- **Behavior**: Skips federation endpoint checks when `BACKEND_URL` secret is not configured

## Configuration

### Enabling Safe Placeholder Mode

Safe Placeholder Mode is controlled by the `SAFE_PLACEHOLDER_MODE` environment variable:

```bash
# Enable safe placeholder mode
export SAFE_PLACEHOLDER_MODE=true

# Disable safe placeholder mode (production)
export SAFE_PLACEHOLDER_MODE=false
```

### Workflow Configuration

In GitHub Actions workflows, safe placeholder mode is automatically enabled based on secret availability:

```yaml
env:
  # Enable safe placeholder mode when no backend URL is configured
  SAFE_PLACEHOLDER_MODE: ${{ secrets.BACKEND_URL != '' && 'false' || 'true' }}
```

This means:
- If `BACKEND_URL` secret exists → Safe mode **disabled**, full production checks run
- If `BACKEND_URL` secret missing → Safe mode **enabled**, external checks skipped

## Script Behavior in Safe Placeholder Mode

### 1. Deep Seek Triage (`deep_seek_triage.py`)

**Normal Mode:**
- Probes federation endpoints
- Validates schema versions
- Performs DNS warmup
- Attempts live calls with retries
- Reports pass/fail status

**Safe Placeholder Mode:**
- Skips all external connectivity checks
- Generates report indicating safe mode active
- Exits successfully (exit code 0)

### 2. Smoke Backend (`smoke_backend.py`)

**Normal Mode:**
- Tests `/api/health` endpoint (required)
- Tests `/api/version` endpoint (optional)
- Tests `/api/routes` endpoint (optional)
- Retries with exponential backoff
- Reports pass/fail status

**Safe Placeholder Mode:**
- Skips all endpoint checks
- Generates report indicating safe mode active
- Exits successfully (exit code 0)

### 3. Triage Matrix (`triage_matrix.py`)

**Normal Mode:**
- Pings all configured endpoints
- Measures response times
- Calculates success rates
- Reports pass/fail status

**Safe Placeholder Mode:**
- Skips all endpoint pings
- Generates report indicating safe mode active
- Exits successfully (exit code 0)

## Output Examples

### Safe Placeholder Mode Output

```json
{
  "generated_at": 1762549240,
  "mode": "safe_placeholder",
  "health": {},
  "details": {},
  "message": "Safe placeholder mode active - external federation checks skipped"
}
```

### Production Mode Output

```json
{
  "generated_at": 1762549240,
  "mode": "production",
  "health": {
    "diagnostics_federation": "PASS",
    "bridge_auto_deploy": "PASS",
    "triage_federation": "PASS"
  },
  "details": {
    "diagnostics_federation": {
      "reachable": true,
      "schema_match": true,
      "latency_ms": 145.2,
      "repairs": [],
      "errors": []
    }
  }
}
```

## Exiting Safe Placeholder Mode

To transition from safe placeholder mode to full production mode:

### 1. Configure Backend URL Secret

Add the `BACKEND_URL` secret in your GitHub repository:

```
Repository → Settings → Secrets and variables → Actions → New repository secret
Name: BACKEND_URL
Value: https://your-backend-domain.com
```

### 2. Deploy Backend Services

Ensure your backend is deployed and accessible at the configured URL:

```bash
# Test backend health
curl https://your-backend-domain.com/api/health

# Should return:
# {"status":"ok","host":"production",...}
```

### 3. Deploy Federation Services

If using federation, ensure federation endpoints are configured in `bridge_backend/federation_map.json` and accessible.

### 4. Verify Workflows

Once secrets are configured and services deployed:

1. Workflows will automatically use production mode
2. Full connectivity checks will be performed
3. Failures will be reported if services are unreachable

## Troubleshooting

### Issue: Workflows failing even with BACKEND_URL configured

**Solution:** 
1. Verify the backend URL is correct and accessible
2. Check that the backend has the expected endpoints (`/api/health`, `/api/version`, etc.)
3. Ensure CORS is configured to allow GitHub Actions IPs

### Issue: Want to test production mode locally

**Solution:**
```bash
# Start local backend
cd bridge_backend
python main.py &

# Test scripts against local backend
export BRIDGE_BASE=http://localhost:8000
export SAFE_PLACEHOLDER_MODE=false
python .github/scripts/federation/smoke_backend.py
```

### Issue: Need to force safe mode even with BACKEND_URL set

**Solution:**
```bash
# Override in workflow run
SAFE_PLACEHOLDER_MODE=true python .github/scripts/deep_seek_triage.py
```

## Best Practices

1. **Development** - Use safe placeholder mode during active development
2. **Staging** - Configure BACKEND_URL pointing to staging environment
3. **Production** - Ensure all secrets are configured, safe mode will auto-disable
4. **Testing** - Use safe placeholder mode in CI tests that shouldn't depend on external services

## Related Configuration

### Environment Variables

- `SAFE_PLACEHOLDER_MODE` - Controls safe placeholder mode (default: auto-detect)
- `ENGINE_SAFE_MODE` - Security feature, should always be `true` in production
- `BACKEND_URL` - Backend service URL (GitHub secret)
- `BRIDGE_BASE` - Override for scripts (defaults to BACKEND_URL)

### Files

- `.github/scripts/deep_seek_triage.py` - Federation endpoint validation
- `.github/scripts/federation/smoke_backend.py` - Backend health checks
- `.github/scripts/federation/triage_matrix.py` - Endpoint matrix validation
- `bridge_backend/federation_map.json` - Federation endpoint configuration

## Security Note

Safe Placeholder Mode is designed for **development and testing only**. In production:

1. Always configure `BACKEND_URL` secret
2. Ensure `ENGINE_SAFE_MODE=true` for security
3. Monitor workflow results for real failures
4. Safe placeholder mode will auto-disable when secrets are configured

---

**Last Updated:** 2025-11-07
**Version:** 1.0.0
