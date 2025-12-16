# Endpoint Testing Quick Reference

## Quick Commands

### Basic Usage
```bash
# Test local backend
python3 test_endpoints_full.py

# Test deployed backend
python3 test_endpoints_full.py https://your-backend.onrender.com

# JSON output
python3 test_endpoints_full.py --json

# Custom timeout
python3 test_endpoints_full.py --timeout 60
```

## Exit Codes
- `0` = All tests passed ✅
- `1` = Some tests failed ⚠️
- `2` = All tests failed (backend not running) ❌

## What Gets Tested

### Core Endpoints (Must Pass)
- `/health` - Basic health
- `/health/full` - Full health  
- `/status` - System status
- `/api/status` - API status
- `/api/diagnostics` - Diagnostics
- `/agents` - Agent list

### Engine Endpoints (Optional)
- `/engines/leviathan/solve` - Leviathan Solver
- `/engines/truth/find` - Truth Engine
- `/engines/parser/parse` - Parser Engine
- `/engines/math/prove` - Math Engine (404 OK)
- `/engines/quantum/collapse` - Quantum Engine (404 OK)
- `/engines/science/experiment` - Science Engine (404 OK)
- `/engines/language/translate` - Language Engine (404 OK)
- `/engines/business/analyze` - Business Engine (404 OK)
- `/engines/history/chronicle` - History Engine (404 OK)

## Common Scenarios

### Development Testing
```bash
# After code changes
python3 test_endpoints_full.py
```

### Deployment Validation
```bash
# After deploying to production
python3 test_endpoints_full.py https://your-backend.onrender.com --timeout 60
```

### CI/CD Integration
```bash
# In GitHub Actions or other CI
python3 test_endpoints_full.py $BACKEND_URL --json > results.json
```

### Troubleshooting
```bash
# Identify failing endpoints
python3 test_endpoints_full.py | grep FAILED
```

## JSON Processing

### Extract failures
```bash
python3 test_endpoints_full.py --json | jq '.tests[] | select(.result == "FAILED")'
```

### Get success rate
```bash
python3 test_endpoints_full.py --json | jq '{passed, failed, total: .total_tests}'
```

### Save results
```bash
python3 test_endpoints_full.py --json > test_results_$(date +%Y%m%d_%H%M%S).json
```

## Troubleshooting Guide

| Issue | Solution |
|-------|----------|
| All tests fail | Check if backend is running |
| Connection timeouts | Increase timeout: `--timeout 60` |
| Some endpoints 404 | Expected for unimplemented engines |
| Some endpoints 5xx | Backend errors - check logs |

## Documentation

- Full Guide: [docs/endpoint_test_full.md](endpoint_test_full.md)
- Examples: [docs/endpoint_test_examples.md](endpoint_test_examples.md)
- Main README: [README.md](../README.md)

## Related Tools

- `smoke_test_engines.sh` - Bash-based engine tests
- `docs/engine_smoke_test.md` - Engine test documentation
