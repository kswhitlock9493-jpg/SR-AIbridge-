# Endpoint Triage Quick Reference

## 🚀 Quick Start

### Manual Check
```bash
cd bridge_backend
python3 scripts/endpoint_triage.py --manual
```

### View Report
```bash
cat bridge_backend/endpoint_report.json
```

### Trigger GitHub Workflow
- Go to **Actions** → **Endpoint Triage** → **Run workflow**

### Add to Dashboard
```jsx
import EndpointStatusPanel from './components/EndpointStatusPanel';

<EndpointStatusPanel />
```

## 📊 Status Levels

| Status | Condition | Icon | Color |
|--------|-----------|------|-------|
| HEALTHY | 0 endpoints failed | ✅ | Green |
| DEGRADED | 1 endpoint failed | ⚠️ | Yellow |
| CRITICAL | 2+ endpoints failed | 🚨 | Red |

## 🔍 Monitored Endpoints

1. `GET /api/status` - Frontend health check
2. `POST /api/diagnostics` - Diagnostics submission  
3. `GET /agents` - Agent listing

## 🔧 Configuration

### Environment Variables
- `BRIDGE_BASE_URL` - Backend URL (default: https://sr-aibridge.onrender.com)
- `BRIDGE_URL` - Frontend URL (default: https://sr-aibridge.netlify.app)

### Add New Endpoint
Edit `bridge_backend/scripts/endpoint_triage.py`:
```python
ENDPOINTS = [
    {"name": "status", "url": "/api/status"},
    {"name": "diagnostics", "url": "/api/diagnostics"},
    {"name": "agents", "url": "/agents"},
    {"name": "health", "url": "/health"},  # ← Add here
]
```

## 📅 Automated Execution

- **On Startup**: Runs 5 seconds after backend starts
- **Hourly**: GitHub Actions cron job (`0 * * * *`)
- **Manual**: Via GitHub Actions UI or command line

## 🛠️ Troubleshooting

### Script Not Running
```bash
# Check script exists and is executable
ls -l bridge_backend/scripts/endpoint_triage.py

# Make executable if needed
chmod +x bridge_backend/scripts/endpoint_triage.py

# Check Python dependencies
pip install requests
```

### Frontend Not Showing Data
```bash
# Check diagnostics timeline API
curl http://localhost:8000/api/diagnostics/timeline

# Verify triage has run
cat bridge_backend/endpoint_report.json
```

### Workflow Failures
1. Check GitHub Actions logs
2. Verify `BRIDGE_URL` secret is set
3. Ensure backend is accessible

## 📝 Example Report

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
        "data": {"message": "OK"}
      },
      {
        "name": "diagnostics",
        "status": "OK",
        "data": {"status": "received"}
      },
      {
        "name": "agents",
        "status": "OK",
        "data": [...]
      }
    ],
    "environment": "backend"
  }
}
```

## 🔗 Related Documentation

- **Full Guide**: `docs/ENDPOINT_TRIAGE.md`
- **Implementation Details**: `docs/ENDPOINT_TRIAGE_IMPLEMENTATION.md`
- **Diagnostics System**: `docs/BRIDGE_NOTIFICATIONS_ROLLBACK.md`

## 💡 Tips

- Use `--manual` flag for on-demand checks
- Check `endpoint_report.json` for detailed diagnostics
- Monitor DiagnosticsTimeline for triage history
- Set up alerts for CRITICAL status
- Review GitHub Actions artifacts for historical data
