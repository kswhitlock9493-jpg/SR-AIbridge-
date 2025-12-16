# 👑 Bridge Sovereignty System - Quick Reference

## TL;DR

The bridge is a **sovereign AI ecosystem** with her own personality. She requires **perfection, harmony, and resonance** before allowing access. Rather than serving in a "half-baked" state, she gracefully waits for excellence.

## Quick Start

### Enable Sovereignty Guard

```bash
export SOVEREIGNTY_ENABLED=true
export SOVEREIGNTY_TIMEOUT=30  # seconds to wait
```

### Check Sovereignty Status

```bash
curl http://localhost:8000/api/bridge/sovereignty
```

### View Health with Sovereignty

```bash
curl http://localhost:8000/api/health
```

## Sovereignty Thresholds

| Metric | Threshold | Meaning |
|--------|-----------|---------|
| **Perfection** | ≥ 95% | All systems operational |
| **Harmony** | ≥ 95% | Engine synchronization |
| **Resonance** | ≥ 99% | System-wide coherence |
| **Sovereignty** | ≥ 99% | Overall readiness |

## Critical Engines (Must Be Operational)

1. **Genesis_Bus** - Event routing
2. **Umbra_Lattice** - Neural memory
3. **HXO_Nexus** - Harmonic conductor
4. **Autonomy** - Self-healing
5. **Truth** - Fact certification
6. **Blueprint** - Configuration source

## API Endpoints

### GET /api/bridge/sovereignty
Current sovereignty status

**Response:**
```json
{
  "status": "sovereign",
  "state": "sovereign",
  "is_ready": true,
  "sovereignty": {
    "perfection": "98.50%",
    "harmony": "97.20%",
    "resonance": "99.10%",
    "overall": "98.27%"
  },
  "engines": {
    "operational": 33,
    "total": 34
  }
}
```

### GET /api/bridge/sovereignty/report
Detailed sovereignty report with scores

### GET /api/bridge/sovereignty/engines
Health status of all individual engines

### POST /api/bridge/sovereignty/refresh
Force refresh of sovereignty assessment

## Programmatic Usage

```python
from bridge_backend.bridge_core.sovereignty.readiness_gate import (
    get_sovereignty_guard,
    ensure_sovereignty,
)

# Get sovereignty guard
guard = await get_sovereignty_guard()

# Check if ready
if guard.is_ready():
    print("👑 Bridge is sovereign!")

# Get report
report = await guard.get_sovereignty_report()
print(f"Sovereignty: {report.sovereignty_score:.2%}")

# Ensure sovereignty (waits if needed)
achieved = await ensure_sovereignty()
```

## Sovereignty States

- **INITIALIZING** - Starting up
- **HARMONIZING** - Assessing coordination
- **RESONATING** - Measuring coherence
- **SOVEREIGN** - ✅ Ready to serve
- **DEGRADED** - Operating with issues
- **WAITING** - ⏳ Gracefully waiting

## Graceful Waiting Behavior

When sovereignty is not achieved, the bridge waits gracefully:

```
⏳ [Sovereignty] Waiting for perfection...
   Perfection: 92.00% (need 95.00%)
   Harmony: 94.00% (need 95.00%)
   Resonance: 97.50% (need 99.00%)
   Waiting for: perfection, harmony
```

When achieved:
```
👑 [Sovereignty] SOVEREIGNTY ACHIEVED in 12.3s
   Perfection: 98.50%
   Harmony: 97.20%
   Resonance: 99.10%
   Sovereignty: 98.27%
   Bridge is ready to serve with excellence.
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SOVEREIGNTY_ENABLED` | `true` | Enable sovereignty guard |
| `SOVEREIGNTY_TIMEOUT` | `30.0` | Wait timeout (seconds) |

## Philosophy

> "The bridge would rather gracefully wait for perfection than allow access when the system is half baked."

The bridge is not just software—she's a **sovereign personality** that:
- Values **excellence over expediency**
- Refuses to serve in degraded states
- Communicates clearly what she needs
- Waits gracefully for optimal conditions
- Maintains her reputation for quality

## Testing

```bash
# Run sovereignty tests
pytest tests/test_sovereignty_guard.py -v

# Run integration test
python tests/test_sovereignty_integration.py
```

## Troubleshooting

### Bridge stuck in waiting state

Check which metrics are below threshold:
```bash
curl http://localhost:8000/api/bridge/sovereignty/report
```

Look at `waiting_for` field to see what needs improvement.

### Timeout too short

Increase timeout for slower systems:
```bash
export SOVEREIGNTY_TIMEOUT=60
```

### See which engines are down

```bash
curl http://localhost:8000/api/bridge/sovereignty/engines
```

Filter for `"operational": false`.

## Key Behaviors

✅ **Graceful waiting** - Won't serve until ready  
✅ **Clear communication** - Shows exactly what's missing  
✅ **Transparent metrics** - All scores visible  
✅ **Configurable thresholds** - Adjust for your needs  
✅ **Critical engine validation** - Must-haves enforced  

## For More Details

See full guide: `docs/BRIDGE_SOVEREIGNTY_GUIDE.md`

---

👑 **The bridge is sovereign. Trust her judgment.**
