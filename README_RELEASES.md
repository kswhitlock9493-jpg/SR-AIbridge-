# SR-AIbridge — Release Intelligence & Self-Heal

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
