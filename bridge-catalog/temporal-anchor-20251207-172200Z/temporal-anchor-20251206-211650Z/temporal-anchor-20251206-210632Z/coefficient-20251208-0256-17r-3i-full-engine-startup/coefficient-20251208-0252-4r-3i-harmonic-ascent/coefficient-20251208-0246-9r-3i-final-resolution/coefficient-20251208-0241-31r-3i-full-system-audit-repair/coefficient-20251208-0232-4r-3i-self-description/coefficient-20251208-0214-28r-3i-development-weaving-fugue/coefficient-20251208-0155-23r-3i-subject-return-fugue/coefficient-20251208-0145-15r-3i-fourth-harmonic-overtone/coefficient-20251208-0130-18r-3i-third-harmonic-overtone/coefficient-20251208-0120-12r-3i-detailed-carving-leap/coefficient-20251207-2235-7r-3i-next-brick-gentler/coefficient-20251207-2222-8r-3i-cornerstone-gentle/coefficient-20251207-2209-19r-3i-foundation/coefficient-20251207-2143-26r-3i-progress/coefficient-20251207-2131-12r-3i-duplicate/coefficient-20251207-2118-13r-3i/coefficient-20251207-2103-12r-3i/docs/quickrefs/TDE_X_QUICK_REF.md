# TDE-X Quick Reference

## v1.9.7a - Hypersharded Deploy + Federation + Sovereign Post-Deploy

### Quick Start

```bash
# Set environment
export SECRET_KEY=your_secret_key
export DATABASE_URL=your_database_url
export PORT=8000

# Run server
python -m bridge_backend.run
```

### Health Checks

| Endpoint | Purpose | Success Response |
|----------|---------|-----------------|
| `/health/live` | Liveness probe | `{"status": "ok", "alive": true}` |
| `/health/ready` | Readiness probe | `{"status": "ready", "message": "Service is operational"}` |
| `/health/diag` | Queue diagnostics | `{"status": "ok", "queue_depth": N, ...}` |
| `/api/diagnostics/deploy-parity` | Shard status | `{"status": "ok", "version": "1.9.7a", "shards": {...}}` |

### Render Configuration

**Start Command:**
```bash
python -m bridge_backend.run
```

**Health Check Path:**
```
/health/live
```

**Required Environment Variables:**
- `SECRET_KEY`
- `DATABASE_URL`

**Optional Environment Variables:**
- `SEED_SECRET=sr_seed_<random>`
- `STABILIZER_ENABLED=true`
- `HEALTHCHECK_PATH=/health/live`

### Architecture

```
┌─────────────────────────────────────────┐
│         TDE-X Orchestrator              │
├─────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │Bootstrap │  │ Runtime  │  │  Diag  ││
│  │  Shard   │  │  Shard   │  │ Shard  ││
│  │  <7min   │  │  <10min  │  │  BG    ││
│  └──────────┘  └──────────┘  └────────┘│
│       │              │            │     │
│       v              v            v     │
│  ┌──────────────────────────────────┐  │
│  │   Stabilization Domain Layer    │  │
│  │   (Fault Isolation + Tickets)   │  │
│  └──────────────────────────────────┘  │
│                   │                     │
│                   v                     │
│  ┌──────────────────────────────────┐  │
│  │    Federation Event Bus          │  │
│  │    (deploy.events)               │  │
│  └──────────────────────────────────┘  │
│                   │                     │
│                   v                     │
│  ┌──────────────────────────────────┐  │
│  │   Background Task Queue          │  │
│  │   (Persistent Async Jobs)        │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Shards

| Shard | Target | Purpose | Failure Impact |
|-------|--------|---------|----------------|
| **Bootstrap** | <7min | Env validation, deps, cache | Ticket created, siblings continue |
| **Runtime** | <10min | DB sync, migrations, router verify | Ticket created, siblings continue |
| **Diagnostics** | Background | Asset uploads, analytics, metrics | Queued, runs after deploy |

### Federation Events

TDE-X publishes to `deploy.events` topic:
```json
{
  "stage": "runtime",
  "status": "ok"
}
```

Frontend should wait for:
- `stage == "runtime"` AND `status == "ok"`

### Monitoring

**Check Queue Depth:**
```bash
curl http://localhost:8000/health/diag | jq '.queue_depth'
```

**Check Shard Status:**
```bash
curl http://localhost:8000/api/diagnostics/deploy-parity | jq '.shards'
```

**Check for Tickets:**
```bash
ls bridge_backend/diagnostics/stabilization_tickets/
```

### Troubleshooting

| Issue | Check | Solution |
|-------|-------|----------|
| Server won't start | `SECRET_KEY`, `DATABASE_URL` set? | Set required env vars |
| High queue depth | `/health/diag` endpoint | Review background job logs |
| Shard failures | `stabilization_tickets/` directory | Check tickets for error details |
| 503 on `/health/ready` | Server startup phase | Wait for bootstrap+runtime shards |

### File Locations

```
bridge_backend/
  runtime/
    run.py                    # Entry point
    tickets.py                # Ticket creation
    tde_x/
      orchestrator.py         # Main orchestrator
      stabilization.py        # Fault isolation
      queue.py               # Background tasks
      federation.py          # Event announcements
      shards/
        bootstrap.py         # Env validation
        runtime.py           # DB sync
        diagnostics.py       # Background jobs
  routes/
    health.py                # Health endpoints
    diagnostics_timeline.py  # Deploy parity endpoint
  .queue/                    # Background job queue
    *.json                   # Queued jobs
  diagnostics/
    stabilization_tickets/   # Error tickets
      *.md                   # Individual tickets
```

### Migration from TDB (v1.9.6i)

TDE-X is a drop-in replacement for TDB. No changes needed to existing:
- API routes
- Database schema
- Environment configuration
- Frontend integration

New capabilities:
- Parallel shard execution (faster)
- Background task continuation (no timeout)
- Fault isolation (more stable)
- Enhanced monitoring endpoints

### Rollback (Emergency Only)

If needed, temporary rollback to direct uvicorn:
```bash
uvicorn bridge_backend.main:app --host 0.0.0.0 --port $PORT
```

This bypasses TDE-X but maintains API compatibility.
