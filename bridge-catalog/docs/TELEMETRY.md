# Runtime Telemetry (v1.8.5)

## Overview

The SR-AIbridge runtime telemetry system provides real-time observability into system health, performance, and operational metrics. It collects and exposes data from various system components to enable rapid diagnostics and informed decision-making.

## Features

- **In-Process Metrics Collection**: Low-overhead telemetry integrated directly into the runtime
- **Rolling Health Windows**: Time-windowed counters and event logs to track trends
- **Latency Tracking**: Request latency buckets with p50/p95 percentiles
- **Event Logging**: Recent events from DB readiness, egress checks, health probes, and requests
- **JSON API**: Accessible via `/api/telemetry` for CI probes and human reviews

## Endpoints

### GET /api/telemetry

Returns a JSON snapshot of runtime telemetry data.

**Response Schema:**
```json
{
  "meta": {
    "service": "SR-AIbridge Backend",
    "env": "production",
    "host": "hostname",
    "uptime_s": 3600
  },
  "counters": {
    "health_ok": 10,
    "health_fail": 0,
    "egress_ok": 80,
    "egress_fail": 2,
    "db_ready_ok": 1,
    "db_ready_fail": 0
  },
  "latency_ms": {
    "count": 250,
    "p50": 45,
    "p95": 120
  },
  "recent_events": [
    {
      "t": 1704067200,
      "kind": "egress",
      "ok": true,
      "ms": 23,
      "note": "api.github.com"
    }
  ]
}
```

## Telemetry Sources

### Database Readiness (`db_ready`)
- Recorded by: `bridge_backend/runtime/wait_for_db.py`
- Tracks PostgreSQL connection establishment time
- Success/failure with timing information

### Egress Connectivity (`egress`)
- Recorded by: `bridge_backend/runtime/egress_canary.py`
- Monitors outbound connectivity to critical hosts
- Per-host timing and success/failure status

### Health Probes (`health`)
- Recorded by: `bridge_backend/runtime/health_probe.py`
- Tracks health endpoint warming and readiness
- Startup health check metrics

### Request Metrics
- Recorded by: `bridge_backend/runtime/metrics_middleware.py`
- Captures HTTP request latencies
- Lightweight sampling for performance monitoring

## Usage

### Accessing Telemetry

**Via curl:**
```bash
curl -sS https://sr-aibridge.onrender.com/api/telemetry | jq .
```

**In CI/CD:**
```bash
# Check if service is healthy
response=$(curl -sS https://sr-aibridge.onrender.com/api/telemetry)
health_ok=$(echo "$response" | jq '.counters.health_ok')
health_fail=$(echo "$response" | jq '.counters.health_fail')

if [ "$health_fail" -gt 0 ]; then
  echo "Health check failures detected"
  exit 1
fi
```

**In Python:**
```python
import requests

resp = requests.get("https://sr-aibridge.onrender.com/api/telemetry")
data = resp.json()

print(f"Service uptime: {data['meta']['uptime_s']}s")
print(f"P95 latency: {data['latency_ms']['p95']}ms")
```

## Configuration

Telemetry is enabled by default with sensible defaults:

- **Event window**: 120 seconds (configurable via `Telemetry(window=...`)
- **Max events**: 2048 (deque maxlen)
- **Latency samples**: 512 (deque maxlen)
- **Environment**: Read from `ENVIRONMENT` env var (default: "production")

## Integration Points

The telemetry system integrates with:

1. **Runtime Scripts**: DB wait, egress checks, health probes
2. **HTTP Middleware**: Request/response timing
3. **CI/CD Pipelines**: Federation triage and smoke tests
4. **Monitoring Tools**: External observers can poll `/api/telemetry`

## Privacy & Security

- No PII or sensitive data is collected
- All data is in-memory only (not persisted to disk)
- Telemetry data is publicly accessible via the API endpoint
- No authentication required for telemetry endpoint (monitoring-friendly)

## Related Documentation

- [Runtime Troubleshooting Guide](RUNTIME_TROUBLESHOOTING.md)
- [Triage Systems Architecture](TRIAGE_SYSTEMS.md)
- [Federation Runtime Guard Workflow](../.github/workflows/federation_runtime_guard.yml)
