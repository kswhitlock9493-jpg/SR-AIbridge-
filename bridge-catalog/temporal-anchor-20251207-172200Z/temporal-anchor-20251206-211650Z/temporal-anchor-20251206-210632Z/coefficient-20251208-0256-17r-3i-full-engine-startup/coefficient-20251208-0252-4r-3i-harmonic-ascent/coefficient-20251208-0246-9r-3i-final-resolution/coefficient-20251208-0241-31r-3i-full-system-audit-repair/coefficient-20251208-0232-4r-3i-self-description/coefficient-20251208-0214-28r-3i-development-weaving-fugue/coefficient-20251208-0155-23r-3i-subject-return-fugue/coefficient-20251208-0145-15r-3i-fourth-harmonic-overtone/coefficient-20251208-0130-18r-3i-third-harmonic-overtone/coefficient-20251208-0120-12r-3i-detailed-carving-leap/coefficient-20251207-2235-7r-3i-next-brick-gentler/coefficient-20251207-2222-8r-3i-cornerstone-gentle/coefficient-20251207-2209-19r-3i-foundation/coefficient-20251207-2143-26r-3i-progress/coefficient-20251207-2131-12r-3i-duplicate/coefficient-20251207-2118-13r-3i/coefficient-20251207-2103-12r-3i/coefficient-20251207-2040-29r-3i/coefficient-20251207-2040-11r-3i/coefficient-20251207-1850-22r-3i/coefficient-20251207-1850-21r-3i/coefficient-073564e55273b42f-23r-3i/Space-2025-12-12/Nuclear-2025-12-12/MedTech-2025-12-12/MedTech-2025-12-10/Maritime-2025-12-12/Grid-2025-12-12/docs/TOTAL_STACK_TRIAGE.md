# Total-Stack Triage Mesh

## Overview

The Total-Stack Triage Mesh provides comprehensive monitoring and automated repair across the entire SR-AIbridge stack:

- **Runtime** - Health checks, database connectivity, and cold-start detection
- **Build** - Build artifact validation and dependency verification
- **Deploy** - Unified release gates with artifact aggregation
- **Endpoints** - API route validation and frontend/backend alignment
- **APIs** - Static analysis of API calls and definitions
- **Event Hooks** - Detection of unused or missing webhooks
- **Environments** - Cross-environment parity and drift detection

## Signals

The triage mesh monitors these key signals:

| Signal | Description | Source |
|--------|-------------|--------|
| **Reachable** | Service responds to health checks | Runtime Triage |
| **SchemaMatch** | Federation schema versions align | Federation Deep-Seek |
| **LiveCallOK** | Test API calls succeed | Federation Deep-Seek |
| **BuildDist** | Build outputs exist and are valid | Build Triage |
| **DBPing** | Database connectivity verified | Runtime Triage |
| **EnvParity** | Environment variables match canonical list | Env Parity Guard |

## Workflows

### 1. Build Triage (Netlify)
**Schedule:** Every 6 hours (at :15)  
**Purpose:** Validates build outputs and dependencies

Auto-repair behaviors:
- Normalizes `netlify.toml` publish path
- Adds missing SPA redirects
- Validates `@netlify/functions-core` if functions exist

### 2. Runtime Triage (Render)
**Schedule:** Every 6 hours (at :45)  
**Purpose:** Monitors runtime health and database connectivity

Checks:
- DNS resolution
- `/api/health` endpoint
- `/api/db/ping` endpoint  
- `/api/db/migrate?dryrun=1` (migration readiness)

### 3. Deploy Gate
**Trigger:** Push to `main` or manual dispatch  
**Purpose:** Blocks releases until all systems green

Evaluates:
- Federation health (all nodes PASS)
- Build artifacts (dist folder exists)
- Runtime health (DNS, health, DB all OK)

### 4. Endpoints & Hooks Sweep
**Schedule:** Every 12 hours  
**Purpose:** Detects API mismatches

Analyzes:
- Backend route definitions (`@router.get`, `@app.post`, etc.)
- Frontend API calls (`fetch()`, `axios.*()`)
- Missing routes (backend routes not called from frontend)
- Orphaned calls (frontend calls to non-existent routes)

### 5. Environment Parity Guard
**Schedule:** Daily at 2 AM  
**Purpose:** Prevents environment drift

Validates canonical environment variables across:
- `.env`
- `.env.production`
- `bridge-frontend/.env.production`
- `.env.netlify`
- `.env.render`

## Escalation

If the Deploy Gate blocks release twice in a row:

1. **Check artifacts** - Download artifact set from failed workflow runs
2. **Review reports** - Examine JSON reports in `bridge_backend/diagnostics/`
3. **Apply patches** - Update environment variables in Netlify/Render as needed
4. **Re-run gate** - Manually trigger Deploy Gate workflow
5. **Open issue** - If problems persist, open issue with artifact set attached

## Reports

All workflows write JSON reports to `bridge_backend/diagnostics/`:

- `federation_repair_report.json` - Federation health and repairs
- `build_triage_report.json` - Build validation results
- `runtime_triage_report.json` - Runtime health metrics
- `endpoint_api_sweep.json` - API route analysis
- `env_parity_report.json` - Environment drift detection
- `total_stack_report.json` - Unified rollup of all reports

## Safe Auto-Repair

The triage mesh performs these safe, non-destructive repairs:

✅ **Cache refresh** - Updates local schema cache files  
✅ **Intent staging** - Suggests environment variable updates  
✅ **Retry with backoff** - Retries failed calls with exponential backoff  
✅ **DNS warmup** - Pre-resolves hostnames before health checks

❌ **Never destructive** - No database mutations, no production config changes

## Running Locally

Individual triage scripts can be run locally:

```bash
# Runtime triage
python3 .github/scripts/runtime_triage_render.py

# Endpoint sweep
python3 .github/scripts/endpoint_api_sweep.py

# Environment parity
python3 .github/scripts/env_parity_guard.py

# Unified report
python3 .github/scripts/deploy_triage.py
```

## Post-Merge Checklist

After merging to `main`:

1. ✅ Manually run Build Triage workflow
2. ✅ Manually run Runtime Triage workflow
3. ✅ Manually run Federation Deep-Seek workflow (seed artifacts)
4. ✅ Run Deploy Gate workflow
5. ✅ Verify PASS status
6. ✅ Check `bridge_backend/diagnostics/total_stack_report.json`
7. ✅ If gate blocks, apply patch intents and re-run

## Integration

The Deploy Gate integrates with existing workflows:

```yaml
# Existing workflows upload their artifacts
- uses: actions/upload-artifact@v4
  with:
    name: federation_repair_report
    path: bridge_backend/diagnostics/federation_repair_report.json

# Deploy Gate downloads and evaluates all artifacts
- uses: actions/download-artifact@v4
  with: { name: federation_repair_report, path: _artifacts/fed }
```

## Troubleshooting

### Deploy Gate Fails

**Symptom:** `fed=False` or `build=False` or `runtime=False`

**Solution:**
1. Check individual workflow runs
2. Download failed workflow artifacts
3. Review error messages in reports
4. Apply suggested patch intents
5. Re-run failed workflow

### Schema Mismatch

**Symptom:** `schema_match: false` in federation report

**Solution:**
1. Check `FEDERATION_SCHEMA_VERSION_*` environment variables
2. Update version in Netlify/Render settings
3. Re-run Federation Deep-Seek workflow

### Missing Endpoints

**Symptom:** `missing_from_backend` or `missing_from_frontend` not empty

**Solution:**
1. Review endpoint sweep report
2. Add missing routes or remove unused calls
3. Update API client/server code

## Architecture

```
┌─────────────────────────────────────────────────┐
│         Total-Stack Triage Mesh                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  Build       │  │  Runtime     │            │
│  │  Triage      │  │  Triage      │            │
│  └──────┬───────┘  └──────┬───────┘            │
│         │                 │                     │
│         ▼                 ▼                     │
│  ┌──────────────────────────────────┐          │
│  │        Deploy Gate               │          │
│  │  (Artifact Aggregation)          │          │
│  └──────────────┬───────────────────┘          │
│                 │                               │
│                 ▼                               │
│  ┌──────────────────────────────────┐          │
│  │  Unified Stack Report            │          │
│  │  (total_stack_report.json)       │          │
│  └──────────────────────────────────┘          │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  Endpoint    │  │  Env Parity  │            │
│  │  Sweep       │  │  Guard       │            │
│  └──────────────┘  └──────────────┘            │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Version History

- **v1.8.2** - Total-Stack Triage Mesh (this release)
- **v1.8.1** - Federation Deep-Seek auto-repair
- **v1.8.0** - Federation triage baseline
