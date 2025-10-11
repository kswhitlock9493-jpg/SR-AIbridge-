# v1.9.6e — Heartbeat Compliance & Method Guard (Final Build)

## Overview
This release eliminates the 405 Method Not Allowed loop, finalizes Render port alignment, and permanently stabilizes the Bridge heartbeat and diagnostics stack.

## Key Changes

### 1. Intelligent Heartbeat (`bridge_backend/runtime/heartbeat.py`)
- **Default method: GET** (FastAPI best practice for `/health`)
- **Auto-switches on 405** using Allow header, then caches preferred method
- **Quiet retry** with exponential backoff + jitter (no loop spam)
- **Environment overrides:**
  - `HEARTBEAT_ENABLED=true` (default: true)
  - `HEARTBEAT_URL=https://sr-aibridge.onrender.com/health` (auto-detects from `RENDER_EXTERNAL_URL`)
  - `HEARTBEAT_METHOD=GET` (optional override, default: auto-detect)
  - `HEARTBEAT_INTERVAL_SECONDS=30` (default: 30)
  - `HEARTBEAT_TIMEOUT_SECONDS=5` (default: 5)

### 2. Health Route Duality (`bridge_backend/routes/control.py`)
- Added POST support for full compatibility with external pingers, Render's checks, and future Netlify/Cloudflare integrations
- Endpoint: `/api/control/health` now supports both GET and POST methods

### 3. Predictive Stabilizer Pattern Detection (`bridge_backend/runtime/predictive_stabilizer.py`)
- Automatically resolves tickets mentioning "405" or "Method Not Allowed"
- Recognizes that v1.9.6e heartbeat self-corrects method mismatches

### 4. Render Port Auto-Bind (`bridge_backend/__main__.py`)
- New entrypoint that always respects `$PORT` environment variable
- Can be started with: `python -m bridge_backend` or via existing `start.sh`

## Testing

All components have been verified:
- ✅ Heartbeat configuration (ENABLED, INTERVAL, TIMEOUT)
- ✅ Method auto-detection (GET/POST/HEAD)
- ✅ 405 recovery via Allow header parsing
- ✅ Backoff + jitter retry logic
- ✅ Stabilizer pattern detection for 405 errors
- ✅ Health endpoint dual-mode (GET/POST)

## Outcome

| Component | Status |
|-----------|--------|
| Heartbeat Method | ✅ Self-corrects (GET/POST/HEAD) |
| Health Route | ✅ Dual-mode (GET/POST) |
| Render Port Scan | ✅ Eliminated |
| Predictive Stabilizer | ✅ Learns & resolves automatically |
| Log Noise | ✅ Reduced |
| Recursive Loops | 🚫 Permanently prevented |

## Migration Notes

No breaking changes. All existing deployments will automatically benefit from:
- Smarter heartbeat method detection
- Better 405 error handling
- Automatic ticket resolution for method mismatch issues

## Start Commands

Any of these work:
```bash
python -m bridge_backend
# or
bash start.sh
# or
uvicorn bridge_backend.main:app --host 0.0.0.0 --port $PORT
```
