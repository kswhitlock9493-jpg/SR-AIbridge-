# API Triage System Implementation Summary

## Overview

The API Triage module has been successfully implemented to continuously inspect all API integrations, validate schema responses, detect regressions, and report anomalies to the Diagnostics channel.

## Files Created

### 1. Backend Script
**`bridge_backend/scripts/api_triage.py`**
- Python-based API triage automation (adapted to match existing Python backend)
- Monitors 3 core endpoints with schema validation
- Validates response structure and data types
- Generates JSON diagnostic reports
- Reports to Bridge diagnostics API
- Returns appropriate exit codes (0=HEALTHY, 1=DEGRADED, 2=CRITICAL)

### 2. GitHub Actions Workflow
**`.github/workflows/api-triage.yml`**
- Runs hourly via cron (`30 * * * *`) - offset 30 minutes from endpoint triage
- Manual trigger via workflow_dispatch
- Uploads triage reports as artifacts
- Posts diagnostics to Bridge API

### 3. Frontend Component
**`bridge-frontend/src/components/APITriagePanel.jsx`**
- Real-time API health dashboard
- Color-coded status indicators (green/yellow/red)
- Auto-refreshes every 60 seconds
- Shows failed checks with schema validation errors
- Fetches data from diagnostics timeline

### 4. Documentation
**`docs/API_TRIAGE.md`**
- Complete usage guide
- Schema validation explanation
- Configuration instructions
- Troubleshooting tips
- Integration examples
- Comparison with endpoint triage

## Files Modified

### 1. Backend Integration
**`bridge_backend/main.py`**
- Added API triage to startup event handler
- Runs alongside existing endpoint triage
- Non-blocking background execution

### 2. Git Ignore
**`.gitignore`**
- Added `bridge_backend/api_triage_report.json` to prevent committing generated reports

## Architecture Integration

### Event Flow

```
1. Startup Triage
   Backend Starts → (5 sec delay) → endpoint_triage.py + api_triage.py
        ↓
   Check Endpoints & Validate Schemas
        ↓
   Generate Reports → api_triage_report.json
        ↓
   POST to /api/diagnostics → Bridge stores event
        ↓
   Frontend polls /api/diagnostics/timeline
        ↓
   APITriagePanel displays status

2. Scheduled Triage (Hourly)
   GitHub Actions Cron (30 min offset) → Run api_triage.py
        ↓
   Check Endpoints & Schemas → Generate Report
        ↓
   Upload Artifact + POST to Bridge
        ↓
   Frontend updates automatically

3. Manual Triage
   User runs: python3 scripts/api_triage.py --manual
        ↓
   Same flow as above
```

### Status Calculation

- **HEALTHY**: 0 failed checks
- **DEGRADED**: 1 failed check
- **CRITICAL**: 2+ failed checks

### Integration Points

1. **Backend Startup**: FastAPI `@app.on_event("startup")` runs both triages
2. **Diagnostics API**: POST `/api/diagnostics` receives triage events
3. **Timeline API**: GET `/api/diagnostics/timeline` serves triage data
4. **Frontend Dashboard**: APITriagePanel displays latest triage
5. **CI/CD Pipeline**: GitHub Actions runs hourly checks (offset from endpoint triage)

## Schema Validation Features

The API triage system validates:

1. **Field Presence**: Required fields must exist
2. **Type Checking**: Fields must match expected types
   - `str` - String values
   - `object` - Dictionary values
   - `list` - Array values
   - `number` - Numeric values
   - `boolean` - Boolean values

### Example Validation

```python
# Check definition
{
    "name": "Agents Registry",
    "url": "/agents",
    "schema": {"agents": "list"}
}

# Validates that response has 'agents' field containing a list
```

## Key Differences from Endpoint Triage

| Aspect | Endpoint Triage | API Triage |
|--------|----------------|------------|
| **Icon** | 🩺 | 🧬 |
| **Primary Focus** | Availability | Correctness |
| **Validation** | HTTP status only | Status + schema |
| **Cron Schedule** | `:00` (top of hour) | `:30` (offset) |
| **Event Type** | `ENDPOINT_TRIAGE` | `API_TRIAGE` |
| **Report File** | `endpoint_report.json` | `api_triage_report.json` |

## End-to-End Behavior

### Startup Sequence
1. Backend starts
2. After 5-second delay:
   - Endpoint triage runs (checks availability)
   - API triage runs (validates schemas)
3. Both report to diagnostics timeline

### CI/CD Automation
- **0:00** - Endpoint triage runs (availability)
- **0:30** - API triage runs (schema validation)
- Both upload reports and notify Bridge

### Dashboard Display
- 🩺 **Endpoint Triage Panel** - Shows availability status
- 🧬 **API Triage Panel** - Shows schema validation status
- Both panels auto-refresh every 60 seconds

### Diagnostics Timeline Integration

The diagnostics timeline receives structured events:

```json
{
  "type": "API_TRIAGE",
  "status": "HEALTHY|DEGRADED|CRITICAL",
  "source": "api_triage.py",
  "meta": {
    "timestamp": "2025-01-15T12:30:00Z",
    "manual": false,
    "failedChecks": [...],
    "results": [...],
    "environment": "backend"
  }
}
```

## Testing

### Manual Testing
```bash
# Test API triage script
cd bridge_backend
python3 scripts/api_triage.py --manual

# Check generated report
cat api_triage_report.json
```

### Expected Output
```
🧬 Starting API triage...
  ✅ Bridge Diagnostics Feed: OK
  ✅ Agents Registry: OK
  ✅ System Status: OK
📄 Report saved to api_triage_report.json
✅ Bridge notified successfully

📡 API Triage: HEALTHY
```

## Configuration

### Environment Variables
- `BRIDGE_BASE_URL` - Base URL for API checks
- `BRIDGE_URL` - Diagnostics endpoint for notifications

### GitHub Secrets (Required)
- `BACKEND_URL` - Backend base URL (optional)
- `BRIDGE_URL` - Bridge diagnostics endpoint

## Benefits

1. **Proactive Monitoring**: Detects issues before they affect users
2. **Schema Validation**: Catches breaking API changes early
3. **Comprehensive Coverage**: Works alongside endpoint triage
4. **Real-time Visibility**: Dashboard shows current status
5. **Historical Tracking**: Events stored in diagnostics timeline
6. **Automated Alerting**: Reports sent to Bridge automatically

## Success Metrics

| Component | Function | Outcome |
|-----------|----------|---------|
| API Triage Script | Validates responses and schemas | ✅ Detects failures before users |
| Diagnostics Reporting | Sends structured results to Bridge | ✅ Central timeline updated |
| GitHub Automation | Runs every hour (offset) | ✅ Maintains live health map |
| Frontend Panel | Displays latest triage | ✅ Real-time status visualization |

## Future Enhancements

Potential improvements:
- Response time tracking
- Historical trend analysis
- Automatic retry logic
- Deep schema validation (nested objects)
- Custom alerting thresholds
- Performance metrics

## Related Systems

- **Endpoint Triage**: Checks endpoint availability
- **Diagnostics Timeline**: Stores all triage events
- **Bridge Notifications**: Receives triage reports
- **Deployment Recovery**: Uses triage data for health checks
