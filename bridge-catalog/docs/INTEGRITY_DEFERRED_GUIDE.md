# Integrity Deferred Guide

**Version:** v1.9.7q  
**Module:** `bridge_backend/bridge_core/integrity/deferred.py`  
**Purpose:** Prevent race conditions in integrity validation through deferred execution

---

## Problem Statement

Traditional integrity checks run immediately at boot, which can cause failures when:

1. **Engines not yet initialized** - Validators run before dependencies are ready
2. **Genesis bus not connected** - Cross-engine checks fail due to incomplete linkage
3. **Reflex tokens not loaded** - Authentication fails before token injection completes
4. **Race conditions** - Validators compete with startup tasks

These lead to spurious failures in CI/CD pipelines and deployment environments.

---

## Solution: Deferred Integrity

The deferred integrity module delays validation until after engine initialization completes.

### Key Concept

Instead of:
```
Boot → Run Integrity → Initialize Engines → Start App
```

We do:
```
Boot → Initialize Engines → Defer → Run Integrity → Start App
```

---

## How It Works

### Function: `delayed_integrity_check(run_integrity_callable)`

**Parameters:**
- `run_integrity_callable` - Function that performs integrity checks

**Behavior:**
1. Log the deferral with configured delay
2. Sleep for `INTEGRITY_DEFER_SECONDS` (default: 3 seconds)
3. Call the integrity check function
4. Return the result

**Example:**
```python
from bridge_backend.bridge_core.integrity.deferred import delayed_integrity_check
from bridge_backend.bridge_core.integrity.core import run_integrity

# This will wait 3 seconds, then run integrity checks
result = delayed_integrity_check(run_integrity)
```

**Console Output:**
```
🧪 Integrity: deferring integrity check for 3.0s…
✅ Integrity: Core integrity check completed
```

---

## Configuration

### Environment Variable

```bash
# Delay before running integrity checks (seconds)
INTEGRITY_DEFER_SECONDS=3
```

### Recommended Values

| Environment | Delay | Reason |
|-------------|-------|--------|
| Local Development | 2 | Fast iteration |
| CI/CD | 3 | Standard reliability |
| Production (simple) | 3 | Standard reliability |
| Production (complex) | 5-10 | Many engines/dependencies |

---

## Integration

### In Application Boot (main.py)

```python
from bridge_backend.bridge_core.integrity.deferred import delayed_integrity_check
from bridge_backend.bridge_core.integrity.core import run_integrity

# After all engines initialize...
delayed_integrity_check(run_integrity)
```

### In CI/CD (GitHub Actions)

```yaml
- name: 🔧 Deferred Integrity
  run: |
    python - <<'PY'
    from bridge_backend.bridge_core.integrity.deferred import delayed_integrity_check
    def check():
        print("integrity: OK")
        return {"status": "ok"}
    delayed_integrity_check(check)
    PY
```

---

## Boot Sequence

The Sanctum Cascade Protocol enforces this order:

```
1. Environment Detection
2. Netlify Guard (path + token)
3. Reflex Auth Forge
4. Umbra⇄Genesis Link (with retry)
5. Deferred Integrity ← HERE
6. FastAPI App Start
```

This ensures all dependencies are ready before validation runs.

---

## Timing Tuning

### Too Short (< 2 seconds)

**Symptoms:**
- Genesis bus connection failures
- "Module not initialized" errors
- Sporadic CI failures

**Solution:** Increase to 3-5 seconds

### Too Long (> 10 seconds)

**Symptoms:**
- Slow boot times
- Delayed feedback in CI
- User-visible startup lag

**Solution:** Decrease to 3-5 seconds, or optimize engine initialization

### Just Right (3-5 seconds)

**Characteristics:**
- Consistent CI passes
- Fast enough for user experience
- Reliable engine initialization
- No race conditions

---

## Custom Integrity Checks

You can pass any callable to `delayed_integrity_check`:

### Example 1: Simple Check

```python
def my_check():
    print("Running custom check...")
    return {"ok": True}

delayed_integrity_check(my_check)
```

### Example 2: Complex Validation

```python
async def validate_engines():
    from bridge_backend.genesis.bus import bus
    from bridge_backend.engines.umbra import core
    
    # Check Genesis bus
    if not bus.is_connected():
        raise RuntimeError("Genesis bus not connected")
    
    # Check Umbra
    if not core.is_ready():
        raise RuntimeError("Umbra not ready")
    
    return {"status": "ok", "engines": ["genesis", "umbra"]}

delayed_integrity_check(validate_engines)
```

### Example 3: Conditional Checks

```python
import os

def conditional_check():
    checks = []
    
    if os.getenv("GENESIS_MODE") == "enabled":
        checks.append("genesis")
    
    if os.getenv("UMBRA_ENABLED") == "true":
        checks.append("umbra")
    
    return {"enabled_checks": checks}

delayed_integrity_check(conditional_check)
```

---

## Testing

### Unit Test

```python
import time
from bridge_backend.bridge_core.integrity.deferred import delayed_integrity_check

def test_deferred_check():
    start = time.time()
    
    def dummy():
        return {"ok": True}
    
    result = delayed_integrity_check(dummy)
    elapsed = time.time() - start
    
    assert result["ok"] is True
    assert elapsed >= 3.0  # Should wait at least 3 seconds
```

### Integration Test

```python
import os
from bridge_backend.bridge_core.integrity.deferred import delayed_integrity_check

def test_env_override():
    os.environ["INTEGRITY_DEFER_SECONDS"] = "1"
    
    start = time.time()
    delayed_integrity_check(lambda: None)
    elapsed = time.time() - start
    
    assert elapsed >= 1.0 and elapsed < 2.0
```

---

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from bridge_backend.bridge_core.integrity.deferred import delayed_integrity_check
delayed_integrity_check(run_integrity)
```

### Disable Deferral (Development)

```bash
# Set to 0 to run immediately
export INTEGRITY_DEFER_SECONDS=0
```

### Verbose Checks

```python
def verbose_check():
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("Starting integrity checks...")
    # ... checks ...
    logger.info("Integrity checks complete")
    
    return {"status": "ok"}

delayed_integrity_check(verbose_check)
```

---

## Best Practices

1. **Always defer** - Never run integrity checks synchronously at boot
2. **Tune per environment** - Different delays for dev/CI/prod
3. **Log clearly** - Make deferral visible in logs
4. **Handle failures gracefully** - Don't crash on integrity check failures
5. **Monitor timing** - Track actual vs. expected delay

---

## Troubleshooting

### Issue: Checks still fail after deferral

**Cause:** Delay too short for your environment  
**Solution:** Increase `INTEGRITY_DEFER_SECONDS` to 5-10

### Issue: Slow boot times

**Cause:** Delay too long  
**Solution:** Decrease `INTEGRITY_DEFER_SECONDS` to 2-3

### Issue: Checks timeout

**Cause:** Integrity check function hangs  
**Solution:** Add timeout to your check function

### Issue: No deferral happening

**Cause:** Module not imported or environment variable not set  
**Solution:** Verify import and check `INTEGRITY_DEFER_SECONDS` value

---

**Version:** v1.9.7q  
**Status:** ✅ Production Ready  
**Scope:** Race-free integrity validation timing
