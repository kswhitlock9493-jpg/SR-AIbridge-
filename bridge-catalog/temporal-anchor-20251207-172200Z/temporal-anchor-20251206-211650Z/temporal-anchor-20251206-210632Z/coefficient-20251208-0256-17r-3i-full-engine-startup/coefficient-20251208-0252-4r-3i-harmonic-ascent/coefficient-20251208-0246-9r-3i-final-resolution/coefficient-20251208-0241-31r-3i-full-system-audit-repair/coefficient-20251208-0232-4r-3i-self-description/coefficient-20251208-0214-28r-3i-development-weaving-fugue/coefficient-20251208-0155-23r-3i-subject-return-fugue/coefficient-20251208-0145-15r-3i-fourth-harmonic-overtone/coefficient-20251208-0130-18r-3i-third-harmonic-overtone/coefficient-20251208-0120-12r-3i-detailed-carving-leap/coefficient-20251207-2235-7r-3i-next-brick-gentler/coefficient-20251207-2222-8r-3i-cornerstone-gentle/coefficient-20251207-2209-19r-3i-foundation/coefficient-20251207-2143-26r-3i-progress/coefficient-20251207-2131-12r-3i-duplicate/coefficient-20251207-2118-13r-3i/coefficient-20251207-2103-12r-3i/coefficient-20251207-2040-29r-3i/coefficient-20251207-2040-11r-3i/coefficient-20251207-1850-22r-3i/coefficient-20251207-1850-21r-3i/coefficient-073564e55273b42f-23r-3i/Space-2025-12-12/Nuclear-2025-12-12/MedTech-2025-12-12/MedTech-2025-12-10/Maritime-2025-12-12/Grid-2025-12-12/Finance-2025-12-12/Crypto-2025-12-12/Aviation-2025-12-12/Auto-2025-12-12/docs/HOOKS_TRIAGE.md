# Hooks Triage System - Operation Reflex

## Overview

The Hooks Triage module continuously monitors webhook endpoints and build hooks, validates their responsiveness, measures latency, and reports health status to the Bridge diagnostics timeline. It supports HMAC signature authentication and provides comprehensive diagnostics for all configured hooks.

## Architecture

### Components

1. **Hooks Configuration** (`bridge_backend/config/hooks.json`)
   - JSON-based configuration for all hooks to monitor
   - Supports relative URLs (to BRIDGE_BASE_URL) and absolute URLs
   - Configurable HTTP methods, expected status codes, and signing secrets
   - Sample payloads with magic marker expansion (`__NOW__` → ISO timestamp)

2. **Triage Script** (`bridge_backend/scripts/hooks_triage.py`)
   - Pings each configured hook with retry logic (3 attempts, linear backoff)
   - Measures response latency in milliseconds
   - Signs payloads with HMAC-SHA256 when configured
   - Generates JSON reports with detailed results
   - Posts events to Bridge diagnostics endpoint

3. **Control API** (`bridge_backend/routes/control.py`)
   - Secure `/api/control/hooks/triage` endpoint for manual triggering
   - HMAC signature verification for authentication
   - Non-blocking background execution
   - Integrated with existing control routes

4. **GitHub Actions Workflow** (`.github/workflows/hooks-triage.yml`)
   - Runs hourly at :15 past the hour (staggered from other triage workflows)
   - Manual trigger via workflow_dispatch
   - Uploads reports as artifacts
   - Posts diagnostics to Bridge API

5. **Frontend Panel** (`bridge-frontend/src/components/HooksTriagePanel.jsx`)
   - Displays latest hooks health status
   - Color-coded status indicators (HEALTHY/DEGRADED/CRITICAL)
   - Shows individual hook results with latency metrics
   - Auto-refreshes every 60 seconds

6. **Unified Timeline Integration**
   - Hooks triage events appear in the unified health timeline
   - Merged by synchrony collector alongside endpoint, API, and CI/CD triage

## Health Status Levels

The system calculates overall health based on failed hook checks:

- **HEALTHY**: 0 failed hooks
- **DEGRADED**: 1 failed hook
- **CRITICAL**: 2+ failed hooks

## Configuration

### Hooks Configuration File

The `bridge_backend/config/hooks.json` file defines all hooks to monitor:

```json
[
  {
    "name": "Bridge Diagnostics Ingest",
    "url": "/api/diagnostics",
    "method": "POST",
    "expectStatus": 200,
    "signingSecretEnv": "BRIDGE_CONTROL_SECRET",
    "samplePayload": {
      "type": "HOOKS_TRIAGE_PING",
      "status": "probe",
      "source": "HooksTriage",
      "meta": { "timestamp": "__NOW__" }
    }
  },
  {
    "name": "GitHub Build Hook (Netlify)",
    "absoluteUrl": "https://api.netlify.com/build_hooks/YOUR_HOOK_ID",
    "method": "POST",
    "expectStatus": 200,
    "signingSecretEnv": null,
    "samplePayload": { "trigger": "triage-ping" }
  },
  {
    "name": "Bridge Status Sync",
    "url": "/api/status",
    "method": "GET",
    "expectStatus": 200
  }
]
```

#### Configuration Fields

- **name** (required): Human-readable hook name
- **url**: Relative URL path (appended to BRIDGE_BASE_URL)
- **absoluteUrl**: Full URL (use instead of `url` for external endpoints)
- **method**: HTTP method (GET, POST, etc.) - defaults to POST
- **expectStatus**: Expected HTTP status code - defaults to 200
- **signingSecretEnv**: Environment variable name containing HMAC secret (optional)
- **samplePayload**: JSON payload to send with POST requests (optional)

#### Magic Markers

- `__NOW__`: Automatically replaced with current ISO 8601 timestamp

### Environment Variables

- `BRIDGE_BASE_URL`: Base URL for relative hook URLs (default: `https://sr-aibridge.onrender.com`)
- `BRIDGE_URL`: Bridge diagnostics endpoint for notifications
- `BRIDGE_CONTROL_SECRET`: HMAC secret for control endpoint authentication and payload signing

### GitHub Secrets (Required for Workflows)

- `BACKEND_URL`: Backend base URL (optional, defaults to `https://sr-aibridge.onrender.com`)
- `BRIDGE_URL`: Bridge diagnostics endpoint
- `BRIDGE_CONTROL_SECRET`: HMAC secret for signing

## Usage

### Manual Execution

```bash
cd bridge_backend
python3 scripts/hooks_triage.py --manual
```

### View Triage Report

```bash
cat bridge_backend/hooks_triage_report.json
```

### Automated Execution

The triage runs automatically:

1. **On Backend Startup**: 5 seconds after server starts
2. **Hourly via GitHub Actions**: Every hour at :15 (e.g., 1:15, 2:15, etc.)
3. **Manual Workflow Trigger**: Via GitHub Actions UI
4. **Manual API Trigger**: Via `/api/control/hooks/triage` endpoint (HMAC authenticated)

### Frontend Integration

Add the HooksTriagePanel component to your dashboard:

```jsx
import HooksTriagePanel from './components/HooksTriagePanel';

function Dashboard() {
  return (
    <div>
      <HooksTriagePanel />
      {/* other components */}
    </div>
  );
}
```

## Integration with Diagnostics Timeline

Hooks triage events appear in the Bridge Diagnostics Timeline with:

- **Type**: `HOOKS_TRIAGE`
- **Icon**: 🪝
- **Status**: HEALTHY/DEGRADED/CRITICAL
- **Timestamp** and individual hook results with latency metrics

## HMAC Signature Authentication

### How It Works

1. The triage script reads the `signingSecretEnv` field from hook configuration
2. If a secret is found in the environment, the payload is signed with HMAC-SHA256
3. The signature is sent in the `X-Bridge-Signature` header
4. The receiving endpoint can verify the signature to ensure authenticity

### Example: Verifying Signatures in Python

```python
import hmac
import hashlib

def verify_signature(request_body: str, signature: str, secret: str) -> bool:
    computed = hmac.new(secret.encode(), request_body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature)
```

## Retry Logic

- Each hook is attempted up to **3 times**
- Linear backoff between attempts: 1 second, then 2 seconds
- Latency is measured from first attempt to final response
- All retries are included in the total latency measurement

## Troubleshooting

### Triage Not Running on Startup

Check backend logs for:
```
🪝 Running Hooks triage...
```

If missing, verify:
- Script exists at `bridge_backend/scripts/hooks_triage.py`
- Configuration exists at `bridge_backend/config/hooks.json`
- Python `requests` library is installed

### Workflow Failures

1. Check workflow logs in GitHub Actions
2. Verify `BRIDGE_URL` secret is set
3. Confirm backend is accessible from GitHub Actions runners
4. Verify hooks configuration is valid JSON

### Frontend Panel Not Showing Data

1. Verify `/api/diagnostics/timeline` endpoint is working
2. Check browser console for fetch errors
3. Confirm hooks triage has run at least once
4. Check unified timeline contains HOOKS_TRIAGE events

### Hook Always Failing

1. Check if the endpoint URL is correct
2. Verify expected status code matches actual response
3. For signed hooks, ensure the secret is correctly configured
4. Check hook endpoint logs for authentication/validation errors

## Security Considerations

### HMAC Signing

- Secrets are read from environment variables only (never hardcoded)
- HMAC-SHA256 provides strong cryptographic authentication
- Timing-safe comparison prevents timing attacks
- Signatures should be verified on receiving endpoints

### Control Endpoint

- `/api/control/hooks/triage` requires valid HMAC signature
- Uses same `BRIDGE_CONTROL_SECRET` as other control endpoints
- Non-blocking execution prevents DoS attacks

### Configuration Security

- Hook configuration file should not contain secrets
- Use `signingSecretEnv` to reference environment variables
- External hook URLs should use HTTPS

## Future Enhancements

Potential improvements for future iterations:

- [ ] Configurable retry count and backoff strategy
- [ ] Support for custom headers per hook
- [ ] Webhook payload validation (schema checking)
- [ ] Historical latency tracking and trending
- [ ] Alert thresholds for latency spikes
- [ ] Support for OAuth/Bearer token authentication
- [ ] Parallel hook execution for faster triage
- [ ] Custom success/failure conditions beyond status codes

## Event Flow

```
1. Startup Triage
   Backend Starts → (5 sec delay) → hooks_triage.py
        ↓
   Load config → Ping each hook → Measure latency
        ↓
   Generate Report → hooks_triage_report.json
        ↓
   POST to /api/diagnostics → Bridge stores event
        ↓
   Frontend polls /api/diagnostics/timeline
        ↓
   HooksTriagePanel displays status

2. Scheduled Triage (Hourly)
   GitHub Actions Cron (15 min past) → Run hooks_triage.py
        ↓
   Ping hooks → Generate Report
        ↓
   Upload Artifact + POST to Bridge
        ↓
   Frontend updates automatically

3. Manual Triage (API)
   POST /api/control/hooks/triage (with HMAC signature)
        ↓
   Verify signature → Run hooks_triage.py in background
        ↓
   Same flow as above

4. Manual Triage (CLI)
   User runs: python3 scripts/hooks_triage.py --manual
        ↓
   Same flow as above
```

## Files Created/Modified

### Created Files
- `bridge_backend/config/hooks.json` - Hook configuration
- `bridge_backend/scripts/hooks_triage.py` - Triage script
- `.github/workflows/hooks-triage.yml` - Scheduled workflow
- `bridge-frontend/src/components/HooksTriagePanel.jsx` - Dashboard panel
- `docs/HOOKS_TRIAGE.md` - Complete documentation

### Modified Files
- `bridge_backend/routes/control.py` - Added hooks triage control endpoint
- `bridge_backend/main.py` - Added hooks triage to startup
- `bridge_backend/scripts/synchrony_collector.py` - Include hooks reports
- `.gitignore` - Exclude hooks_triage_report.json
