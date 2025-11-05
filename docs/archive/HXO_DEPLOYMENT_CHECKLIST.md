# HXO Deployment Checklist — v1.9.6n

**Version:** 1.9.6n  
**Target:** Production (Render + Netlify)  
**Risk Level:** Low (disabled by default, zero breaking changes)

---

## Pre-Deployment Checklist

### ✅ Code Quality
- [x] All modules import successfully
- [x] CAS ID computation validated (deterministic & unique)
- [x] Blueprint validation working (valid/invalid stages)
- [x] Genesis topics registered
- [x] HXO link registered in genesis_link.py
- [x] Routes included in main.py with proper gating

### ✅ Documentation
- [x] HXO_OVERVIEW.md (architecture)
- [x] HXO_OPERATIONS.md (ops guide)
- [x] HXO_BLUEPRINT_CONTRACT.md (schemas)
- [x] HXO_GENESIS_TOPICS.md (events)
- [x] HXO_QUICK_REF.md (quick reference)
- [x] HXO_IMPLEMENTATION_SUMMARY.md (delivery summary)

### ✅ Configuration
- [x] .env.example updated with 11 HXO variables
- [x] All config has safe defaults
- [x] HXO_ENABLED defaults to false (safe deploy)

### ✅ Safety Guards
- [x] Admiral-only mutating operations
- [x] Timeout guards (HXO_SHARD_TIMEOUT_MS)
- [x] Concurrency limits (HXO_MAX_CONCURRENCY)
- [x] Max shards cap (HXO_MAX_SHARDS)
- [x] Checkpoint integrity (SQLite transactions)
- [x] Audit trail (hxo.audit events)

---

## Deployment Steps

### Step 1: Merge to Main

```bash
# Ensure all commits are pushed
git push origin copilot/add-hypshard-x-orchestrator

# Create PR and merge to main
# Title: "v1.9.6n — Hypshard-X Orchestrator (HXO)"
```

### Step 2: Deploy to Render (Backend)

Render will auto-deploy on merge to main. Monitor deployment:

```bash
# Watch deployment logs
# Look for:
# [HXO] Disabled (set HXO_ENABLED=true to enable)
```

**Expected:** HXO is disabled by default, no impact on existing deployments.

### Step 3: Verify Backend Health

```bash
# Check health endpoint
curl https://sr-aibridge.onrender.com/health/ready

# Should return:
# {"status": "ready", "message": "Service is operational"}
```

### Step 4: Enable HXO (Optional, for testing)

In Render dashboard:

```bash
# Add environment variable
HXO_ENABLED=true

# Redeploy
```

Monitor logs:

```bash
# Look for:
# [HXO] v1.9.6n routes enabled - hypshard-x orchestrator active
```

### Step 5: Test HXO Endpoints

```bash
# Test status endpoint (should return 404 for non-existent plan)
curl https://sr-aibridge.onrender.com/api/hxo/status/test

# Expected: 404 with "Plan not found" message
```

### Step 6: Submit Test Plan (Admiral only)

```bash
curl -X POST https://sr-aibridge.onrender.com/api/hxo/create-and-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Admiral" \
  -d '{
    "name": "test_deploy",
    "stages": [
      {"id": "pack", "kind": "deploy.pack", "slo_ms": 120000}
    ],
    "constraints": {"max_shards": 100}
  }'

# Should return:
# {
#   "plan_id": "...",
#   "name": "test_deploy",
#   "status": "submitted",
#   "total_shards": N
# }
```

### Step 7: Monitor Test Plan

```bash
# Get status
curl https://sr-aibridge.onrender.com/api/hxo/status/{plan_id}

# Watch for completion
# done_shards should equal total_shards
```

### Step 8: Verify Checkpoint Persistence

```bash
# Check checkpoint DB exists
# In Render shell:
ls -lh /opt/render/project/src/bridge_backend/.hxo/checkpoints.db

# Should exist and have non-zero size
```

### Step 9: Test Abort (Admiral only)

```bash
# Submit another plan
curl -X POST https://sr-aibridge.onrender.com/api/hxo/create-and-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Admiral" \
  -d '{
    "name": "abort_test",
    "stages": [{"id": "pack", "kind": "deploy.pack"}]
  }'

# Abort it
curl -X POST https://sr-aibridge.onrender.com/api/hxo/abort/{plan_id} \
  -H "Authorization: Admiral"

# Should return:
# {"plan_id": "...", "status": "aborted"}
```

### Step 10: Verify Genesis Integration

```bash
# Check Genesis events
curl https://sr-aibridge.onrender.com/api/genesis/events?topic=hxo.plan

# Should return recent hxo.plan events
```

---

## Post-Deployment Monitoring

### Metrics to Track

| Metric | Target | Alert If |
|--------|--------|----------|
| HXO API response time | < 100ms | > 500ms |
| Shard completion rate | > 95% | < 90% |
| Failed shard ratio | < 1% | > 5% |
| Checkpoint DB size | < 100MB | > 500MB |
| Genesis event rate | < 1000/min | > 5000/min |

### Log Queries

```bash
# Find HXO errors
grep "ERROR.*\[HXO\]" logs/app.log

# Find failed shards
grep "hxo.shard.failed" logs/app.log

# Find auto-tune signals
grep "hxo.autotune.signal" logs/app.log
```

---

## Rollback Plan

If issues arise:

### Quick Disable

```bash
# In Render dashboard
HXO_ENABLED=false

# Redeploy
```

### Full Rollback

```bash
# Revert merge commit
git revert <merge_commit_sha>

# Push to main
git push origin main

# Render auto-deploys
```

### Abort In-Flight Plans

```bash
# Get all active plans
curl https://sr-aibridge.onrender.com/api/genesis/events?topic=hxo.plan

# Abort each
curl -X POST https://sr-aibridge.onrender.com/api/hxo/abort/{plan_id} \
  -H "Authorization: Admiral"
```

---

## Known Limitations (v1.9.6n)

1. **Replay Not Fully Implemented**: `/api/hxo/replay/{plan_id}` returns 501
2. **Mock Executors**: Current executors are mocks; real implementations pending
3. **Single-Process Only**: Federation hooks exist but not fully wired
4. **No UI Dashboard**: Status must be queried via API

These are **intentional** for v1.9.6n. Future versions will address.

---

## Success Criteria

Deployment is successful if:

- ✅ Backend deploys without errors
- ✅ Health checks pass
- ✅ HXO routes accessible (when enabled)
- ✅ Test plan submits and completes
- ✅ Checkpoint DB persists
- ✅ Genesis events published
- ✅ No performance degradation on existing endpoints

---

## Production Readiness (Optional)

To use HXO in production workflows:

1. **Implement Real Executors**: Replace mocks with actual work logic
2. **Wire TDE-X Integration**: Update TDE-X stages to use HXO
3. **Enable Auto-Tuning**: Connect Autonomy signals to real actions
4. **Dashboard**: Build UI for real-time monitoring
5. **Alerts**: Set up alerts for failed shards, timeout risks

---

## Support Contacts

**Issues**: Create GitHub issue with:
- Plan ID
- Timestamp
- Error logs
- HXO status output

**Emergency**: Disable HXO via `HXO_ENABLED=false`

---

## Deployment Sign-Off

- [ ] Code reviewed by Admiral
- [ ] Documentation reviewed
- [ ] Test plan executed successfully
- [ ] Rollback plan validated
- [ ] Monitoring dashboard ready
- [ ] Team notified of new feature

**Approved by:** _____________  
**Date:** _____________  
**Version Deployed:** v1.9.6n

---

**Status:** Ready for production deployment 🚀
