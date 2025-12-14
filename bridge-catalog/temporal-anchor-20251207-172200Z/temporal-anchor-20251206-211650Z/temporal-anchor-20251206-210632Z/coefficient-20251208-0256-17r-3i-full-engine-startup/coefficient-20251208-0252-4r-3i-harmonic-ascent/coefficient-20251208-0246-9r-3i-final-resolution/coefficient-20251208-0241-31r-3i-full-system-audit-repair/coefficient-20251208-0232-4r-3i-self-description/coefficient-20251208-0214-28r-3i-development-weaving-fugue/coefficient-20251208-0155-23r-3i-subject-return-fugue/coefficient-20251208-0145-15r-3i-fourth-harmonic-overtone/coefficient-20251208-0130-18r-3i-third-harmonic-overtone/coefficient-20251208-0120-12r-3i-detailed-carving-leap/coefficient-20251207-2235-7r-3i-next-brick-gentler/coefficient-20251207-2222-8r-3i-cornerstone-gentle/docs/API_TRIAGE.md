# API Triage System

## Overview

The API Triage System is an advanced health monitoring solution for SR-AIbridge service health. It continuously inspects all API integrations (Bridge internal + external), validates schema responses, detects regressions, and reports anomalies to the Diagnostics channel.

It extends endpoint triage by introducing behavioral and payload-level validation — so not just "is the endpoint up?" but "is it responding correctly?"

## Architecture

### Components

1. **Python Triage Script** (`bridge_backend/scripts/api_triage.py`)
   - Checks core API endpoints with schema validation
   - Validates response structure and data types
   - Generates JSON reports with detailed diagnostics
   - Sends notifications to Bridge diagnostics endpoint
   - Returns appropriate exit codes based on health status

2. **Backend Integration** (`bridge_backend/main.py`)
   - Runs API triage automatically on server startup (after 5-second delay)
   - Runs alongside endpoint triage
   - Non-blocking background execution
   - Integrates with existing FastAPI application

3. **GitHub Actions Workflow** (`.github/workflows/api-triage.yml`)
   - Runs hourly via cron schedule (`30 * * * *`) - offset from endpoint triage
   - Manual trigger via workflow_dispatch
   - Uploads triage reports as artifacts
   - Sends diagnostics to Bridge API

4. **Frontend Component** (`bridge-frontend/src/components/APITriagePanel.jsx`)
   - Displays current API health status
   - Color-coded status indicators (HEALTHY/DEGRADED/CRITICAL)
   - Lists failed checks with error details
   - Auto-refreshes every 60 seconds

## API Checks

The system validates the following endpoints with schema checking:

### 1. Bridge Diagnostics Feed
- **Endpoint**: `/api/diagnostics`
- **Schema**: `{ status: "string" }`
- **Purpose**: Verifies diagnostics system is operational

### 2. Agents Registry
- **Endpoint**: `/agents`
- **Schema**: `{ agents: "list" }`
- **Purpose**: Validates agent registry returns proper structure

### 3. System Status
- **Endpoint**: `/api/status`
- **Schema**: `{ status: "string" }`
- **Purpose**: Confirms system status endpoint responds correctly

## Schema Validation

The API Triage system validates response schemas by checking:

- **Field Presence**: Required fields must exist in response
- **Type Checking**: Fields must match expected types:
  - `str` - String values
  - `object` - Dictionary/object values
  - `list` - Array/list values
  - `number` - Integer or float values
  - `boolean` - Boolean values

### Example Schema Validation

```python
# Check definition
{
    "name": "Agents Registry",
    "url": "/agents",
    "schema": {"agents": "list"}
}

# Valid response
{
    "agents": [...]
}

# Invalid response (would fail)
{
    "agents": "not a list"  # Wrong type
}
# or
{
    "data": [...]  # Missing 'agents' field
}
```

## Health Status Levels

- **HEALTHY**: All API checks passing with valid schemas
- **DEGRADED**: 1 API check failing
- **CRITICAL**: 2 or more API checks failing

## Usage

### Manual Execution

Run API triage check manually:

```bash
cd bridge_backend
python3 scripts/api_triage.py --manual
```

Exit codes:
- `0`: HEALTHY
- `1`: DEGRADED
- `2`: CRITICAL

### View Triage Report

The script generates `api_triage_report.json` with detailed diagnostics:

```json
{
  "type": "API_TRIAGE",
  "status": "HEALTHY",
  "source": "api_triage.py",
  "meta": {
    "timestamp": "2025-01-15T12:00:00+00:00",
    "manual": false,
    "failedChecks": [],
    "results": [
      {
        "name": "Bridge Diagnostics Feed",
        "url": "/api/diagnostics",
        "status": "OK"
      }
    ],
    "environment": "backend"
  }
}
```

### Automated Execution

#### Startup Integration

The API triage automatically runs when the backend starts:

```python
# In bridge_backend/main.py
@app.on_event("startup")
async def startup_triage():
    # ... runs api_triage.py in background
```

#### GitHub Actions

The workflow runs hourly (30 minutes past the hour):

```bash
# Trigger manually
gh workflow run api-triage.yml

# View workflow runs
gh run list --workflow=api-triage.yml
```

### Frontend Integration

Import and use the `APITriagePanel` component:

```jsx
import APITriagePanel from './components/APITriagePanel';

function Dashboard() {
  return (
    <div>
      <APITriagePanel />
    </div>
  );
}
```

## Configuration

### Environment Variables

- `BRIDGE_BASE_URL`: Base URL for API checks (default: `https://bridge.sr-aibridge.com`)
- `BRIDGE_URL`: Bridge diagnostics endpoint for notifications (default: `https://sr-aibridge.netlify.app/api/diagnostics`)

### GitHub Secrets

Configure in repository settings:
- `BACKEND_URL`: Backend base URL (optional, defaults to production URL)
- `BRIDGE_URL`: Bridge diagnostics endpoint URL

## Integration with Diagnostics Timeline

API triage events appear in the Bridge Diagnostics Timeline with:
- Type: `API_TRIAGE`
- Icon: 🧬
- Status: HEALTHY/DEGRADED/CRITICAL
- Timestamp and failed check details

## Comparison with Endpoint Triage

| Feature | Endpoint Triage | API Triage |
|---------|----------------|------------|
| **Icon** | 🩺 | 🧬 |
| **Focus** | Endpoint availability | Response correctness |
| **Validation** | HTTP status codes | Schema + status codes |
| **Schedule** | Top of hour (`:00`) | Half past hour (`:30`) |
| **Type** | `ENDPOINT_TRIAGE` | `API_TRIAGE` |

Both systems work together to provide comprehensive health monitoring.

## Troubleshooting

### Triage Not Running on Startup

Check backend logs for:
```
🧬 Running API triage...
```

If missing, verify:
- Script exists at `bridge_backend/scripts/api_triage.py`
- Script has execute permissions
- Python `requests` library is installed

### Workflow Failures

1. Check workflow logs in GitHub Actions
2. Verify `BRIDGE_URL` secret is set
3. Confirm backend is accessible from GitHub Actions runners
4. Check for schema validation errors in report

### Frontend Panel Not Showing Data

1. Verify `/api/diagnostics/timeline` endpoint is working
2. Check browser console for fetch errors
3. Confirm API triage has run at least once (check diagnostics timeline)
4. Verify event type is `API_TRIAGE` (not `ENDPOINT_TRIAGE`)

### Schema Validation Errors

If API checks are failing with schema errors:

1. Check the expected schema in `api_triage.py`
2. Verify the API endpoint returns matching structure
3. Update schema if API response format has changed
4. Check for null/undefined values in required fields

## Security Considerations

- API triage runs with read-only access to endpoints
- No sensitive data is logged in triage reports
- Network errors are caught and logged safely
- Timeout protection (8 seconds) prevents hanging connections

## Extending the System

### Adding New API Checks

Edit `bridge_backend/scripts/api_triage.py`:

```python
CHECKS = [
    # ... existing checks
    {
        "name": "Your New Check",
        "url": "/api/your-endpoint",
        "schema": {
            "field1": "str",
            "field2": "object",
            "field3": "list"
        }
    }
]
```

### Custom Schema Types

Supported types in schema validation:
- `str` - String
- `object` - Dictionary/object
- `list` - Array/list
- `number` - Integer or float
- `boolean` - Boolean

### Adjusting Health Thresholds

Modify status calculation in `run_api_triage()`:

```python
# Current logic
if len(failed) == 0:
    state = "HEALTHY"
elif len(failed) <= 1:
    state = "DEGRADED"
else:
    state = "CRITICAL"
```

## Future Enhancements

Potential improvements:
- Response time tracking and alerting
- Historical trend analysis
- Automatic retry logic for transient failures
- Deep schema validation (nested objects)
- Custom alerting thresholds per endpoint
- Performance metrics collection

## Related Documentation

- [Endpoint Triage System](ENDPOINT_TRIAGE.md)
- [Diagnostics Timeline](DIAGNOSTICS_TIMELINE.md)
- [Bridge Notifications](BRIDGE_NOTIFICATIONS.md)
