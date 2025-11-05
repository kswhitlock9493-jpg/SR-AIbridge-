# Umbra Cognitive Stack — Complete Documentation

## 🌑 Overview

**Project Umbra Ascendant** transforms the SR-AIbridge into a self-aware, experience-driven orchestration intelligence. Umbra integrates Autonomous Repair, Predictive Learning, and Admiral Echo Reflection into one continuous cognition loop.

**Version:** v1.9.7d  
**Status:** Production Ready  
**Author:** Copilot with Admiral

---

## 🧠 The Cognitive Architecture

```
┌──────────────────────────────────────────────────────────┐
│                 PROJECT UMBRA ASCENDANT                 │
│  (Self-Healing • Self-Learning • Self-Reflective)       │
├──────────────────────────────────────────────────────────┤
│ Umbra Core         → Pipeline Self-Healing               │
│ Umbra Memory       → Experience Graph & Recall           │
│ Umbra Predictive   → Confidence-Based Pre-Repair         │
│ Umbra Echo         → Human-Informed Adaptive Learning    │
│ Truth Engine       → Certification of all cognitive data │
│ ChronicleLoom      → Immutable memory persistence        │
└──────────────────────────────────────────────────────────┘
```

---

## 🔧 Component Details

### Umbra Core - Pipeline Self-Healing

**Purpose:** Observes system telemetry and autonomously detects and repairs anomalies.

**Key Features:**
- Real-time anomaly detection from telemetry
- Automatic repair plan generation
- Confidence-based repair execution
- Truth Engine certification
- Genesis Bus event publishing

**Anomaly Types:**
- High error rate (>10%)
- High latency (>5000ms)
- High memory usage (>90%)

**Example Usage:**
```python
from bridge_backend.bridge_core.engines.umbra import UmbraCore

core = UmbraCore(memory=memory, truth=truth, genesis_bus=bus)

# Detect anomaly
telemetry = {"error_rate": 0.15, "response_time": 200}
anomaly = await core.detect_anomaly(telemetry)

# Generate and apply repair
if anomaly:
    repair = await core.generate_repair(anomaly)
    result = await core.apply_repair(repair)
```

---

### Umbra Memory - Experience Graph & Recall

**Purpose:** Stores and recalls repair experiences, learns patterns from history.

**Key Features:**
- Persistent memory storage (`vault/umbra/umbra_memory.json`)
- Experience categorization (repair, anomaly, echo, prediction_feedback)
- Pattern learning and analysis
- ChronicleLoom integration for audit trail
- Truth Engine certification

**Memory Structure:**
```json
{
  "id": "exp_123_1697123456789",
  "timestamp": "2025-10-12T19:30:00Z",
  "category": "repair",
  "data": {
    "anomaly_id": "high_error_rate",
    "actions": [...],
    "confidence": 0.85
  },
  "result": {
    "success": true,
    "actions_applied": [...]
  },
  "certified": true,
  "signature": "sha256:abc..."
}
```

**Example Usage:**
```python
from bridge_backend.bridge_core.engines.umbra import UmbraMemory

memory = UmbraMemory(truth=truth, chronicle_loom=loom)

# Record experience
entry = await memory.record("repair", repair_data, result)

# Recall experiences
repairs = await memory.recall(category="repair", limit=10)

# Learn patterns
patterns = await memory.learn_pattern("repair")
```

---

### Umbra Predictive - Confidence-Based Pre-Repair

**Purpose:** Uses learned patterns to predict and prevent issues before they occur.

**Key Features:**
- Pattern-based issue prediction
- Confidence threshold filtering (default: 0.7)
- Preventive repair execution
- Self-adjusting confidence model
- Integration with Umbra Core and Memory

**Prediction Flow:**
1. Analyze current telemetry
2. Compare against learned patterns
3. Calculate prediction confidence
4. Generate preventive repair if confidence > threshold
5. Apply repair through Umbra Core

**Example Usage:**
```python
from bridge_backend.bridge_core.engines.umbra import UmbraPredictive

predictive = UmbraPredictive(memory=memory, core=core)

# Predict issue
telemetry = {"error_rate": 0.08}  # Trending but not critical
prediction = await predictive.predict_issue(telemetry)

# Apply preventive repair
if prediction:
    result = await predictive.apply_preventive_repair(prediction)

# Update model with feedback
feedback = {"accuracy": 0.92, "prediction": "high_error_rate"}
await predictive.update_model(feedback)
```

---

### Umbra Echo - Human-Informed Adaptive Learning

**Purpose:** Observes manual edits and Admiral actions, mirrors them into the experience graph.

**Key Features:**
- File system monitor for watched paths
- Intent classification (fix, optimize, override, feature, maintenance)
- Subsystem detection (ci_cd, configuration, engines, api, tests)
- Git commit observation
- HXO synchronization for schema regeneration
- Truth Engine certification

**Watched Paths:**
- `.github/workflows/`
- `.env`
- `/config/`
- `bridge_backend/bridge_core/engines/`

**Intent Classification:**
- `intent:fix` - Bug fixes, error corrections
- `intent:optimize` - Performance improvements
- `intent:override` - Configuration overrides, disables
- `intent:feature` - New features, additions
- `intent:maintenance` - General maintenance

**Example Usage:**
```python
from bridge_backend.bridge_core.engines.umbra import UmbraEcho

echo = UmbraEcho(memory=memory, truth=truth, genesis_bus=bus)

# Capture manual edit
change = {
    "actor": "Admiral",
    "file": ".github/workflows/deploy.yml",
    "diff": "fix: Update deployment timeout",
    "commit_hash": "abc123"
}
entry = await echo.capture_edit(change)

# Observe git commit
commit_data = {
    "hash": "abc123def456",
    "author": "Admiral",
    "files": [...]
}
entries = await echo.observe_commit(commit_data)
```

---

## 🔄 Full Cognitive Lifecycle

| Phase | Actor | Description | Output |
|-------|-------|-------------|--------|
| **Observe** | Umbra Core | Detects anomalies from telemetry | Anomaly data |
| **Repair** | Umbra Predictive | Generates & applies autonomous fix | Repair result |
| **Certify** | Truth Engine | Validates fix & publishes Genesis event | Certification |
| **Record** | Umbra Memory | Stores sequence in ChronicleLoom | Memory entry |
| **Reflect** | Umbra Echo | Learns from Admiral's manual actions | Echo entry |
| **Evolve** | Umbra Core | Integrates new patterns into predictive model | Updated model |

---

## 📡 Genesis Bus Integration

### Published Topics

#### `umbra.anomaly.detected`
**When:** Umbra Core detects an anomaly  
**Payload:**
```json
{
  "timestamp": "2025-10-12T19:30:00Z",
  "type": "high_error_rate",
  "severity": "high",
  "message": "Error rate 15.0% exceeds threshold",
  "detected_by": "umbra_core"
}
```

#### `umbra.pipeline.repaired`
**When:** A repair is successfully applied  
**Payload:**
```json
{
  "timestamp": "2025-10-12T19:30:05Z",
  "repair_id": "high_error_rate",
  "success": true,
  "actions_applied": [...],
  "certified": true,
  "signature": "sha256:..."
}
```

#### `umbra.echo.recorded`
**When:** Echo captures an Admiral action  
**Payload:**
```json
{
  "actor": "Admiral",
  "timestamp": "2025-10-12T19:30:10Z",
  "file": ".github/workflows/deploy.yml",
  "intent": "intent:fix",
  "certified": true
}
```

#### `umbra.memory.learned`
**When:** Memory patterns are updated  
**Payload:**
```json
{
  "timestamp": "2025-10-12T19:30:15Z",
  "commit": "abc123def456",
  "changes_learned": 3,
  "actor": "Admiral"
}
```

---

## 🔒 Security & RBAC

### Admiral Only (Write Operations)
- `/api/umbra/repair` - Apply repairs
- `/api/umbra/predict/prevent` - Apply preventive repairs
- `/api/umbra/echo/capture` - Capture manual edits
- `/api/umbra/echo/observe` - Observe commits

### Captain (Read + Monitor)
- `/api/umbra/memory` - View experiences
- `/api/umbra/memory/patterns` - View learned patterns
- `/api/umbra/predict` - View predictions
- `/api/umbra/metrics` - View metrics

### Observer (Read-Only)
- `/api/umbra/status` - View engine status
- `/api/umbra/metrics` - View metrics

**Security Guarantees:**
- All memory entries certified by Truth Engine
- All echo events certified by Truth Engine
- Immutable audit trail in ChronicleLoom
- RBAC enforcement via permissions middleware
- Genesis Bus event verification

---

## 🧪 Testing

### Test Coverage
- **40+ test cases** across 4 test files
- 100% core functionality coverage
- Integration tests with Truth Engine and ChronicleLoom
- RBAC enforcement validation

### Running Tests
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

## ⚙️ Configuration

### Environment Variables

```bash
# Enable Umbra self-healing intelligence
UMBRA_ENABLED=true

# Enable Umbra Memory (experience graph & recall)
UMBRA_MEMORY_ENABLED=true

# Enable Umbra Echo (human-informed learning)
UMBRA_ECHO_ENABLED=true

# Training interval for predictive model updates
UMBRA_TRAIN_INTERVAL=15m

# Enable reflection on git commits
UMBRA_REFLECT_ON_COMMIT=true
```

### Storage Paths
- **Memory:** `vault/umbra/umbra_memory.json`
- **Logs:** Published to Genesis Bus and ChronicleLoom

---

## 📊 Metrics & Monitoring

### Umbra Core Metrics
```json
{
  "enabled": true,
  "anomalies_detected": 42,
  "repairs_applied": 38,
  "success_rate": 0.95
}
```

### Umbra Memory Metrics
```json
{
  "enabled": true,
  "total_experiences": 156,
  "categories": {
    "repair": 38,
    "anomaly": 42,
    "echo": 67,
    "prediction_feedback": 9
  },
  "certified_count": 156
}
```

### Umbra Predictive Metrics
```json
{
  "enabled": true,
  "predictions_made": 23,
  "confidence_threshold": 0.72,
  "avg_confidence": 0.84
}
```

### Umbra Echo Metrics
```json
{
  "enabled": true,
  "echo_events": 67,
  "intents": {
    "intent:fix": 34,
    "intent:optimize": 12,
    "intent:feature": 15,
    "intent:maintenance": 6
  },
  "watched_paths": 4
}
```

---

## 🚀 Deployment

### Prerequisites
- Python 3.12+
- FastAPI application
- Truth Engine enabled
- Genesis Bus configured
- ChronicleLoom available

### Integration Steps

1. **Enable Umbra in environment:**
```bash
export UMBRA_ENABLED=true
export UMBRA_MEMORY_ENABLED=true
export UMBRA_ECHO_ENABLED=true
```

2. **Mount Umbra routes in FastAPI:**
```python
from bridge_backend.bridge_core.engines.umbra.routes import router as umbra_router

app.include_router(umbra_router, prefix="/api")
```

3. **Initialize engines on startup:**
```python
from bridge_backend.bridge_core.engines.umbra import (
    UmbraCore, UmbraMemory, UmbraPredictive, UmbraEcho
)

@app.on_event("startup")
async def startup():
    # Initialize Umbra stack
    memory = UmbraMemory(truth=truth, chronicle_loom=loom)
    core = UmbraCore(memory=memory, truth=truth, genesis_bus=bus)
    predictive = UmbraPredictive(memory=memory, core=core)
    echo = UmbraEcho(memory=memory, truth=truth, genesis_bus=bus)
```

4. **Verify deployment:**
```bash
curl https://your-bridge.onrender.com/api/umbra/status
```

---

## 💡 Best Practices

### For Admirals
- Review Echo-captured changes regularly
- Provide feedback on prediction accuracy
- Monitor repair success rates
- Adjust confidence thresholds as needed

### For Captains
- Monitor memory patterns for insights
- Track prediction trends
- Review anomaly detection accuracy
- Report unusual patterns to Admiral

### For Developers
- Test anomaly scenarios thoroughly
- Validate repair actions before deployment
- Monitor Genesis Bus events
- Keep watched paths updated

---

## 🔧 Troubleshooting

### Umbra Not Detecting Anomalies
- Check `UMBRA_ENABLED=true` in environment
- Verify telemetry data format
- Review anomaly thresholds in `core.py`

### Memory Not Persisting
- Check `vault/umbra/` directory permissions
- Verify `UMBRA_MEMORY_ENABLED=true`
- Review `umbra_memory.json` for errors

### Echo Not Capturing Changes
- Check `UMBRA_ECHO_ENABLED=true`
- Verify watched paths configuration
- Ensure files match watched patterns

### Predictions Not Working
- Ensure sufficient memory experiences (>10)
- Check confidence threshold setting
- Review pattern learning results

---

## 📚 Additional Resources

- **CHANGELOG.md** - Version history and release notes
- **UMBRA_QUICK_REF.md** - Quick reference guide
- **API Documentation** - `/api/docs` endpoint
- **Test Suite** - `bridge_backend/tests/test_umbra_*.py`

---

## 🎯 Future Enhancements

- **Steward Visualization** - Echo Weave mode in Neural Weave dashboard
- **Multi-Model Learning** - Support for multiple predictive models
- **Advanced Pattern Detection** - Deep learning for pattern recognition
- **Distributed Memory** - Federated memory across Bridge nodes
- **Real-time Dashboard** - Live cognitive metrics visualization

---

**Status:** ✅ Production Ready  
**Version:** v1.9.7d  
**Compatibility:** Python 3.12+, FastAPI  
**Dependencies:** Truth Engine, Genesis Bus, ChronicleLoom  
**Security:** RBAC enforced, Truth certified, Audit logged
