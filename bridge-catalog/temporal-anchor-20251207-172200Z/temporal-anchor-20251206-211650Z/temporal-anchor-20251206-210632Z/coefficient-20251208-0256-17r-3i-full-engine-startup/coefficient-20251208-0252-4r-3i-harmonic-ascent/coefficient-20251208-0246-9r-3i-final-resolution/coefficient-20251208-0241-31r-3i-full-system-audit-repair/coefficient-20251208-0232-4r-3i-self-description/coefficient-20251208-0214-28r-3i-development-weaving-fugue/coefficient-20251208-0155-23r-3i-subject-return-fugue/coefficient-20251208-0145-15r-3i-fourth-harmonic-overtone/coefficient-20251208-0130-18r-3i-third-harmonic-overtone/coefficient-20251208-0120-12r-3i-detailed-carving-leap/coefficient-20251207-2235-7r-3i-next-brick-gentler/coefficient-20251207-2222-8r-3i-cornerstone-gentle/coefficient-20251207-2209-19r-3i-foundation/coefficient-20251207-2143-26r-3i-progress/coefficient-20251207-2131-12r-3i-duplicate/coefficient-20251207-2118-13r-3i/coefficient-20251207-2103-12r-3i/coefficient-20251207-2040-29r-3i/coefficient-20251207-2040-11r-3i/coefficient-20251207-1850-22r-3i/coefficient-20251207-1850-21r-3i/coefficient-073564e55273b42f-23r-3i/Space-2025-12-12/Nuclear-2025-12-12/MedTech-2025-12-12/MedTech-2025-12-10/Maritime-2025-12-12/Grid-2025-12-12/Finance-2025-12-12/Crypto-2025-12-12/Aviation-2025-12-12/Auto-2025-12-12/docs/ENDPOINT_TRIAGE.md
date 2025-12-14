# Endpoint Triage System

## Overview

The Endpoint Triage System is an autonomous health monitoring solution for SR-AIbridge backend endpoints. It performs automatic health checks, reports status to the Bridge diagnostics system, and provides real-time visibility into endpoint availability.

## Architecture

### Components

1. **Python Triage Script** (`bridge_backend/scripts/endpoint_triage.py`)
   - Checks core API endpoints: `/api/status`, `/api/diagnostics`, `/agents`
   - Generates JSON reports with detailed diagnostics
   - Sends notifications to Bridge diagnostics endpoint
   - Returns appropriate exit codes based on health status

2. **Backend Integration** (`bridge_backend/main.py`)
   - Runs triage automatically on server startup (after 5-second delay)
   - Non-blocking background execution
   - Integrates with existing FastAPI application

3. **GitHub Actions Workflow** (`.github/workflows/endpoint-triage.yml`)
   - Runs hourly via cron schedule (`0 * * * *`)
   - Manual trigger via workflow_dispatch
   - Uploads triage reports as artifacts
   - Sends diagnostics to Bridge API

4. **Frontend Component** (`bridge-frontend/src/components/EndpointStatusPanel.jsx`)
   - Displays current endpoint health status
   - Color-coded status indicators (HEALTHY/DEGRADED/CRITICAL)
   - Lists failed endpoints with details
   - Auto-refreshes every 60 seconds

## Health Status Levels

- **HEALTHY**: All endpoints responding correctly
- **DEGRADED**: 1 endpoint failing
- **CRITICAL**: 2 or more endpoints failing

## Usage

### Manual Execution

Run triage check manually:

```bash
cd bridge_backend
python3 scripts/endpoint_triage.py --manual
```

Exit codes:
- `0`: HEALTHY
- `1`: DEGRADED
- `2`: CRITICAL

### View Triage Report

The script generates `endpoint_report.json` with detailed diagnostics:

```json
{
  "type": "ENDPOINT_TRIAGE",
  "status": "HEALTHY",
  "source": "endpoint_triage.py",
  "meta": {
    "timestamp": "2025-01-15T12:00:00+00:00",
    "manual": false,
    "failedEndpoints": [],
    "results": [
      {
        "name": "status",
        "status": "OK",
        "data": {...}
      }
    ],
    "environment": "backend"
  }
}
```

### Automated Execution

The triage runs automatically:

1. **On Backend Startup**: 5 seconds after server starts
2. **Hourly via GitHub Actions**: Every hour on the hour
3. **Manual Workflow Trigger**: Via GitHub Actions UI

### Frontend Integration

Add the EndpointStatusPanel component to your dashboard:

```jsx
import EndpointStatusPanel from './components/EndpointStatusPanel';

function Dashboard() {
  return (
    <div>
      <EndpointStatusPanel />
      {/* other components */}
    </div>
  );
}
```

## Configuration

### Environment Variables

- `BRIDGE_BASE_URL`: Backend URL to check (default: `https://sr-aibridge.onrender.com`)
- `BRIDGE_URL`: Bridge frontend URL for diagnostics (default: `https://sr-aibridge.netlify.app`)

### Monitored Endpoints

Current endpoints:
- `GET /api/status` - Frontend health check
- `POST /api/diagnostics` - Diagnostics submission
- `GET /agents` - Agent listing

To add more endpoints, edit `ENDPOINTS` array in `endpoint_triage.py`:

```python
ENDPOINTS = [
    {"name": "status", "url": "/api/status"},
    {"name": "diagnostics", "url": "/api/diagnostics"},
    {"name": "agents", "url": "/agents"},
    # Add new endpoints here
    {"name": "health", "url": "/health"},
]
```

## Integration with Diagnostics Timeline

Triage events appear in the Bridge Diagnostics Timeline with:
- Type: `ENDPOINT_TRIAGE`
- Icon: 🩺
- Status: HEALTHY/DEGRADED/CRITICAL
- Timestamp and failed endpoint details

## Troubleshooting

### Triage Not Running on Startup

Check backend logs for:
```
🚑 Running initial endpoint triage...
```

If missing, verify:
- Script exists at `bridge_backend/scripts/endpoint_triage.py`
- Script has execute permissions
- Python `requests` library is installed

### Workflow Failures

1. Check workflow logs in GitHub Actions
2. Verify `BRIDGE_URL` secret is set
3. Confirm backend is accessible from GitHub Actions runners

### Frontend Panel Not Showing Data

1. Verify `/api/diagnostics/timeline` endpoint is working
2. Check browser console for fetch errors
3. Confirm triage has run at least once (check diagnostics timeline)

## Security Considerations

- Triage runs in background without blocking server startup
- No sensitive data logged in triage reports
- Reports are excluded from git via `.gitignore`
- Graceful failure: continues even if Bridge notification fails

## Future Enhancements

Potential improvements:
- Configurable endpoint timeout values
- Retry logic for transient failures
- Alerting thresholds (e.g., notify on DEGRADED for X minutes)
- Historical trend analysis
- Per-endpoint custom health checks
- Integration with self-healing mechanisms
