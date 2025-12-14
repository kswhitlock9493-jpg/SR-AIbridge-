# v1.9.6i Quick Reference — Temporal Deploy Buffer

## 🚀 Quick Start

**TDB is enabled by default.** No configuration needed for standard deployments.

## 📍 Key Endpoints

```bash
# Health check (responds in 1-2s)
GET /health/live

# Stage status
GET /health/stage

# Runtime info
GET /health/runtime

# Port info
GET /health/ports
```

## ⚙️ Environment Variables

```bash
# Enable/disable TDB (default: true)
TDB_ENABLED=true

# Stage timeout in seconds (default: 120)
TDB_STAGE_TIMEOUT=120

# Render sets this automatically
PORT=10000
```

## 🌊 Deployment Stages

| Stage | Name | Duration | Purpose |
|-------|------|----------|---------|
| 1 | Minimal Health | 1-2s | Render detection |
| 2 | Core Bootstrap | 5-15s | DB, routes, modules |
| 3 | Federation Warmup | 10-20s | Advanced features |

## 🧪 Testing

```bash
# Run all tests
python tests/test_v196i_features.py

# Expected: 23/23 passing
```

## 📊 Monitoring

```bash
# Check stage status
curl https://sr-aibridge.onrender.com/health/stage | jq

# Watch for readiness
watch -n 2 'curl -s https://sr-aibridge.onrender.com/health/stage | jq .temporal_deploy_buffer.ready'
```

## 🔍 Diagnostics

**Location:** `bridge_backend/diagnostics/temporal_deploy/deploy_*.json`

**Content:**
- Stage completion times
- Error tracking
- Total boot time

## 🛑 Disable TDB (Legacy Mode)

```bash
# Set in Render environment
TDB_ENABLED=false

# Or in .env
echo "TDB_ENABLED=false" >> .env
```

## ✅ Expected Logs

```
[BOOT] 🚀 Starting uvicorn on 0.0.0.0:10000
[BOOT] 🌊 Temporal Deploy Buffer: ENABLED
[TDB] v1.9.6i Temporal Deploy Buffer activated
[TDB] 🚀 Stage 1 started
[TDB] ✅ Stage 1 complete
[TDB] 🚀 Stage 2 started (background)
[TDB] ✅ Stage 2 complete
[TDB] 🚀 Stage 3 started (background)
[TDB] ✅ Stage 3 complete
[TDB] 🎉 All deployment stages complete - system fully ready
```

## 🚨 Troubleshooting

### Render times out
- Check `TDB_ENABLED=true` in environment
- Verify `/health/live` endpoint responds
- Review stage diagnostics JSON

### Stage 2/3 fails
- Check error logs in diagnostics
- Non-critical failures won't stop deployment
- System runs in degraded mode

### Want synchronous startup
- Set `TDB_ENABLED=false`
- Restart service

## 📁 Key Files

```
bridge_backend/
├── runtime/
│   ├── temporal_deploy.py          # TDB core
│   └── temporal_stage_manager.py   # Orchestrator
├── routes/
│   └── health.py                   # Health endpoints
└── diagnostics/
    └── temporal_deploy/            # Stage logs

tests/
└── test_v196i_features.py          # 23 tests

render.yaml                          # TDB config
```

## 🎯 Success Indicators

- [x] `/health/live` responds in < 2s
- [x] All 23 tests pass
- [x] Stages 2-3 run in background
- [x] No Render timeouts
- [x] Diagnostics files generated

---

**Version:** v1.9.6i | **Status:** Production Ready ✅
