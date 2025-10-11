# SR-AIbridge — Release Intelligence & Self-Heal

## What's new in v1.9.6f (Latest)

**Render Bind & Startup Stability Patch (Final)**

- **Adaptive Port Binding:** 2.5s prebind monitor waits for Render's delayed `PORT` injection
- **Graceful Rebind Fallback:** Auto-falls back to `:8000` if target port unavailable
- **Deferred Heartbeat:** Launches only after confirmed Uvicorn bind (eliminates race conditions)
- **Predictive Watchdog:** Monitors startup latency, creates diagnostic tickets if > 6s
- **Self-Healing Diagnostics:** Auto-resolves old tickets, persistent metric logging
- **Enhanced Logging:** `[STABILIZER]` prefix for all startup metrics
- **No More Timeouts:** Eliminates Render pre-deploy failures and false shutdown states

### Migration from v1.9.6b → v1.9.6f
No breaking changes. Simply deploy - all enhancements are backward compatible.

### Expected Logs
```
[PORT] Resolved immediately: 10000
[BOOT] Adaptive port bind: ok on 0.0.0.0:10000
[STABILIZER] Startup latency 2.43s (tolerance: 6.0s)
[HEARTBEAT] ✅ Initialized
```

### Health Check
- `GET /` returns `{ ok: true, version: "1.9.6f" }`
- No `Pre-deploy has failed` or `Timed out` messages

---

## What's new in v1.9.6b
- Render port binding via `$PORT` (no more port-scan timeouts).
- Auto DB schema sync on startup (SQLAlchemy create_all).
- Permanent heartbeat using `httpx`.
- Release Intelligence + Predictive Stabilizer:
  - Reads `diagnostics/release_insights.json`
  - Creates stabilization tickets under `diagnostics/stabilization_tickets/`
  - Optionally opens GitHub Issues (set `GITHUB_REPO` and `GITHUB_TOKEN`)
- Netlify header alignment (`netlify.toml`) for CORS/testing parity.

## One-time checklist
- Set Render start command: `bash -lc 'uvicorn bridge_backend.main:app --host 0.0.0.0 --port ${PORT}'`
- Add env vars from `.env.template`
- (Optional) Provide `GITHUB_TOKEN` with `repo:issues`

## Health verify
- `GET /` returns `{ ok: true, version: "v1.9.6b" }`
- Logs show:
  - `[DB] ✅ Database schema synchronized successfully.`
  - `heartbeat: ✅ initialized`
  - `stabilizer: ... ticket created` (if low stability score)

## Why this permanently fixes your two recurring pains

### 1. Render port scans timing out
We now always bind Uvicorn to $PORT → Render sees the open port immediately.

### 2. Heartbeat sometimes "disabled"
httpx is in requirements.txt, and heartbeat runs as its own async task. If HEARTBEAT_URL isn't set, it simply no-ops without warnings.

### 3. "models" import/path errors
We standardized package paths (explicit bridge_backend.* imports) and added __init__.py everywhere.

### 4. DB missing tables after deploy
init_schema() runs create_all() on startup, so fresh environments and ephemeral DBs self-bootstrap.

### 5. Self-heal + learn
Release intel feeds the Predictive Stabilizer, which creates a local ticket and (if configured) a GitHub Issue with context and actions. Next deploys can verify reduced volatility.

## How to merge

1. Commit all files above.
2. Push branch release/v1.9.6b.
3. Open PR with title: "v1.9.6b — Predictive Stabilization & Self-Healing".
4. On Render, ensure start command uses $PORT.
5. Set GITHUB_REPO and GITHUB_TOKEN to enable issue auto-creation.
