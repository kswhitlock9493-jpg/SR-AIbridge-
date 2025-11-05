# Env Steward v1.9.6l — Quick Reference

## Quick Start

Want to quickly see what environment variables are missing across your deployment platforms?

```bash
# Enable Steward
export STEWARD_ENABLED=true
export STEWARD_OWNER_HANDLE=kswhitlock9493-jpg

# Run the drift report script
python3 get_env_drift.py > drift_report.json

# Or view the summary only
python3 get_env_drift.py 2>&1 >/dev/null
```

The script will:
1. Connect to Render, Netlify, and GitHub (if credentials configured)
2. Compare environment variables across all platforms
3. Output a comprehensive JSON report showing what's missing where
4. Save the report to `logs/steward_drift_report.json`

See [STEWARD_ENVRECON_INTEGRATION.md](STEWARD_ENVRECON_INTEGRATION.md) for full details.

---

## Overview

**Env Steward** is an admiral-tier environment orchestration engine that provides:

- 🔍 **Environment drift detection** across Render, Netlify, and GitHub
- 📋 **Planned, phased changes** with Blueprint validation
- 🛡️ **Admiral-only access** with explicit authorization
- 🔐 **Capability tokens** for short-lived write permissions
- 🚀 **Provider adapters** for Render, Netlify, and GitHub
- 📡 **Genesis event publishing** for full audit trail

---

## Security Model

### Admiral-Tier Lock

**Only the admiral (owner) can:**
- View steward status
- Create execution plans
- Issue capability tokens
- Apply environment changes

**This is enforced at multiple levels:**
1. **Permissions middleware** - Blocks non-admiral access to `/api/steward/*`
2. **RBAC matrix** - Admiral role has `steward.read`, `steward.cap.issue`, `steward.write`
3. **Core engine** - Validates actor against `STEWARD_OWNER_HANDLE`

### Default Deny

Write mode is **OFF by default**. To enable writes:

1. Set `STEWARD_WRITE_ENABLED=true` (environment variable)
2. Issue a capability token as admiral
3. Use the token in `X-Bridge-Cap` header when applying changes

---

## Configuration

### Environment Variables

```bash
# Engine toggles
STEWARD_ENABLED=true                  # Enable/disable the engine
STEWARD_WRITE_ENABLED=false           # Enable write mode (default: false)
STEWARD_CAP_TTL_SECONDS=600           # Capability token lifetime (default: 10 min)
STEWARD_OWNER_HANDLE=kswhitlock9493-jpg  # Admiral username

# Provider toggles (safe to leave false)
STEWARD_RENDER_ENABLED=false
STEWARD_NETLIFY_ENABLED=false
STEWARD_GITHUB_ENABLED=false

# Provider identifiers (non-secret)
RENDER_SERVICE_ID=srv-d39k3ejuibrs73etqnag
NETLIFY_SITE_ID=
GITHUB_REPO_SLUG=kswhitlock9493-jpg/SR-AIbridge-

# Provider API tokens (secret - leave blank unless enabling write-mode)
RENDER_API_TOKEN=
NETLIFY_AUTH_TOKEN=
GITHUB_TOKEN=
```

**Important:** Add secrets only in platform dashboards (Render/Netlify/GitHub), not in code or logs.

---

## API Endpoints

All endpoints require **admiral role**. Non-admiral users will receive:

```json
{
  "detail": "steward_admiral_only"
}
```

### 1. Get Status

```bash
GET /api/steward/status
```

**Response:**
```json
{
  "enabled": true,
  "write_enabled": false,
  "owner_handle": "kswhitlock9493-jpg",
  "cap_ttl_seconds": 600
}
```

### 2. Compute Diff

```bash
POST /api/steward/diff?providers=render,netlify,github&dry_run=true
```

**Response:**
```json
{
  "has_drift": false,
  "providers": ["render", "netlify", "github"],
  "changes": [],
  "missing_in_render": [],
  "missing_in_netlify": [],
  "missing_in_github": [],
  "extra_in_render": [],
  "extra_in_netlify": [],
  "conflicts": {},
  "summary": {
    "total_keys": 16,
    "local_count": 16,
    "render_count": 16,
    "netlify_count": 16,
    "github_count": 16
  },
  "timestamp": "2025-10-11T17:45:00.000000"
}
```

**New in v1.9.6l**: The diff endpoint now integrates with EnvRecon to provide comprehensive environment drift reporting. See [STEWARD_ENVRECON_INTEGRATION.md](STEWARD_ENVRECON_INTEGRATION.md) for details.

### 3. Create Plan

```bash
POST /api/steward/plan
Content-Type: application/json

{
  "providers": ["render", "netlify", "github"],
  "strategy": "safe-phased"
}
```

**Response:**
```json
{
  "id": "abc123...",
  "providers": ["render", "netlify", "github"],
  "strategy": "safe-phased",
  "phases": [
    {
      "name": "non-secrets",
      "changes": []
    }
  ],
  "mutation_window_id": "def456...",
  "certified": true,
  "created_at": "2025-10-11T17:45:00.000000"
}
```

### 4. Issue Capability Token (Admiral Only)

```bash
POST /api/steward/cap/issue?reason=sync+envs&ttl_seconds=600
X-Actor: kswhitlock9493-jpg
```

**Response:**
```json
{
  "cap_token": "cap_abc123...",
  "ttl_seconds": 600,
  "actor": "kswhitlock9493-jpg",
  "reason": "sync envs"
}
```

### 5. Apply Plan (Admiral Only, Write Mode Required)

```bash
POST /api/steward/apply
Content-Type: application/json
X-Bridge-Cap: cap_abc123...
X-Actor: kswhitlock9493-jpg

{
  "plan": { ... },
  "confirm": true
}
```

**Response:**
```json
{
  "ok": true,
  "plan_id": "abc123...",
  "changes_applied": 5,
  "change_counts": {
    "created": 2,
    "updated": 3,
    "deleted": 0
  },
  "rollback_ref": "rollback_xyz789...",
  "errors": [],
  "timestamp": "2025-10-11T17:45:00.000000"
}
```

---

## Usage Flow

### Read-Only Mode (Default)

1. **Enable engine:**
   ```bash
   STEWARD_ENABLED=true
   ```

2. **Check drift:**
   ```bash
   curl -X POST http://localhost:8000/api/steward/diff?user_id=kswhitlock9493-jpg
   ```

3. **Create plan:**
   ```bash
   curl -X POST http://localhost:8000/api/steward/plan \
     -H "Content-Type: application/json" \
     -d '{"providers": ["render"]}'
   ```

### Write Mode (Admiral Only)

1. **Enable write mode:**
   ```bash
   STEWARD_WRITE_ENABLED=true
   STEWARD_RENDER_ENABLED=true  # Enable specific provider
   ```

2. **Add provider tokens** in platform dashboards (not in code)

3. **Issue capability:**
   ```bash
   curl -X POST "http://localhost:8000/api/steward/cap/issue?reason=sync+envs" \
     -H "X-Actor: kswhitlock9493-jpg"
   ```

4. **Apply plan:**
   ```bash
   curl -X POST http://localhost:8000/api/steward/apply \
     -H "Content-Type: application/json" \
     -H "X-Bridge-Cap: cap_..." \
     -H "X-Actor: kswhitlock9493-jpg" \
     -d '{"plan": {...}, "confirm": true}'
   ```

---

## Genesis Events

Steward publishes events to the Genesis bus for audit and orchestration:

| Topic | Description |
|-------|-------------|
| `steward.intent` | Diff or plan intention |
| `steward.plan` | Plan created with mutation window |
| `steward.apply` | Plan execution started |
| `steward.result` | Execution result (success/failure) |
| `steward.rollback` | Rollback triggered |
| `steward.cap.issued` | Capability token issued |

**Example event:**
```json
{
  "topic": "steward.result",
  "data": {
    "plan_id": "abc123...",
    "ok": true,
    "changes": {"created": 2, "updated": 3},
    "rollback_bundle": "rollback_xyz789..."
  }
}
```

---

## Testing

### Unit Tests

```bash
python3 -m pytest bridge_backend/tests/test_steward.py -v
```

### Integration Test (Manual)

```bash
# 1. Check status
curl http://localhost:8000/api/steward/status?user_id=kswhitlock9493-jpg

# 2. Check diff
curl -X POST "http://localhost:8000/api/steward/diff?user_id=kswhitlock9493-jpg"

# 3. Create plan
curl -X POST "http://localhost:8000/api/steward/plan?user_id=kswhitlock9493-jpg" \
  -H "Content-Type: application/json" \
  -d '{"providers": ["render"]}'
```

### Permission Tests

```bash
# Non-admiral should be denied
curl http://localhost:8000/api/steward/status?user_id=test_captain
# Expected: 403 {"detail": "steward_admiral_only"}

# Admiral should succeed
curl http://localhost:8000/api/steward/status?user_id=kswhitlock9493-jpg
# Expected: 200 {"enabled": true, ...}
```

---

## Security Guarantees

✅ **Default Deny** - Write is off unless explicitly enabled  
✅ **Admiral-Only** - Only owner can issue capabilities and apply changes  
✅ **Least Authority** - Only variables in Blueprint EnvSpec can be mutated  
✅ **No Secret Echo** - Values never logged; only hashes in events  
✅ **Loop-Safe** - Mutation windows + recursion checks prevent echo storms  
✅ **Short-Lived Caps** - Capability tokens expire (default: 10 minutes)  
✅ **Audit Trail** - All operations published to Genesis bus  

---

## Troubleshooting

### "steward_admiral_only" error

**Cause:** Non-admiral user trying to access steward endpoints  
**Solution:** Only the admiral (owner) can use steward. Check `STEWARD_OWNER_HANDLE` matches your username.

### "Steward engine is disabled"

**Cause:** `STEWARD_ENABLED` is not set to `true`  
**Solution:** Set `STEWARD_ENABLED=true` in environment variables

### "Write mode disabled"

**Cause:** `STEWARD_WRITE_ENABLED` is not set to `true`  
**Solution:** Set `STEWARD_WRITE_ENABLED=true` to enable writes (admiral only)

### "Missing X-Bridge-Cap header"

**Cause:** Trying to apply without capability token  
**Solution:** Issue a capability token first with `/api/steward/cap/issue`

### Adapter errors

**Cause:** Provider tokens or IDs not configured  
**Solution:** 
1. Enable the provider: `STEWARD_RENDER_ENABLED=true`
2. Add the service ID: `RENDER_SERVICE_ID=srv-...`
3. Add the API token in the platform dashboard (not in code)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Env Steward Engine                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │   Diff   │→ │   Plan   │→ │  Apply   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│       ↓              ↓              ↓                     │
│  ┌─────────────────────────────────────┐                │
│  │      Blueprint Validation            │                │
│  │      Truth Certification             │                │
│  │      Cascade Phasing                 │                │
│  └─────────────────────────────────────┘                │
│                      ↓                                    │
│  ┌─────────────────────────────────────┐                │
│  │         Provider Adapters            │                │
│  │  ┌────────┐ ┌────────┐ ┌────────┐  │                │
│  │  │ Render │ │Netlify │ │ GitHub │  │                │
│  │  └────────┘ └────────┘ └────────┘  │                │
│  └─────────────────────────────────────┘                │
│                      ↓                                    │
│  ┌─────────────────────────────────────┐                │
│  │         Genesis Event Bus            │                │
│  │   (steward.* topics for audit)       │                │
│  └─────────────────────────────────────┘                │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Best Practices

1. **Keep write mode OFF** until you need it
2. **Use short TTLs** for capability tokens (default: 10 minutes)
3. **Add provider tokens in dashboards** only, never in code or logs
4. **Review diffs** before creating plans
5. **Review plans** before applying
6. **Monitor Genesis events** for audit trail
7. **Test in read-only mode** first
8. **Use dry_run=true** when testing

---

## Next Steps

1. **Enable read-only mode** to start monitoring drift
2. **Review drift reports** to understand current state
3. **Create plans** to see proposed changes
4. **When ready for writes:**
   - Add provider tokens in dashboards
   - Enable write mode
   - Issue capability token
   - Apply plan

---

**Version:** v1.9.6l  
**Admiral-Tier:** Locked to owner only  
**Status:** Production-ready (read-only default, write requires explicit enablement)
