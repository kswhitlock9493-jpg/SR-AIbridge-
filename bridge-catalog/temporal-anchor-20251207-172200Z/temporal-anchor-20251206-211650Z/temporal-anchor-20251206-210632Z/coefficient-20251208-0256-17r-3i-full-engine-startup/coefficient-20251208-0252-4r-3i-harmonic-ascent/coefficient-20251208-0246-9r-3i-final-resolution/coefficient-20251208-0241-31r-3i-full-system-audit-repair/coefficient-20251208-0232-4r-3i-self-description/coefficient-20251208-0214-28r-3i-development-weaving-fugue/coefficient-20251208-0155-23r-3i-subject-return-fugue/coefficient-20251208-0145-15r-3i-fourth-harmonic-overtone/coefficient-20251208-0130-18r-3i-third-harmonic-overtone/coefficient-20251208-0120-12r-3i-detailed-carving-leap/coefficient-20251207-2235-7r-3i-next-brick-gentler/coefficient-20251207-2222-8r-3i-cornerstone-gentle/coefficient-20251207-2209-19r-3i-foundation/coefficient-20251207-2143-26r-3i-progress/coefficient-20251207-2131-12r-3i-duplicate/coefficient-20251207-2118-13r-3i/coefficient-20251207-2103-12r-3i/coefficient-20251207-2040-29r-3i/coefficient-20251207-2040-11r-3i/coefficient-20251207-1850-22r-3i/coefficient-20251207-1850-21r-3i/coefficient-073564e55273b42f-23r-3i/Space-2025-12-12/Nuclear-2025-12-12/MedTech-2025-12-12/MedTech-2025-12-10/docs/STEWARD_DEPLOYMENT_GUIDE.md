# Env Steward v1.9.6l — Deployment Guide

## Admiral-Tier Environment Orchestration

This guide walks you through deploying and using the Env Steward engine.

---

## Overview

**Env Steward** provides:

✅ **Default Deny** - Write is off unless you actively mint a short-lived capability  
✅ **Least Authority** - Only variables present in Blueprint EnvSpec can be created/updated  
✅ **No Secret Echo** - Values never logged; ciphertext stored in Vault; only hashes in events  
✅ **Loop-Safe** - Mutation window IDs + Guardian recursion checks block echo storms  
✅ **Admiral-Tier Lock** - Only the owner (admiral) can access steward features  

---

## Pre-Deployment Checklist

- [x] All steward files committed to repository
- [x] Genesis bus topics registered
- [x] Permissions middleware updated
- [x] Routes registered in main.py
- [x] Environment variables documented in .env.example
- [x] Tests created and verified

---

## Deployment Steps

### 1. Ship to Main

Merge the PR to main:

```bash
git checkout main
git merge copilot/update-env-steward-feature
git push origin main
```

Render will auto-deploy in ~2-3 minutes.

### 2. Enable Engine (Read-Only)

Add these environment variables in **Render Dashboard** → **Environment**:

```bash
STEWARD_ENABLED=true
STEWARD_WRITE_ENABLED=false  # Keep false for read-only mode
STEWARD_CAP_TTL_SECONDS=600
STEWARD_OWNER_HANDLE=kswhitlock9493-jpg

# Provider toggles (keep false for now)
STEWARD_RENDER_ENABLED=false
STEWARD_NETLIFY_ENABLED=false
STEWARD_GITHUB_ENABLED=false

# Provider identifiers (non-secret, safe to add)
RENDER_SERVICE_ID=srv-d39k3ejuibrs73etqnag
NETLIFY_SITE_ID=
GITHUB_REPO_SLUG=kswhitlock9493-jpg/SR-AIbridge-
```

**Save** and wait for Render to redeploy.

### 3. Verify Deployment

Check that the engine is running:

```bash
curl https://sr-aibridge.onrender.com/api/steward/status
```

Expected response:
```json
{
  "enabled": true,
  "write_enabled": false,
  "owner_handle": "kswhitlock9493-jpg",
  "cap_ttl_seconds": 600
}
```

### 4. Test Diff/Plan (Read-Only)

Compute drift across providers:

```bash
curl -X POST "https://sr-aibridge.onrender.com/api/steward/diff?user_id=kswhitlock9493-jpg"
```

Create a plan:

```bash
curl -X POST "https://sr-aibridge.onrender.com/api/steward/plan?user_id=kswhitlock9493-jpg" \
  -H "Content-Type: application/json" \
  -d '{"providers": ["render"], "strategy": "safe-phased"}'
```

---

## Optional: Enable Write Mode

⚠️ **Only when you're ready to make actual environment changes.**

### 5. Add Provider Tokens

In **Render/Netlify/GitHub Dashboards** (not in code), add:

**Render Dashboard** → **Environment**:
```bash
RENDER_API_TOKEN=<your-render-api-token>
```

**Netlify Dashboard** → **Environment variables**:
```bash
NETLIFY_AUTH_TOKEN=<your-netlify-auth-token>
```

**GitHub** → **Settings** → **Secrets and variables** → **Actions**:
```bash
GITHUB_TOKEN=<your-github-token>
```

### 6. Enable Write Mode

In **Render Dashboard** → **Environment**, update:

```bash
STEWARD_WRITE_ENABLED=true
STEWARD_RENDER_ENABLED=true  # Enable specific provider(s)
```

**Save** and wait for redeploy.

### 7. Issue Capability Token

```bash
curl -X POST "https://sr-aibridge.onrender.com/api/steward/cap/issue?reason=sync+envs&ttl_seconds=600" \
  -H "X-Actor: kswhitlock9493-jpg"
```

Response:
```json
{
  "cap_token": "cap_abc123...",
  "ttl_seconds": 600,
  "actor": "kswhitlock9493-jpg",
  "reason": "sync envs"
}
```

**Save this token** (it expires in 10 minutes).

### 8. Apply Plan

```bash
curl -X POST "https://sr-aibridge.onrender.com/api/steward/apply" \
  -H "Content-Type: application/json" \
  -H "X-Bridge-Cap: cap_abc123..." \
  -H "X-Actor: kswhitlock9493-jpg" \
  -d '{
    "plan": {
      "id": "...",
      "providers": ["render"],
      "strategy": "safe-phased",
      "phases": [...],
      "mutation_window_id": "...",
      "certified": true
    },
    "confirm": true
  }'
```

### 9. Monitor Genesis Events

Watch the Genesis bus for audit trail:

```bash
curl "https://sr-aibridge.onrender.com/genesis/events?topic=steward.result"
```

---

## Security Notes

### Admiral-Only Access

All steward endpoints are locked to admiral role. Non-admiral users receive:

```json
{
  "detail": "steward_admiral_only"
}
```

This is enforced at **three levels**:

1. **Permissions Middleware** - Blocks `/api/steward/*` for non-admirals
2. **RBAC Matrix** - Admiral has `steward.read`, `steward.cap.issue`, `steward.write`
3. **Core Engine** - Validates actor against `STEWARD_OWNER_HANDLE`

### Capability Tokens

- **Short-lived** (default: 10 minutes)
- **Bound to mutation window** (plan-specific)
- **Single-use** (window closes after apply)
- **Checked by Permission Engine** and Guardians

### Secret Handling

- Values **never logged**
- Secrets stored as **ciphertext in Vault**
- Events contain only **hashes**, never plaintext
- Provider tokens added only in **platform dashboards**, never in code

---

## Rollback

Every apply operation creates a rollback bundle:

```json
{
  "rollback_ref": "rollback_xyz789..."
}
```

To rollback (future feature):

```bash
curl -X POST "https://sr-aibridge.onrender.com/api/cascade/rollback?id=rollback_xyz789..."
```

---

## Monitoring

### Genesis Events

Subscribe to steward topics for audit:

- `steward.intent` - Diff/plan requests
- `steward.plan` - Plan created
- `steward.apply` - Apply started
- `steward.result` - Apply completed
- `steward.rollback` - Rollback triggered
- `steward.cap.issued` - Capability issued

### Health Check

```bash
curl https://sr-aibridge.onrender.com/api/steward/status
```

Check `enabled` and `write_enabled` status.

---

## Troubleshooting

### Deployment Issues

**Problem:** Steward routes not found  
**Solution:** Check `STEWARD_ENABLED=true` in environment

**Problem:** "steward_admiral_only" error  
**Solution:** Ensure `user_id=kswhitlock9493-jpg` matches `STEWARD_OWNER_HANDLE`

### Write Mode Issues

**Problem:** "Write mode disabled"  
**Solution:** Set `STEWARD_WRITE_ENABLED=true`

**Problem:** Adapter errors  
**Solution:** 
1. Enable provider: `STEWARD_RENDER_ENABLED=true`
2. Add service ID: `RENDER_SERVICE_ID=srv-...`
3. Add API token in platform dashboard

**Problem:** "Missing X-Bridge-Cap header"  
**Solution:** Issue capability token first with `/api/steward/cap/issue`

---

## Ops Playbook

### Daily Operations

1. **Check drift** (automated via Genesis subscriptions)
2. **Review plans** (manual or triggered by autonomy)
3. **Apply changes** (admiral-only, requires capability)

### Emergency Rollback

1. Get rollback ref from `steward.result` event
2. Call `/api/cascade/rollback?id=<ref>`
3. Verify state in providers

### Capability Management

- **Default TTL:** 10 minutes
- **Max TTL:** 600 seconds (configurable via `STEWARD_CAP_TTL_SECONDS`)
- **Issuance:** Admiral-only
- **Validation:** Checked by Permission Engine + Guardians

---

## What's Next?

### Phase 1: Read-Only Monitoring (Current)

- ✅ Drift detection
- ✅ Plan creation
- ✅ Genesis event publishing
- ✅ Admiral-tier lock

### Phase 2: Write Mode (Optional)

- Add provider tokens
- Enable write mode
- Test apply operations
- Monitor rollback bundles

### Phase 3: Autonomy Integration (Future)

- Autonomy can **request plans**
- Admiral **reviews and approves**
- Autonomy **cannot apply** without owner capability

---

## Support

For issues or questions:

1. Check `STEWARD_QUICK_REF.md` for API usage
2. Review Genesis events for audit trail
3. Check Render logs for errors
4. Verify environment variables in dashboard

---

**Version:** v1.9.6l  
**Status:** Production-Ready (Read-Only Default)  
**Admiral-Tier:** Locked to Owner Only  
**Write Mode:** Off by Default (Requires Explicit Enablement)
