# API Triage Quick Reference

## What is API Triage?

API Triage validates API responses with schema checking to ensure endpoints return correct data structures, not just HTTP 200 status codes.

## Quick Commands

```bash
# Run API triage manually
cd bridge_backend
python3 scripts/api_triage.py --manual

# View latest report
cat api_triage_report.json

# Trigger GitHub Actions workflow
gh workflow run api-triage.yml
```

## Exit Codes

- `0` - HEALTHY (all checks pass)
- `1` - DEGRADED (1 check fails)
- `2` - CRITICAL (2+ checks fail)

## Monitored Endpoints

| Endpoint | Schema | Purpose |
|----------|--------|---------|
| `/api/diagnostics` | `{status: "str"}` | Diagnostics system |
| `/agents` | `{agents: "list"}` | Agent registry |
| `/api/status` | `{status: "str"}` | System status |

## Schema Types

- `str` - String value
- `object` - Dictionary/object
- `list` - Array/list
- `number` - Integer or float
- `boolean` - Boolean

## Event Structure

```json
{
  "type": "API_TRIAGE",
  "status": "HEALTHY|DEGRADED|CRITICAL",
  "meta": {
    "timestamp": "ISO-8601",
    "manual": false,
    "failedChecks": [...],
    "results": [...]
  }
}
```

## Frontend Component

```jsx
import APITriagePanel from './components/APITriagePanel';

<APITriagePanel />
```

## Environment Variables

- `BRIDGE_BASE_URL` - Base URL for checks (default: production)
- `BRIDGE_URL` - Diagnostics endpoint for notifications

## Integration Points

1. **Startup**: Runs automatically with backend
2. **CI/CD**: Hourly at `:30` (offset from endpoint triage)
3. **Timeline**: Events appear in diagnostics
4. **Dashboard**: 🧬 panel shows status

## Comparison

| Feature | Endpoint Triage | API Triage |
|---------|----------------|------------|
| Icon | 🩺 | 🧬 |
| Checks | Availability | Schema validity |
| Schedule | `:00` | `:30` |

## Files

- Script: `bridge_backend/scripts/api_triage.py`
- Workflow: `.github/workflows/api-triage.yml`
- Component: `bridge-frontend/src/components/APITriagePanel.jsx`
- Report: `bridge_backend/api_triage_report.json` (git ignored)

## Common Issues

### Schema Validation Failed
- Check if API response structure changed
- Verify expected schema matches actual response
- Update schema in `api_triage.py` if needed

### No Data in Frontend
- Confirm triage has run at least once
- Check `/api/diagnostics/timeline` endpoint
- Verify event type is `API_TRIAGE`

## Adding New Checks

Edit `bridge_backend/scripts/api_triage.py`:

```python
CHECKS = [
    # ... existing checks
    {
        "name": "New Check",
        "url": "/api/new-endpoint",
        "schema": {"field": "type"}
    }
]
```

## Documentation

- Full guide: `docs/API_TRIAGE.md`
- Implementation: `docs/API_TRIAGE_IMPLEMENTATION.md`
- Endpoint triage: `docs/ENDPOINT_TRIAGE.md`
