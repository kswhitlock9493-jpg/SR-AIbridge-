# SR-AIbridge Full Endpoint Test

Comprehensive endpoint testing tool for validating all SR-AIbridge backend API endpoints.

## Features

- Tests all critical API endpoints with retry logic
- Detailed success/failure reporting
- Configurable timeout and retry settings
- JSON output format for CI/CD integration
- Color-coded console output
- Tests health, diagnostics, agents, and engine endpoints

## Usage

### Basic Usage

Test a local backend:
```bash
python3 test_endpoints_full.py
```

Test a deployed backend:
```bash
python3 test_endpoints_full.py https://your-backend.onrender.com
```

### Advanced Options

```bash
# Custom timeout
python3 test_endpoints_full.py --timeout 10

# JSON output for CI/CD
python3 test_endpoints_full.py --json

# Combine options
python3 test_endpoints_full.py https://your-backend.onrender.com --timeout 60 --json
```

### Help

```bash
python3 test_endpoints_full.py --help
```

## Tested Endpoints

### Core Endpoints (Required)
- `GET /health` - Basic health check
- `GET /health/full` - Comprehensive health check
- `GET /status` - System status
- `GET /api/status` - Frontend health check
- `POST /api/diagnostics` - Diagnostics submission
- `GET /agents` - List agents

### Engine Endpoints (Optional)
- `POST /engines/leviathan/solve` - Leviathan Solver
- `POST /engines/truth/find` - Truth Engine
- `POST /engines/parser/parse` - Parser Engine
- `POST /engines/math/prove` - Math Engine (may return 404)
- `POST /engines/quantum/collapse` - Quantum Engine (may return 404)
- `POST /engines/science/experiment` - Science Engine (may return 404)
- `POST /engines/language/translate` - Language Engine (may return 404)
- `POST /engines/business/analyze` - Business Engine (may return 404)
- `POST /engines/history/chronicle` - History Engine (may return 404)

## Exit Codes

- `0` - All tests passed
- `1` - Some tests failed
- `2` - All tests failed (backend not running or misconfigured)

## Output

### Console Output
Provides color-coded, human-readable output with:
- Test progress with numbered steps
- Pass/fail status with emojis
- Response times
- Error messages for failed tests
- Summary statistics

### JSON Output
Structured JSON format suitable for:
- CI/CD pipelines
- Automated monitoring
- Log aggregation systems

Example:
```json
{
  "timestamp": "2024-01-15T12:00:00Z",
  "base_url": "http://localhost:8000",
  "total_tests": 15,
  "passed": 15,
  "failed": 0,
  "tests": [
    {
      "name": "Health Check",
      "method": "GET",
      "endpoint": "/health",
      "result": "PASSED",
      "status_code": 200,
      "response_time": 0.01,
      "error": null
    }
  ]
}
```

## Integration

### CI/CD Pipeline

Add to GitHub Actions:
```yaml
- name: Test Backend Endpoints
  run: |
    python3 test_endpoints_full.py ${{ secrets.BACKEND_URL }} --timeout 60 --json > endpoint_results.json
    
- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: endpoint-test-results
    path: endpoint_results.json
```

### Monitoring

Schedule regular endpoint tests:
```bash
# Run every 5 minutes
*/5 * * * * cd /path/to/SR-AIbridge && python3 test_endpoints_full.py --json >> /var/log/endpoint_tests.log
```

## Comparison with smoke_test_engines.sh

This tool differs from `smoke_test_engines.sh` in several ways:

| Feature | test_endpoints_full.py | smoke_test_engines.sh |
|---------|----------------------|----------------------|
| Language | Python | Bash |
| JSON Output | ✅ Yes | ❌ No |
| Retry Logic | ✅ Configurable | ✅ Fixed (3 retries) |
| Response Times | ✅ Measured | ❌ No |
| Core Endpoints | ✅ Yes | ❌ No |
| Engine Endpoints | ✅ Yes | ✅ Yes |
| CI/CD Ready | ✅ Yes | ⚠️ Limited |

Use `test_endpoints_full.py` for:
- Comprehensive endpoint validation
- CI/CD integration
- Detailed reporting
- JSON output needs

Use `smoke_test_engines.sh` for:
- Quick engine-only checks
- Bash-based workflows
- Legacy compatibility

## Troubleshooting

### All Tests Fail
- Ensure backend is running
- Check backend URL is correct
- Verify network connectivity
- Try increasing timeout: `--timeout 60`

### Some Tests Fail
- Check which specific endpoints are failing
- Review error messages in output
- Some engine endpoints may not be implemented (404 is expected)

### Connection Timeouts
- Increase timeout value
- Check backend performance
- Verify backend is not overloaded

## Requirements

- Python 3.7+
- `requests` library (included in requirements.txt)

## License

Part of SR-AIbridge project. See main repository for license details.
