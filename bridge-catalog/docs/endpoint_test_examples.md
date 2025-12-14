# Endpoint Test Examples

This document demonstrates various use cases for the `test_endpoints_full.py` script.

## Example 1: Successful Backend Test

Testing a fully functional backend:

```bash
$ python3 test_endpoints_full.py http://localhost:8000

🚀 SR-AIbridge Comprehensive Endpoint Test
======================================================================
Backend URL: http://localhost:8000
Timeout: 30s
Max Retries: 3
Total Tests: 15
======================================================================

[1/15] Testing: Health Check
  Endpoint: GET /health
  Description: Basic health check for load balancers
  ✅ PASSED (HTTP 200, 0.01s)

[2/15] Testing: Full Health Check
  Endpoint: GET /health/full
  Description: Comprehensive system health check
  ✅ PASSED (HTTP 200, 0.00s)

... (additional tests) ...

======================================================================
📊 Test Summary
======================================================================
Total Tests:  15
Passed:       15
Failed:       0
Success Rate: 100.0%
======================================================================

🎉 All endpoints are functional!
✅ SR-AIbridge backend is ready for operation
```

**Exit Code:** 0 (success)

## Example 2: Partial Failures

Testing a backend with some failing endpoints:

```bash
$ python3 test_endpoints_full.py http://localhost:8001 --timeout 3

🚀 SR-AIbridge Comprehensive Endpoint Test
======================================================================
Backend URL: http://localhost:8001
Timeout: 3s
Max Retries: 3
Total Tests: 15
======================================================================

[1/15] Testing: Health Check
  Endpoint: GET /health
  Description: Basic health check for load balancers
  ✅ PASSED (HTTP 200, 0.01s)

[2/15] Testing: Full Health Check
  Endpoint: GET /health/full
  Description: Comprehensive system health check
  ❌ FAILED
  Error: Expected 200, got 500

[4/15] Testing: API Status
  Endpoint: GET /api/status
  Description: Frontend health check endpoint
  ❌ FAILED
  Error: Expected 200, got 503

... (additional tests) ...

======================================================================
📊 Test Summary
======================================================================
Total Tests:  15
Passed:       8
Failed:       7
Success Rate: 53.3%
======================================================================

Failed Tests:
  ❌ Full Health Check
     Endpoint: GET /health/full
     Error: Expected 200, got 500
  ❌ API Status
     Endpoint: GET /api/status
     Error: Expected 200, got 503
  ... (additional failures) ...

⚠️  Some endpoints need attention
📋 Check the detailed output above
```

**Exit Code:** 1 (partial failure)

## Example 3: JSON Output for CI/CD

Using JSON output format for automated processing:

```bash
$ python3 test_endpoints_full.py http://localhost:8000 --json

{
  "timestamp": "2024-01-15T12:00:00.000000+00:00",
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
      "response_time": 0.010123,
      "error": null
    },
    {
      "name": "Full Health Check",
      "method": "GET",
      "endpoint": "/health/full",
      "result": "PASSED",
      "status_code": 200,
      "response_time": 0.005432,
      "error": null
    },
    ... (additional test results) ...
  ]
}
```

**Exit Code:** 0 (success)

This JSON output can be:
- Piped to `jq` for filtering: `python3 test_endpoints_full.py --json | jq '.tests[] | select(.result == "FAILED")'`
- Saved to a file: `python3 test_endpoints_full.py --json > results.json`
- Uploaded as a CI/CD artifact
- Sent to monitoring systems

## Example 4: Backend Not Running

Testing when the backend is completely unavailable:

```bash
$ python3 test_endpoints_full.py http://localhost:9999 --timeout 2

🚀 SR-AIbridge Comprehensive Endpoint Test
======================================================================
Backend URL: http://localhost:9999
Timeout: 2s
Max Retries: 3
Total Tests: 15
======================================================================

[1/15] Testing: Health Check
  Endpoint: GET /health
  Description: Basic health check for load balancers
  ❌ FAILED
  Error: Connection error (attempt 3/3)

[2/15] Testing: Full Health Check
  Endpoint: GET /health/full
  Description: Comprehensive system health check
  ❌ FAILED
  Error: Connection error (attempt 3/3)

... (all tests fail) ...

======================================================================
📊 Test Summary
======================================================================
Total Tests:  15
Passed:       0
Failed:       15
Success Rate: 0.0%
======================================================================

Failed Tests:
  ❌ Health Check
     Endpoint: GET /health
     Error: Connection error (attempt 3/3)
  ... (all endpoints listed) ...

⚠️  Some endpoints need attention
📋 Check the detailed output above

❌ All endpoint tests failed
🚨 Backend may not be running or is misconfigured
```

**Exit Code:** 2 (complete failure - backend not running)

## Example 5: Testing Deployed Backend

Testing a production deployment:

```bash
$ python3 test_endpoints_full.py https://sr-aibridge.onrender.com --timeout 60

🚀 SR-AIbridge Comprehensive Endpoint Test
======================================================================
Backend URL: https://sr-aibridge.onrender.com
Timeout: 60s
Max Retries: 3
Total Tests: 15
======================================================================

[1/15] Testing: Health Check
  Endpoint: GET /health
  Description: Basic health check for load balancers
  ✅ PASSED (HTTP 200, 0.45s)

... (tests continue) ...
```

## Example 6: Integration with GitHub Actions

Use in CI/CD pipeline:

```yaml
# .github/workflows/endpoint-test.yml
name: Endpoint Tests

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  test-endpoints:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install requests
      
      - name: Test Production Endpoints
        run: |
          python3 test_endpoints_full.py ${{ secrets.BACKEND_URL }} \
            --timeout 60 \
            --json > endpoint_results.json
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: endpoint-test-results
          path: endpoint_results.json
      
      - name: Check Results
        run: |
          if [ $? -ne 0 ]; then
            echo "::error::Endpoint tests failed"
            exit 1
          fi
```

## Example 7: Filtering JSON Results

Extract only failed tests:

```bash
$ python3 test_endpoints_full.py --json | jq '.tests[] | select(.result == "FAILED")'

{
  "name": "Full Health Check",
  "method": "GET",
  "endpoint": "/health/full",
  "result": "FAILED",
  "status_code": 500,
  "response_time": 0.015,
  "error": "Expected 200, got 500"
}
```

Get success rate:

```bash
$ python3 test_endpoints_full.py --json | jq '{passed, failed, total: .total_tests, success_rate: ((.passed / .total_tests) * 100)}'

{
  "passed": 8,
  "failed": 7,
  "total": 15,
  "success_rate": 53.333333333333336
}
```

## Example 8: Quick Health Check

Test only critical endpoints by modifying the script or using it as a quick validation:

```bash
# Quick validation - if this succeeds (exit code 0), backend is healthy
$ python3 test_endpoints_full.py && echo "Backend is healthy!"
```

## Use Cases

1. **Development**: Validate backend after code changes
2. **Deployment**: Verify endpoints after deployment
3. **Monitoring**: Regular health checks via cron
4. **CI/CD**: Automated testing in pipelines
5. **Troubleshooting**: Identify failing endpoints quickly
6. **Documentation**: Generate endpoint status reports

## Tips

- Use `--timeout` to adjust for slow networks or cold starts
- Use `--json` for programmatic processing
- Pipe JSON output to monitoring systems
- Run regularly to catch issues early
- Save results for historical tracking
- Compare results over time to identify trends
