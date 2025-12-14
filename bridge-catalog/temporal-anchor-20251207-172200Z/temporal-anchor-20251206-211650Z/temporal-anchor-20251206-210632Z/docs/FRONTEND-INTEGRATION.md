# SR-AIbridge v1.9.7 — Frontend Integration Guide

## Purpose
Netlify hosts your frontend (UI), Render hosts your backend (logic).  
Both are unified under a shared CORS + proxy protocol.

## Architecture Overview

**Layer** | **Role** | **System**
----------|----------|------------
Render | Intelligence Core | FastAPI, DB, heartbeat, diagnostics
Netlify | User Interface | React/Vite or Next.js frontend, proxy to Render
Predictive Stabilizer | Neural Immune System | Learns & repairs failed proxy states
Diagnostics | Nervous System | Generates self-healing tickets
Heartbeat | Circulatory Link | Confirms Render ↔ Netlify health sync

## Setup

### Backend Deployment (Render)
1. Deploy backend to Render (Python / FastAPI)
2. Set environment variable `HOST_PLATFORM=render` (auto-detected if `RENDER` env is present)
3. Configure `DATABASE_URL` for PostgreSQL connection
4. Verify `/health` endpoint returns `{"status": "ok", "host": "render"}`

### Frontend Deployment (Netlify)
1. Deploy frontend to Netlify
2. Netlify automatically redirects `/api/*` and `/health` to Render backend via `netlify.toml`
3. Set environment variable `HOST_PLATFORM=netlify` (auto-detected if `NETLIFY` env is present)
4. Verify proxy is working: `curl https://your-site.netlify.app/health`

## Local Development

Run both frontend and backend locally:

```bash
# Terminal 1: Backend
cd bridge_backend
uvicorn bridge_backend.main:app --reload

# Terminal 2: Frontend
cd bridge-frontend
npm run dev
```

Visit http://localhost:3000/api/health — you should see:
```json
{
  "status": "ok",
  "host": "local",
  "message": "Bridge link established and synchronized",
  "service": "SR-AIbridge",
  "version": "1.9.7"
}
```

## Environment Variables

| Variable | Purpose | Set On | Required |
|----------|---------|--------|----------|
| `HOST_PLATFORM` | Auto-set ("render", "netlify", "local") | All | ✅ Yes (auto-detected) |
| `HEARTBEAT_URL` | Optional override for health route | Render | ❌ No (auto-detected) |
| `DATABASE_URL` | PostgreSQL database connection | Render | ✅ Yes |
| `RENDER` | Auto-set by Render platform | Render | ✅ Yes (auto) |
| `NETLIFY` | Auto-set by Netlify platform | Netlify | ✅ Yes (auto) |
| `ALLOWED_ORIGINS` | CORS-allowed origins | Render | ✅ Yes |
| `HEARTBEAT_METHOD` | HTTP method for heartbeat (default: GET) | Render | ❌ No |

## Expected Behavior

### Health Endpoints
- `/health` returns 200 OK from both hosts
- Response includes `"host"` field indicating platform ("render", "netlify", or "local")
- Both Netlify and Render respond with identical structure

### API Routes
- `/api/*` routes seamlessly from frontend to backend
- CORS headers automatically handled
- No recursive loops or proxy errors

### Diagnostics
- Stabilizer logs anomalies in `/diagnostics/stabilization_tickets`
- Proxy events are recorded with timestamps
- Auto-healing tickets generated for CORS/proxy failures

## Troubleshooting

### CORS Errors
**Symptom:** Browser shows CORS policy errors

**Solution:**
1. Confirm frontend domain is in `ALLOWED_ORIGINS` environment variable
2. Check `bridge_backend/main.py` CORS configuration
3. Verify `netlify.toml` headers section includes CORS headers

### 405 Method Not Allowed or Timeouts
**Symptom:** `/health` returns 405 or times out

**Solution:**
1. Ensure `/health` uses `GET` method (not `POST`)
2. Check `heartbeat.py` is using `HEARTBEAT_METHOD=GET`
3. Verify Render service is running and accessible

### Proxy Loops
**Symptom:** Requests loop infinitely between Netlify and Render

**Solution:**
1. Disable any redundant proxy in Netlify's dashboard
2. Verify `netlify.toml` redirects are not conflicting
3. Check for circular HEARTBEAT_URL configuration

### Health Check Returns Wrong Host
**Symptom:** `/health` shows incorrect `"host"` value

**Solution:**
1. Verify `HOST_PLATFORM` environment variable is set correctly
2. Check that platform auto-detection is working (`RENDER` or `NETLIFY` env vars)
3. Review logs for `[BOOT] Detected host environment:` message

## Post-Deploy Verification

After deploying v1.9.7, run these checks:

### 1. Confirm Backend Health
```bash
curl -s https://sr-aibridge.onrender.com/health
```
Expected response:
```json
{
  "status": "ok",
  "host": "render",
  "message": "Bridge link established and synchronized"
}
```

### 2. Confirm Frontend Health
```bash
curl -s https://sr-aibridge.netlify.app/health
```
Expected response (proxied from Render):
```json
{
  "status": "ok",
  "host": "render",
  "message": "Bridge link established and synchronized"
}
```

### 3. Test Live Proxy
```bash
curl -I https://sr-aibridge.netlify.app/api/health
```
Expected: `HTTP/2 200 OK`

### 4. Verify Database Connection
Check Render logs for:
```
✅ Runtime initialized successfully with: postgresql+asyncpg://...
```

### 5. Self-Test Verification (if implemented)
```bash
curl -s https://sr-aibridge.onrender.com/diagnostics/selftest
```
Expected summary:
```json
{
  "render_to_db": "ok",
  "netlify_proxy": "ok",
  "heartbeat": "ok",
  "environment_sync": "ok"
}
```

### 6. Telemetry Confirmation
Check logs for:
```
[TELEMETRY] Netlify ↔ Render channels active
```

## Result

✅ Unified ecosystem  
✅ Full transparency between hosts  
✅ Zero backend duplication  
✅ Predictive error handling  
✅ Consistent health & runtime behavior  

---

**Tagline:** "Render is the Brain. Netlify is the Face. Both speak one language."

The Bridge is a living system with environmental awareness, self-healing diagnostics, and universal connectivity. 🧠❤️🌐
