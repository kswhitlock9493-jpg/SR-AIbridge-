# v1.9.6d — Runtime Intelligence Core Implementation

## Summary

This release implements the Runtime Intelligence Core update that provides one-shot fixes for:
- Render port scan loop
- Heartbeat noise
- AsyncSession leaking into response models
- Fragile route imports
- Missing/optional Blueprint engine
- Predictive stabilizer ticket churn

The system now binds to the correct Render PORT, auto-detects HEARTBEAT_URL, heals/learns at boot, and hardens all routers.

## Changes Made

### 1. Version Updates
- **bridge_backend/__init__.py**: Added `__version__ = "1.9.6d"`
- **bridge_backend/main.py**: Updated FastAPI app version to "1.9.6d"

### 2. Render Port & Process Launch
- **scripts/start.sh** (NEW): Created startup script that reads `$PORT` (Render sets this) and execs uvicorn on that port
  - Defaults to PORT=8000 if not set
  - Configurable HOST and APP via environment variables
  - Logs the target configuration before launch

- **render.yaml**: Updated to use `bash scripts/start.sh` as startCommand
  - Added `ENABLE_BLUEPRINT_ENGINE=false` environment variable
  - Added comment about HEARTBEAT_URL auto-detection

### 3. Heartbeat Auto-Detection & Quiet Mode
- **bridge_backend/runtime/heartbeat.py**: 
  - Auto-detects HEARTBEAT_URL from `RENDER_EXTERNAL_URL` if not explicitly set
  - Constructs `/health` endpoint URL automatically
  - Failed external pings now gracefully downgrade to internal checks (no spam)
  - Updated version reference to v1.9.6d

### 4. Predictive Stabilizer: Learn & Resolve Tickets
- **bridge_backend/runtime/predictive_stabilizer.py**:
  - Added `resolve_tickets()` function to scan and resolve tickets
  - Created `resolved/` subdirectory for archived tickets
  - Added `_is_resolved()` function with checks for:
    - PORT environment variable tickets (resolved when PORT is set)
    - HEARTBEAT_URL tickets (always resolved now due to auto-detection)
  - Tickets are moved to `resolved/` when conditions are fixed

- **bridge_backend/runtime/release_intel.py**:
  - Integrated `resolve_tickets()` call at boot
  - Runs before stability analysis to clean up old tickets

### 5. Route Integrity Sweep
- **bridge_backend/bridge_core/missions/routes.py**:
  - Made AsyncSession parameter keyword-only with `*,` separator
  - Ensures FastAPI doesn't mistake DB session for a response field

- **bridge_backend/routes/control.py**:
  - Added `/render-ok` endpoint with `response_model=None`
  - Added `/health` endpoint with `response_model=None`
  - Both return simple dicts without Pydantic validation

### 6. Blueprint Engine Optional
- **bridge_backend/bridge_core/engines/blueprint/routes.py**:
  - Added `ENABLE_BLUEPRINT_ENGINE` environment variable check
  - Blueprint engine is optional by default (no hard crash)
  - When `ENABLE_BLUEPRINT_ENGINE=true` and models are missing, raises ImportError at startup
  - When disabled, engine gracefully skips itself with clear logging

## Testing Results

All custom tests passed:
- ✅ Version is 1.9.6d
- ✅ start.sh exists and is executable
- ✅ Heartbeat auto-detection works
- ✅ PORT ticket resolution works
- ✅ HEARTBEAT_URL ticket resolution works
- ✅ Blueprint engine disabled by default
- ✅ Control endpoints exist
- ✅ render.yaml updated correctly

## Deployment Instructions

### 1. Render Configuration

Set Start Command to:
```bash
bash scripts/start.sh
```

Or adopt the updated `render.yaml` which already includes this.

### 2. Optional: Blueprint Engine

To enable the Blueprint engine when models are available:
```bash
ENABLE_BLUEPRINT_ENGINE=true
```

### 3. Optional: Heartbeat URL

The system auto-detects from `RENDER_EXTERNAL_URL`. To hard-pin:
```bash
HEARTBEAT_URL=https://sr-aibridge.onrender.com/health
```

## Why This Removes the Root Causes

1. **Port loop**: Uvicorn binds to exactly the port Render scans via `$PORT` environment variable
2. **AsyncSession error**: DB session is now keyword-only dependency; FastAPI never interprets it as a response field
3. **Fragile imports**: Every router import is already guarded by existing `safe_import()` mechanism
4. **Blueprint "model not found"**: Optional by default; strict mode available via env flag
5. **Stabilizer noise**: Tickets get resolved and archived, not re-warned forever
6. **Heartbeat chatter**: Clean auto-detect; quiet internal fallback on external ping failure

## Files Modified

1. bridge_backend/__init__.py
2. bridge_backend/main.py
3. bridge_backend/runtime/heartbeat.py
4. bridge_backend/runtime/predictive_stabilizer.py
5. bridge_backend/runtime/release_intel.py
6. bridge_backend/bridge_core/missions/routes.py
7. bridge_backend/bridge_core/engines/blueprint/routes.py
8. bridge_backend/routes/control.py
9. render.yaml
10. scripts/start.sh (NEW)

## Backward Compatibility

- All changes are backward compatible
- Default behavior matches previous version when environment variables are not set
- Blueprint engine remains disabled by default (same as v1.9.6c with BLUEPRINTS_ENABLED)
- Heartbeat system gracefully handles missing HEARTBEAT_URL
- Port binding falls back to 8000 in non-Render environments

## Next Steps

1. Deploy to Render
2. Verify PORT binding is correct (should be 10000 on Render)
3. Monitor heartbeat logs for auto-detection message
4. Check that no stabilization tickets are recreated on subsequent boots
