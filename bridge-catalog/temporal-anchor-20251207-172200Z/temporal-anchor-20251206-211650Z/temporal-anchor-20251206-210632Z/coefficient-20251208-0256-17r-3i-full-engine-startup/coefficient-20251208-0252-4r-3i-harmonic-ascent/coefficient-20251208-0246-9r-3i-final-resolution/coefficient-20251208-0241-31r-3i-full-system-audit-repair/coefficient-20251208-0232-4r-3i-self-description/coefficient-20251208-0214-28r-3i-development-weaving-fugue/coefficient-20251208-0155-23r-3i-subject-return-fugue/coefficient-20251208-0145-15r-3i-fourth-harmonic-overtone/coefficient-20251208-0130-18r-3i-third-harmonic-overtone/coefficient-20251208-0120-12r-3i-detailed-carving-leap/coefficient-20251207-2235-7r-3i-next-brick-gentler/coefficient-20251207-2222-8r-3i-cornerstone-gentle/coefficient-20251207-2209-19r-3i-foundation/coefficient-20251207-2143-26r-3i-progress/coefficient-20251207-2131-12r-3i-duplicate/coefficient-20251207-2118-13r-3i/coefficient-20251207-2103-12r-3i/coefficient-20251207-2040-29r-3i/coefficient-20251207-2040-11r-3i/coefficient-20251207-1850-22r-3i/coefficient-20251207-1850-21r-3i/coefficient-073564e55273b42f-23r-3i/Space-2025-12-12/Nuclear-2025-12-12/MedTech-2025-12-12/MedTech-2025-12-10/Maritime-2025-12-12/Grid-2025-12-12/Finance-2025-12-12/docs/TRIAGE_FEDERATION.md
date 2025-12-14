# Triage Federation v1.7.5

## Overview

The Triage Federation system provides robust, self-healing health checks for the SR-AIbridge platform. It combines API triage, endpoint triage, and diagnostics federation with built-in retry logic, backoff mechanisms, and circuit breakers to reduce false-positive alerts.

## Components

### 1. Shared Triage Client (`bridge_backend/tools/triage/common/utils.py`)

A reusable HTTP client library with:
- **Configurable timeouts**: Default 8000ms, configurable via `TRIAGE_TIMEOUT_MS`
- **Exponential backoff**: Base 0.8s with 2.0x multiplier per retry
- **Jitter**: Random delay up to 350ms to avoid thundering herd
- **Circuit breaker**: Stops after 6 consecutive failures
- **Retry logic**: Up to 4 attempts by default

### 2. API Triage (`bridge_backend/tools/triage/api_triage.py`)

Tests multiple common health check endpoints:
- `/api/health`
- `/api/v1/health`
- `/healthz`
- `/api/_meta`
- `/api/version`

**Success criteria**: At least one endpoint responds with HTTP 200.

**Output**: `bridge_backend/diagnostics/api_triage_report.json`

### 3. Endpoint Triage (`bridge_backend/tools/triage/endpoint_triage.py`)

Parity-aware endpoint testing:
- Reads `bridge_parity_report.json` to identify routes missing from frontend
- Tests up to 20 endpoints (configurable via `ENDPOINT_TRIAGE_LIMIT`)
- Uses retry logic for each endpoint

**Success criteria**: All tested endpoints respond successfully.

**Output**: `bridge_backend/diagnostics/endpoint_triage_report.json`

### 4. Diagnostics Federation (`bridge_backend/tools/triage/diagnostics_federate.py`)

Heartbeat aggregator:
- Waits up to 120 seconds for all triage reports
- Bundles all reports into a single federation report
- Only fails if all self-healing paths are exhausted

**Output**: `bridge_backend/diagnostics/triage_federation_report.json`

### 5. GitHub Action (`triage_federation.yml`)

Automated workflow that:
- Runs every 30 minutes via cron
- Triggers on push to main branch
- Triggers on pull requests
- Can be manually dispatched

**Workflow steps**:
1. Run API triage (continues on failure)
2. Run endpoint triage (continues on failure)
3. Run diagnostics federation (continues on failure)
4. Upload all reports as artifacts
5. Fail only if federation report shows failure

## Environment Variables

### Required
- `PUBLIC_API_BASE` or `VITE_API_BASE`: Base URL for API endpoints (e.g., `https://sr-aibridge.onrender.com`)

### Optional Tuning
- `TRIAGE_TIMEOUT_MS`: HTTP timeout in milliseconds (default: 8000)
- `TRIAGE_MAX_RETRIES`: Maximum retry attempts (default: 4)
- `TRIAGE_BACKOFF_BASE`: Base backoff delay in seconds (default: 0.8)
- `TRIAGE_BACKOFF_FACTOR`: Backoff multiplier (default: 2.0)
- `TRIAGE_JITTER_MAX`: Maximum jitter in seconds (default: 0.35)
- `TRIAGE_CIRCUIT_BREAKER_FAILS`: Failures before circuit break (default: 6)
- `ENDPOINT_TRIAGE_LIMIT`: Max endpoints to test (default: 20)
- `FEDERATION_MAX_WAIT_S`: Max wait for reports (default: 120)

## How Retries & Backoff Work

Each HTTP request follows this pattern:

1. **Attempt 1**: Immediate request
2. **Attempt 2**: Wait 0.8s + jitter (0-0.35s)
3. **Attempt 3**: Wait 1.6s + jitter
4. **Attempt 4**: Wait 3.2s + jitter

If the circuit breaker threshold (6 failures) is reached before max retries, the check stops early.

## Report Formats

### API Triage Report
```json
{
  "ok": true,
  "base": "https://sr-aibridge.onrender.com",
  "checks": [
    {
      "path": "/api/health",
      "result": {
        "ok": true,
        "attempts": 1,
        "code": 200
      }
    }
  ]
}
```

### Endpoint Triage Report
```json
{
  "ok": true,
  "tested": [
    {
      "rel": "/api/agents",
      "url": "https://sr-aibridge.onrender.com/api/agents",
      "result": {
        "ok": true,
        "attempts": 2,
        "code": 200
      }
    }
  ],
  "missing": [],
  "base": "https://sr-aibridge.onrender.com"
}
```

### Federation Report
```json
{
  "ok": true,
  "waited_s": 4,
  "reports": {
    "api_triage_report.json": { "ok": true, ... },
    "endpoint_triage_report.json": { "ok": true, ... },
    "firewall_report.json": { "ok": true, "note": "not-generated" }
  }
}
```

## Reading Reports

Reports are uploaded as artifacts in GitHub Actions:
1. Go to Actions → Triage Federation Heartbeat
2. Select a workflow run
3. Download "triage-federation-reports" artifact
4. Unzip and review JSON files

## Local Testing

```bash
# Set environment variables
export PUBLIC_API_BASE=https://sr-aibridge.onrender.com
export TRIAGE_MAX_RETRIES=4

# Run individual triage scripts
cd bridge_backend/tools/triage
python3 api_triage.py
python3 endpoint_triage.py
python3 diagnostics_federate.py

# Check outputs
cat ../../diagnostics/api_triage_report.json
cat ../../diagnostics/endpoint_triage_report.json
cat ../../diagnostics/triage_federation_report.json
```

## Integration with Existing Systems

This federation system complements existing triage systems:
- **API Triage** (`bridge_backend/scripts/api_triage.py`): Legacy script, still runs on startup
- **Endpoint Triage** (`bridge_backend/scripts/endpoint_triage.py`): Legacy script, still runs hourly
- **Hooks Triage** (`bridge_backend/scripts/hooks_triage.py`): Independent webhook monitoring

The new federation system provides a unified, robust view across all triage operations.

## Troubleshooting

### "parity report missing" error
Run the parity engine first:
```bash
python3 bridge_backend/tools/parity_engine.py
```

### "PUBLIC_API_BASE missing" error
Set the environment variable:
```bash
export PUBLIC_API_BASE=https://sr-aibridge.onrender.com
```

### All checks failing
Check network connectivity and ensure the API is actually running:
```bash
curl https://sr-aibridge.onrender.com/api/health
```

## Version History

- **v1.7.5**: Initial triage federation with auto-heal, backoff, and circuit breaker
