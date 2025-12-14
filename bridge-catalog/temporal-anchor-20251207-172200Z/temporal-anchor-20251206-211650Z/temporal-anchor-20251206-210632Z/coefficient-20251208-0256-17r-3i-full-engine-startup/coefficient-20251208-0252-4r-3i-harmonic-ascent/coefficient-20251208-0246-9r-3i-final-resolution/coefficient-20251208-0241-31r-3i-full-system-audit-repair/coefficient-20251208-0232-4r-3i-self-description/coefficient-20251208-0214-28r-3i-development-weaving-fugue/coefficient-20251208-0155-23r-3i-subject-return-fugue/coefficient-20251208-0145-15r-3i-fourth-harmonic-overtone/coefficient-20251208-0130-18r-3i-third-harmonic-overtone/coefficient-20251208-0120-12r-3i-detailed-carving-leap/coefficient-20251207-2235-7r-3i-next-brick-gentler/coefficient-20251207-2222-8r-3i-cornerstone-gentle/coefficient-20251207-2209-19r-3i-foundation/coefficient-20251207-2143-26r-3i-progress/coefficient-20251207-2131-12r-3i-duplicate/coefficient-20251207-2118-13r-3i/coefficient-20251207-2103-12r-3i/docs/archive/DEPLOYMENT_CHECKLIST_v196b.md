# v1.9.6b Deployment Checklist

## 🚀 SR-AIbridge v1.9.6b — Route Integrity Sweep, Auto-Healing Runtime & Deployment Guard

This document provides deployment instructions for v1.9.6b across all environments.

---

## ✅ Pre-Deployment Verification

Before deploying, ensure all checks pass:

```bash
# 1. Run route sweep validator
python tools/route_sweep_check.py

# 2. Run tests
pytest -q

# 3. Lint check
flake8 bridge_backend --ignore=E501,W503 --exclude=bridge_backend/tests

# 4. Verify imports
python bridge_backend/tests/test_imports.py
python bridge_backend/tests/test_route_sweep.py
```

All commands should exit with code 0 (success).

---

## 🔹 Render (Backend) Deployment

### Configuration

| Setting | Value |
|---------|-------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn bridge_backend.main:app --host 0.0.0.0 --port $PORT` |
| **Health Check** | `/ping` → `{ "ok": true }` |
| **Python Version** | 3.11.9 |

### Environment Variables

**Required:**
- `DATABASE_URL` - PostgreSQL connection string (async driver: `postgresql+asyncpg://...`)
- `PORT` - Auto-set by Render (typically 10000)
- `ENVIRONMENT` - `production`

**Optional (with defaults):**
- `APP_VERSION` - `v1.9.6b`
- `LOG_LEVEL` - `info`
- `HEARTBEAT_URL` - External heartbeat endpoint (optional)
- `HEARTBEAT_INTERVAL_SEC` - `25` (seconds)
- `ALLOWED_ORIGINS` - Comma-separated CORS origins
- `CORS_ALLOW_ALL` - `false`
- `BRIDGE_NODE` - `render-primary`

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Render Auto-Deploy**
   - Render automatically deploys from `main` branch
   - Build takes ~2-3 minutes
   - Port binding: Render sets `$PORT` automatically (usually 10000)

3. **Verify Health**
   ```bash
   curl https://sr-aibridge.onrender.com/ping
   # Should return: {"ok": true, "version": "v1.9.6b"}
   ```

4. **Check Startup Logs**
   - Look for: `[MIDDLEWARE] Header sync enabled`
   - Look for: `[DB Bootstrap] ✅ Schema auto-sync complete`
   - Look for: `[HEART] heartbeat started`

---

## 🔹 Netlify (Frontend) Deployment

### Configuration

1. **Add Environment Variable**
   ```
   VITE_API_URL=https://sr-aibridge.onrender.com
   ```

2. **Ensure CORS Matches**
   - Netlify origin should be in Render's `ALLOWED_ORIGINS`
   - Default: `https://sr-aibridge.netlify.app`

3. **Redeploy**
   ```bash
   # Trigger redeploy from Netlify dashboard or:
   git push origin main
   ```

4. **Handshake Auto-Validates**
   - Frontend calls `/api/health` on mount
   - Headers are synchronized via `HeaderSyncMiddleware`
   - CORS errors should not occur

---

## 🔹 GitHub Actions CI/CD

### Workflow: Bridge Integrity CI

**File:** `.github/workflows/bridge-ci.yml`

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

**Steps:**
1. ✅ Install dependencies
2. ✅ Run route sweep validator (`tools/route_sweep_check.py`)
3. ✅ Run tests (`pytest`)
4. ✅ Lint check (`flake8`)
5. ✅ Success confirmation

**Configuration:**
```yaml
env:
  DATABASE_URL: postgresql+asyncpg://user:pass@localhost/db
  NETLIFY_ORIGIN: "*"
```

### CI Failure Scenarios

**Route Sweep Check Fails:**
```
❌ Route Sweep Check Failed:
  [bridge_backend/core/routes.py] Direct AsyncSession param on line 47
```

**Fix:**
```python
# ❌ Before (unsafe)
async def my_route(db: AsyncSession):
    ...

# ✅ After (safe)
from typing import Annotated
from fastapi import Depends
from bridge_backend.bridge_core.db.db_manager import get_db_session

DbDep = Annotated[AsyncSession, Depends(get_db_session)]

async def my_route(db: DbDep):
    ...
```

---

## 🧩 New Components in v1.9.6b

### 1. Database Bootstrap (`bridge_backend/db/bootstrap.py`)

**Function:** `auto_sync_schema()`
- Auto-creates database tables if missing
- Safe to call on every startup
- Non-fatal if it fails

**Integration:**
```python
from bridge_backend.db.bootstrap import auto_sync_schema
await auto_sync_schema()
```

### 2. Header Sync Middleware (`bridge_backend/middleware/headers.py`)

**Class:** `HeaderSyncMiddleware`
- Adds `X-Bridge-Node` and `X-Bridge-Version` headers
- Standardizes `Cache-Control` for API responses
- Ensures CORS consistency across environments

**Integration:**
```python
from bridge_backend.middleware.headers import HeaderSyncMiddleware
app.add_middleware(HeaderSyncMiddleware)
```

### 3. Route Sweep Check (`tools/route_sweep_check.py`)

**Purpose:** CI validator for route integrity
- Scans all `routes*.py` files
- Detects unsafe AsyncSession usage
- Fails build if violations found

**Usage:**
```bash
python tools/route_sweep_check.py
```

**Output:**
```
✅ All routes comply with Bridge standards.
   - No direct AsyncSession exposure detected
   - Dependency injection patterns are correct
```

### 4. GitHub Actions Workflow (`.github/workflows/bridge-ci.yml`)

**Purpose:** Continuous integration pipeline
- Runs on push/PR to `main` or `develop`
- Executes: route sweep, tests, linting
- Blocks merge if checks fail

---

## 🔧 Troubleshooting

### Port Binding Issues

**Symptom:** Render shows "Port scan timeout"

**Fix:**
- Ensure `startCommand` uses `$PORT` (not hardcoded)
- Check logs for: `Target PORT=10000`
- Verify: `uvicorn ... --port $PORT`

### Database Connection Errors

**Symptom:** `AsyncSession requires async driver`

**Fix:**
- Update `DATABASE_URL` to use `postgresql+asyncpg://`
- Not: `postgresql://` (sync driver)

### CORS Errors

**Symptom:** Frontend cannot reach backend

**Fix:**
1. Check Render `ALLOWED_ORIGINS` includes Netlify URL
2. Check Netlify `VITE_API_URL` points to Render
3. Verify `HeaderSyncMiddleware` is loaded (check logs)

### Heartbeat Not Running

**Symptom:** No heartbeat logs

**Fix:**
- Check: `httpx>=0.27.2` in `requirements.txt`
- Check: `[HEART] heartbeat started` in startup logs
- Set `HEARTBEAT_URL` if external ping needed

---

## 📊 Health Check Endpoints

| Endpoint | Purpose | Expected Response |
|----------|---------|-------------------|
| `/` | Root health | `{"ok": true, "version": "v1.9.6b"}` |
| `/ping` | Basic ping | `{"ok": true}` |
| `/api/health` | Service health | `{"status": "ok", ...}` |
| `/api/routes` | Route listing | `{"count": N, "routes": [...]}` |
| `/api/telemetry` | Runtime metrics | `{...}` |

---

## 🏁 Deployment Success Criteria

All must pass:

- [ ] Render build completes without errors
- [ ] `/ping` returns `{"ok": true}`
- [ ] Startup logs show:
  - `[MIDDLEWARE] Header sync enabled`
  - `[DB Bootstrap] ✅ Schema auto-sync complete`
  - `[HEART] heartbeat started`
- [ ] No port binding errors
- [ ] No database connection errors
- [ ] Frontend can reach backend (no CORS errors)
- [ ] GitHub Actions CI passes
- [ ] Route sweep check passes
- [ ] All tests pass

---

## 🔮 Version Info

- **Version:** v1.9.6b
- **Release Date:** 2025-10-10
- **Scope:** Route Integrity Sweep, Auto-Healing Runtime & Deployment Guard
- **Status:** Production-ready
- **Next Version:** v1.9.7 (Netlify parity bundler, Release Intelligence Engine)

---

## 📞 Support

If deployment fails:

1. Check this checklist first
2. Review startup logs on Render
3. Run local tests: `pytest -q`
4. Run route sweep: `python tools/route_sweep_check.py`
5. Check GitHub Actions logs

---

**✅ Bridge now defends, heals, and validates itself.**
