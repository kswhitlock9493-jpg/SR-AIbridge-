# Umbra Cognitive Stack - Quick Reference

## 🌑 Quick Start

### Enable Umbra
```bash
export UMBRA_ENABLED=true
export UMBRA_MEMORY_ENABLED=true
export UMBRA_ECHO_ENABLED=true
export UMBRA_REFLECT_ON_COMMIT=true
```

---

## 📡 API Endpoints

### Core Operations
```bash
# Detect anomalies
POST /api/umbra/detect
{
  "error_rate": 0.15,
  "response_time": 200,
  "memory_usage": 0.6
}

# Generate and apply repair (Admiral only)
POST /api/umbra/repair
{
  "error_rate": 0.15,
  "response_time": 200
}
```

### Memory Operations
```bash
# Recall experiences
GET /api/umbra/memory?category=repair&limit=10

# Learn patterns
GET /api/umbra/memory/patterns?pattern_type=repair
```

### Predictive Operations
```bash
# Predict issues
POST /api/umbra/predict
{
  "error_rate": 0.08,
  "response_time": 100
}

# Apply preventive repair (Admiral only)
POST /api/umbra/predict/prevent
{
  "error_rate": 0.08
}
```

### Echo Operations (Admiral Only)
```bash
# Capture manual edit
POST /api/umbra/echo/capture
{
  "actor": "Admiral",
  "file": ".github/workflows/deploy.yml",
  "diff": "fix: Update timeout",
  "commit_hash": "abc123"
}

# Observe git commit
POST /api/umbra/echo/observe
{
  "hash": "abc123",
  "author": "Admiral",
  "files": [...]
}
```

### Metrics
```bash
# Get all metrics
GET /api/umbra/metrics

# Get status
GET /api/umbra/status
```

---

## 🧠 Components

| Component | Purpose | Key Feature |
|-----------|---------|-------------|
| **Umbra Core** | Pipeline self-healing | Autonomous anomaly detection & repair |
| **Umbra Memory** | Experience graph | Pattern learning from history |
| **Umbra Predictive** | Pre-repair intelligence | Issue prediction & prevention |
| **Umbra Echo** | Human-guided learning | Captures Admiral actions |

---

## 🔄 Cognitive Lifecycle

```
Observe → Repair → Certify → Record → Reflect → Evolve
   ↑                                              ↓
   └──────────────────────────────────────────────┘
```

1. **Observe** - Umbra Core detects anomaly
2. **Repair** - Umbra Predictive generates fix
3. **Certify** - Truth Engine validates
4. **Record** - Umbra Memory stores experience
5. **Reflect** - Umbra Echo learns from Admiral
6. **Evolve** - Model updates with new patterns

---

## 🔒 RBAC Quick Reference

### Admiral (Full Access)
- ✅ All read operations
- ✅ Apply repairs
- ✅ Capture Echo events
- ✅ Apply preventive repairs

### Captain (Read + Monitor)
- ✅ View memory & patterns
- ✅ View predictions
- ✅ View metrics
- ❌ No write operations

### Observer (Read-Only)
- ✅ View status
- ✅ View metrics
- ❌ No predictions
- ❌ No write operations

---

## 📊 Metrics at a Glance

```json
{
  "umbra_core": {
    "anomalies_detected": 42,
    "repairs_applied": 38,
    "success_rate": 0.95
  },
  "umbra_memory": {
    "total_experiences": 156,
    "certified_count": 156
  },
  "umbra_predictive": {
    "predictions_made": 23,
    "avg_confidence": 0.84
  },
  "umbra_echo": {
    "echo_events": 67,
    "intents": {
      "intent:fix": 34,
      "intent:optimize": 12,
      "intent:feature": 15
    }
  }
}
```

---

## 🎯 Common Tasks

### Detect and Repair an Anomaly
```python
# 1. Detect
anomaly = await core.detect_anomaly(telemetry)

# 2. Generate repair
repair = await core.generate_repair(anomaly)

# 3. Apply
result = await core.apply_repair(repair)
```

### Learn from Past Repairs
```python
# Get all repair experiences
repairs = await memory.recall(category="repair", limit=50)

# Learn patterns
patterns = await memory.learn_pattern("repair")

# Use patterns for prediction
prediction = await predictive.predict_issue(telemetry)
```

### Capture Admiral Actions
```python
# Capture single edit
entry = await echo.capture_edit(change)

# Observe entire commit
entries = await echo.observe_commit(commit_data)

# Sync to HXO
await echo.sync_to_hxo(entry)
```

---

## 📡 Genesis Bus Topics

| Topic | When Published |
|-------|----------------|
| `umbra.anomaly.detected` | Anomaly detected |
| `umbra.pipeline.repaired` | Repair applied |
| `umbra.echo.recorded` | Echo captured |
| `umbra.memory.learned` | Pattern learned |
| `truth.certify.cognitive` | Cognitive data certified |
| `hxo.echo.sync` | HXO sync requested |

---

## 🧪 Testing

```bash
# Run all Umbra tests
pytest bridge_backend/tests/test_umbra_*.py -v

# Run specific component
pytest bridge_backend/tests/test_umbra_core.py -v
pytest bridge_backend/tests/test_umbra_memory.py -v
pytest bridge_backend/tests/test_umbra_echo.py -v
pytest bridge_backend/tests/test_umbra_predictive.py -v
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Anomalies not detected | Check `UMBRA_ENABLED=true` |
| Memory not persisting | Check `vault/umbra/` permissions |
| Echo not capturing | Verify `UMBRA_ECHO_ENABLED=true` |
| Predictions not working | Ensure >10 memory experiences |
| Low confidence | Provide accuracy feedback |

---

## 💾 Storage Paths

- **Memory:** `vault/umbra/umbra_memory.json`
- **Logs:** Genesis Bus + ChronicleLoom

---

## 🎯 Intent Classification

| Intent | Triggers | Example |
|--------|----------|---------|
| `intent:fix` | fix, bug, error | "fix: Resolve auth bug" |
| `intent:optimize` | optim, improve, perf | "optimize: Cache queries" |
| `intent:override` | override, disable, skip | "override: Skip validation" |
| `intent:feature` | feat, add, new | "feat: Add OAuth support" |
| `intent:maintenance` | (default) | "Update dependencies" |

---

## 📋 Watched Paths (Echo)

- `.github/workflows/` - CI/CD configs
- `.env` - Environment configs
- `/config/` - Application configs
- `bridge_backend/bridge_core/engines/` - Engine code

---

## 🚀 Integration Example

```python
from bridge_backend.bridge_core.engines.umbra import (
    UmbraCore, UmbraMemory, UmbraPredictive, UmbraEcho
)

# Initialize
memory = UmbraMemory(truth=truth, chronicle_loom=loom)
core = UmbraCore(memory=memory, truth=truth, genesis_bus=bus)
predictive = UmbraPredictive(memory=memory, core=core)
echo = UmbraEcho(memory=memory, truth=truth, genesis_bus=bus)

# Use
telemetry = {"error_rate": 0.15}
anomaly = await core.detect_anomaly(telemetry)
if anomaly:
    repair = await core.generate_repair(anomaly)
    result = await core.apply_repair(repair)
```

---

## ⚡ Performance Tips

1. **Set appropriate limits** - Use `limit` parameter in memory recall
2. **Monitor confidence** - Adjust threshold based on accuracy
3. **Watch selective paths** - Only monitor critical files
4. **Batch commit observations** - Process multiple changes together
5. **Regular pattern learning** - Run daily or weekly

---

## 📚 Resources

- **Full Documentation:** `UMBRA_README.md`
- **API Docs:** `/api/docs`
- **Tests:** `bridge_backend/tests/test_umbra_*.py`
- **Changelog:** `CHANGELOG.md` (v1.9.7d)

---

**Version:** v1.9.7d  
**Status:** ✅ Production Ready  
**Support:** Admiral-tier feature
