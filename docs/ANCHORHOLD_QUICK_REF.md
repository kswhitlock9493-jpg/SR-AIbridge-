# Anchorhold Protocol — Quick Reference

## Version Info
- **Version:** 1.9.4
- **Protocol:** Anchorhold
- **Status:** ✅ Production Ready

## Key Features

### 1. Dynamic Port Binding
```python
port = int(os.environ.get("PORT", 8000))
uvicorn.run("bridge_backend.main:app", host="0.0.0.0", port=port)
```
- Auto-binds to Render's dynamic port
- Default: 8000 (local dev)

### 2. Schema Auto-Sync
```python
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```
- Runs on startup
- Self-healing database

### 3. Heartbeat System
```python
# 5-minute keepalive ping
HEARTBEAT_INTERVAL = 300
```
- Keeps Render alive
- Target: `/api/health`

### 4. CORS Config
```python
CORS_ALLOW_ORIGINS = [
    "https://sr-aibridge.netlify.app",
    "https://sr-aibridge.onrender.com"
]
```

## Quick Commands

### Local Testing
```bash
# Start server
PORT=8000 python -m bridge_backend.main

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/api/version

# Test CORS
curl -I -H "Origin: https://sr-aibridge.netlify.app" http://localhost:8000/
```

### Validation
```bash
# Syntax check
python3 -m py_compile bridge_backend/main.py

# Import test
python3 -c "from bridge_backend.main import app; print(app.version)"

# Heartbeat test
python3 -c "from runtime.heartbeat import start_heartbeat; print('OK')"
```

## API Endpoints

### Root
```bash
GET /
{
  "status": "active",
  "version": "1.9.4",
  "protocol": "Anchorhold"
}
```

### Version
```bash
GET /api/version
{
  "version": "1.9.4",
  "protocol": "Anchorhold",
  "service": "SR-AIbridge Backend"
}
```

## Environment Variables

### Required
- `DATABASE_URL` - Database connection
- `ALLOWED_ORIGINS` - CORS origins (comma-separated)

### Optional
- `PORT` - Server port (Render sets dynamically)
- `BRIDGE_API_URL` - Backend URL for heartbeat
- `ENVIRONMENT` - production/development

## Files Changed
1. `bridge_backend/main.py` - Core changes
2. `bridge_backend/runtime/heartbeat.py` - NEW
3. `bridge_backend/runtime/auto_repair.py` - Enhanced
4. `bridge_backend/requirements.txt` - Added httpx
5. `render.yaml` - Updated config
6. `netlify.toml` - API proxy

## Troubleshooting

### Port issues
- Check `PORT` env var
- Verify `sync: false` in render.yaml

### CORS errors
- Check `ALLOWED_ORIGINS`
- Verify origin in allowed list

### Heartbeat fails
- Ensure httpx installed
- Check `/api/health` exists

### Schema sync fails
- Verify DB connection
- Check models import

## Deployment

### Render
- Auto-deploys from GitHub
- Uses `python -m bridge_backend.main`
- Dynamic PORT assigned

### Netlify
- Auto-builds frontend
- Proxies `/api/*` to Render
- Environment in netlify.toml

---

**Full Docs:** See `docs/ANCHORHOLD_PROTOCOL.md`
