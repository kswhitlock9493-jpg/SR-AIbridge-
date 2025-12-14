# TDE-X v1.9.7a Deployment Guide

## Overview

TDE-X (Temporal Deploy Engine - Extended) is a hypersharded deployment orchestrator that replaces the old TDE path with parallel shard execution and sovereign background task continuation.

## Key Features

- **Hypersharded Deployment**: Three parallel shards (bootstrap, runtime, diagnostics) run independently
- **Stabilization Domains**: Fault isolation prevents global crashes; failures produce tickets
- **Federation Hooks**: Event-driven deployment announcements to Deploy Federation Bus
- **Background Sovereign Tasks**: Long-running work continues after deploy completes
- **Health & Readiness**: Comprehensive health endpoints for monitoring

## Architecture

### Shards

1. **Bootstrap Shard** (Target: <7 min)
   - Environment variable validation
   - Dependency checks
   - Cache warming

2. **Runtime Shard** (Target: <10 min)
   - Database schema sync
   - Migrations
   - API router verification

3. **Diagnostics Shard** (Background only)
   - Asset uploads
   - Analytics
   - Parity sync

### Components

```
bridge_backend/
  runtime/
    run.py                         # Entry point: python -m bridge_backend.run
    tde_x/
      orchestrator.py              # Orchestrates shards with parallel execution
      stabilization.py             # StabilizationDomain context manager
      federation.py                # Event hooks → federation bus
      queue.py                     # Background task queue (async, persistent)
      shards/
        bootstrap.py               # Env/dep/cache bootstrap
        runtime.py                 # DB schema align, migrations, router verify
        diagnostics.py             # Long-tail background jobs
    tickets.py                     # Ticket creation for StabilizationDomain
  routes/
    health.py                      # /health/live, /health/ready, /health/diag
    diagnostics_timeline.py        # /api/diagnostics/deploy-parity (updated)
```

## Endpoints

### Health Checks

#### `/health/live`
Always returns 200 OK once process started.
```json
{"status": "ok", "alive": true}
```

#### `/health/ready`
Returns 200 OK after bootstrap+runtime shards succeed; else 503.
```json
{"status": "ready", "message": "Service is operational"}
```

#### `/health/diag`
Returns diagnostics queue depth + last ticket id.
```json
{
  "status": "ok",
  "queue_depth": 2,
  "last_ticket": null,
  "ticket_count": 0
}
```

### Deploy Parity

#### `/api/diagnostics/deploy-parity`
Returns current shard states + background queue status.
```json
{
  "status": "ok",
  "version": "1.9.7a",
  "shards": {
    "bootstrap": true,
    "runtime": true,
    "diagnostics": false
  },
  "queue": {
    "depth": 2,
    "active": true
  },
  "tickets": {
    "count": 0,
    "has_issues": false
  }
}
```

## Environment Variables

### Required
- `SECRET_KEY` - Application secret key
- `DATABASE_URL` - Database connection string (e.g., `sqlite+aiosqlite:///./dev.db` or `postgresql+asyncpg://...`)

### Optional
- `PORT` - Server port (default: 8000, Render injects this)
- `HOST` - Server host (default: 0.0.0.0)
- `LOG_LEVEL` - Logging level (default: info)
- `SEED_SECRET` - Seed secret for cryptographic operations
- `STABILIZER_ENABLED` - Enable predictive stabilizer (default: true)
- `HEALTHCHECK_PATH` - Health check path (default: /health/live)

## Render Configuration

### Start Command
```bash
python -m bridge_backend.run
```

### Health Check Path
```
/health/live
```

### Pre-Deploy Command (Optional)
```bash
true
```
TDE-X doesn't require pre-deploy commands, but you can keep existing hooks if needed.

## Local Testing

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export SECRET_KEY=dev
export DATABASE_URL=sqlite+aiosqlite:///./dev.db
export PORT=8000
```

### 3. Run Server
```bash
python -m bridge_backend.run
```

### 4. Test Endpoints
```bash
# Test liveness
curl http://localhost:8000/health/live

# Test readiness
curl http://localhost:8000/health/ready

# Test diagnostics
curl http://localhost:8000/health/diag

# Test deploy parity
curl http://localhost:8000/api/diagnostics/deploy-parity
```

## Netlify (Frontend) Integration

No frontend changes required. Deploy Federation will now receive:
```json
{
  "topic": "deploy.events",
  "stage": "runtime",
  "status": "ok"
}
```

Frontend hydration should wait for:
- `stage == "runtime"`
- `status == "ok"`

## Background Tasks

TDE-X queues background tasks that run after deployment:
- `upload_assets` - Upload build artifacts
- `emit_metrics` - Push deployment telemetry

Queue location: `bridge_backend/.queue/`

Tasks are persisted as JSON files and drained asynchronously after app startup.

## Rollback

Safe rollback option if needed:
```bash
# Temporary rollback to direct uvicorn
uvicorn bridge_backend.main:app --host 0.0.0.0 --port $PORT
```

## What This Solves

1. **Render Timeouts**: Core deploy finishes well within 30 min; heavy tasks continue in background
2. **Crash Loops**: Shard isolation + ticketing prevents app-level failure
3. **Cross-Stack Coordination**: Federation becomes event-driven
4. **Observability**: Clear parity + diagnostic endpoints

## Monitoring

### Queue Depth
Monitor `/health/diag` to track background job queue depth.

### Shard Status
Check `/api/diagnostics/deploy-parity` for shard completion status.

### Tickets
Failed operations create tickets in `bridge_backend/diagnostics/stabilization_tickets/`.

## Troubleshooting

### Issue: Server won't start
- Check `SECRET_KEY` and `DATABASE_URL` are set
- Verify port 8000 (or $PORT) is available

### Issue: High queue depth
- Check `/health/diag` for queue status
- Background jobs may be slow or stuck
- Review logs for errors in queue processing

### Issue: Shard failures
- Check `bridge_backend/diagnostics/stabilization_tickets/` for tickets
- Review server logs for shard execution errors
- StabilizationDomain isolates failures to prevent global crash
