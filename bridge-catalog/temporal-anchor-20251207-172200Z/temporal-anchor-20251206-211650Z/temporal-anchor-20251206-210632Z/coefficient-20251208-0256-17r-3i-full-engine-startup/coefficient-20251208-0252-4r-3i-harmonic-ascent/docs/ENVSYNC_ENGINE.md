# EnvSync Engine - Render & Netlify Auto-Sync

## Overview

The EnvSync Engine provides autonomous, hands-off synchronization of environment variables between the SR-AIbridge canonical source and Render/Netlify deployment platforms. It discovers credentials elegantly, computes diffs, and keeps providers in lockstep without manual intervention.

## Features

- **Token Discovery Chain**: Automatically locates API tokens from ENV vars, secret files, Vault, or dashboard endpoints
- **Idempotent Sync**: Only updates variables that have drifted; never creates duplicates
- **Dry-run & Enforce Modes**: Preview changes before applying them
- **Rich Diffing**: See exactly what will change (create, update, delete, noop)
- **Telemetry & Tickets**: Automatic diagnostics when drift occurs or providers fail
- **Background Scheduler**: Periodic sync on @hourly or @daily schedule
- **Manual Triggers**: HTTP endpoints for on-demand sync

## Architecture

```
EnvSync Engine
├── Discovery Chain
│   ├── Environment Variables
│   ├── Secret Files (/etc/secrets, ./secrets)
│   ├── Bridge Vault API
│   └── Dashboard Token Endpoints
├── Provider Adapters
│   ├── Render API
│   └── Netlify API
├── Diff Engine
│   ├── Create (new vars)
│   ├── Update (changed vars)
│   ├── Delete (optional)
│   └── Noop (unchanged)
├── Sync Orchestrator
│   ├── Fetch from providers
│   ├── Compute diff vs canonical
│   ├── Apply changes (dry-run or enforce)
│   └── Report telemetry
└── Genesis & Autonomy Integration
    ├── Genesis Bus event notifications
    ├── Autonomy-triggered syncs
    └── Coordinated secret rotation
```

### Genesis Bus Integration

EnvSync emits events to the Genesis Bus for system-wide coordination:

- `ENVSYNC_DRIFT_DETECTED`: When provider variables differ from canonical
- `ENVSYNC_COMPLETE`: After sync operations complete

Other engines can subscribe to these events and react accordingly.

### Autonomy Engine Integration

The Autonomy engine can trigger EnvSync operations:

- On-demand sync requests
- Secret rotation workflows
- Automated drift remediation

EnvSync registers itself as an autonomous task, allowing the Autonomy orchestrator to manage sync scheduling and error handling.

## Configuration

### Environment Variables

Add these to your `.env` or deployment platform:

```bash
# === ENVSYNC CORE ===
ENVSYNC_ENABLED=true
ENVSYNC_MODE=enforce            # one of: dry-run | enforce
ENVSYNC_SCHEDULE=@hourly        # @hourly | @daily
ENVSYNC_CANONICAL_SOURCE=vault  # vault | file | env | dashboard
ENVSYNC_TARGETS=render,netlify  # comma-list: render,netlify

# === TOKEN DISCOVERY ===
ENVSYNC_DISCOVERY_ORDER=env,secret_files,vault,dashboard
ENVSYNC_SECRET_FILENAMES=render.token,netlify.token
ENVSYNC_VAULT_TOKEN_KEYS=RENDER_API_TOKEN,NETLIFY_API_TOKEN
ENVSYNC_DASHBOARD_TOKEN_URLS=https://admin.example.com/api/tokens/envsync

# === RENDER SELECTORS ===
RENDER_ACCOUNT_ID=auto
# Legacy RENDER_SERVICE_ID removed=srv-xxxxx
RENDER_REGION=oregon             # optional, cosmetic

# === NETLIFY SELECTORS ===
NETLIFY_SITE_ID=auto             # or explicit site id
NETLIFY_TEAM_ID=auto             # optional

# === SYNC SHAPING ===
ENVSYNC_INCLUDE_PREFIXES=BRIDGE_,SR_,HEART_,ENVSYNC_
ENVSYNC_EXCLUDE_PREFIXES=SECRET_,INTERNAL_,DEBUG_
ENVSYNC_ALLOW_DELETIONS=false    # if true, removes provider-only keys
```

## Token Discovery

The EnvSync engine uses a **discovery chain** to locate API tokens without hardcoding them:

### 1. Environment Variables
First checks `RENDER_API_TOKEN` and `NETLIFY_API_TOKEN` in environment.

### 2. Secret Files
Looks for files in `/etc/secrets/` and `./secrets/`:
- `render.token`
- `netlify.token`

### 3. Vault API
Queries the Bridge Vault at `GET /bridge/vault/secret?key=RENDER_API_TOKEN`

### 4. Dashboard Endpoints
Calls admin dashboard URLs (if configured) to fetch tokens dynamically:
```
GET https://admin.example.com/api/tokens/envsync?key=RENDER_API_TOKEN
```

**Important**: The discovery stops at the first successful source in the configured order.

## API Endpoints

### Health Check
```bash
GET /envsync/health
```
Returns current configuration and status.

### Dry-Run (Preview Changes)
```bash
POST /envsync/dry-run/render
POST /envsync/dry-run/netlify
```
Shows what would change without applying.

### Apply Sync
```bash
POST /envsync/apply/render
POST /envsync/apply/netlify
POST /envsync/apply-all
```
Applies synchronization in enforce mode.

## Usage Examples

### Manual Dry-Run
```bash
curl -X POST https://bridge.sr-aibridge.com/envsync/dry-run/render
```

Response:
```json
{
  "provider": "render",
  "mode": "dry-run",
  "applied": false,
  "diff": [
    {"key": "BRIDGE_VERSION", "op": "update", "from_val": "1.9.7", "to_val": "1.9.8"},
    {"key": "NEW_VAR", "op": "create", "from_val": null, "to_val": "value"}
  ],
  "errors": []
}
```

### Apply Sync to All Providers
```bash
curl -X POST https://bridge.sr-aibridge.com/envsync/apply-all
```

## Include/Exclude Filtering

The engine respects prefix-based filtering:

**Include Prefixes**: Only variables starting with these prefixes are synced
- Default: `BRIDGE_`, `SR_`, `HEART_`, `ENVSYNC_`

**Exclude Prefixes**: Variables with these prefixes are never synced
- Default: `SECRET_`, `INTERNAL_`, `DEBUG_`

**Logic**: Exclude takes precedence. If a variable matches an exclude prefix, it's skipped. Otherwise, it must match an include prefix (if any are defined).

## Scheduled Sync

The engine runs automatically in the background based on `ENVSYNC_SCHEDULE`:

- `@hourly`: Every 60 minutes
- `@daily`: Every 24 hours

Check logs for sync activity:
```
[ENVSYNC] render: applied=True changes=3 errors=0
[ENVSYNC] netlify: applied=True changes=2 errors=0
```

## GitHub Actions Integration

After every merge to `main`, the EnvSync workflow automatically triggers:

```yaml
# .github/workflows/envsync.yml
name: EnvSync After Merge
on:
  push:
    branches: [ "main" ]
jobs:
  envsync:
    runs-on: ubuntu-latest
    steps:
      - name: Call EnvSync
        run: |
          curl -X POST "$BRIDGE_BASE_URL/envsync/apply-all"
```

## Troubleshooting

### Token Not Found
```
RuntimeError: Render API token not found via discovery chain
```
**Solution**: Ensure `RENDER_API_TOKEN` is set in ENV, secret file, Vault, or dashboard.

### Empty Diff
If the engine reports 0 changes but you expect drift:
1. Check include/exclude prefixes
2. Verify `ENVSYNC_CANONICAL_SOURCE` is correct
3. Run dry-run to inspect the diff

### Provider Errors
```
errors: ["HTTP 401 Unauthorized"]
```
**Solution**: Verify API tokens are valid and have correct permissions.

## Dashboard Token Endpoint (Optional)

If you want to expose tokens via a dashboard:

```python
# Your admin dashboard route
@router.get("/api/tokens/envsync")
async def get_envsync_token(key: str):
    # Authenticate request (bearer token, session, etc.)
    if key == "RENDER_API_TOKEN":
        return {"value": load_from_secure_storage("render_token")}
    # etc.
```

## Security Notes

- Never log or print token values
- Use secure storage for tokens (Vault, secret files with proper permissions)
- Dashboard endpoints should require authentication
- Tokens should have minimal required permissions (env var management only)

## Operational Best Practices

1. **Start with dry-run**: Always test with `POST /envsync/dry-run/provider` first
2. **Monitor logs**: Check for `[EnvSync]` messages in application logs
3. **Review diffs**: Inspect the diff before using enforce mode
4. **Use scheduled sync**: Let the engine keep things fresh automatically
5. **Handle failures gracefully**: Engine creates tickets for diagnostics on errors

## Version History

- **v1.9.8**: Initial EnvSync Engine release
  - Token discovery chain
  - Render & Netlify adapters
  - Dry-run and enforce modes
  - Background scheduler
  - GitHub Actions integration
