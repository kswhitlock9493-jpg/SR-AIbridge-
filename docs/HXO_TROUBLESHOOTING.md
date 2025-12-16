# HXO Troubleshooting Guide

**Version:** v1.9.6p  
**Purpose:** Diagnostics, recovery, and common issue resolution

---

## Quick Diagnostics

### Check HXO Status

```bash
curl http://localhost:8000/api/hxo/status
```

Expected response:
```json
{
  "enabled": true,
  "version": "1.9.6p",
  "active_plans": 2,
  "total_shards_pending": 50,
  "total_shards_running": 10,
  "total_shards_complete": 1000,
  "engine_health": {
    "autonomy": "healthy",
    "blueprint": "healthy",
    "truth": "healthy",
    "cascade": "healthy",
    "federation": "healthy",
    "parser": "healthy",
    "leviathan": "healthy",
    "arie": "healthy",
    "envrecon": "healthy"
  }
}
```

---

## Common Issues

### Issue: HXO Not Starting

**Symptoms:**
- `/api/hxo/*` endpoints return 404
- Logs show: "HXO disabled, skipping initialization"

**Diagnosis:**
```bash
# Check if HXO is enabled
grep HXO_ENABLED .env
```

**Solution:**
```bash
# Enable HXO
export HXO_ENABLED=true

# Restart backend
pm2 restart bridge-backend
```

---

### Issue: Plans Stuck in PENDING

**Symptoms:**
- Plans created but never start executing
- No shards transition to RUNNING

**Diagnosis:**
```bash
# Check active plans
curl http://localhost:8000/api/hxo/status/{plan_id}

# Check logs
tail -f bridge_backend/logs/hxo.log | grep -i "error\|warning"
```

**Common Causes:**
1. **Genesis Bus disabled** → HXO can't receive events
2. **Blueprint validation failure** → Plan rejected by schema validator
3. **Truth consensus failure** → Harmonic consensus timeout

**Solution:**
```bash
# Enable Genesis Bus
export GENESIS_ENABLED=true

# Check Blueprint status
curl http://localhost:8000/api/blueprint/status

# Check Truth Engine
curl http://localhost:8000/api/truth/status

# Retry plan
curl -X POST http://localhost:8000/api/hxo/plan/{plan_id}/retry
```

---

### Issue: High Shard Failure Rate

**Symptoms:**
- Many shards transition to FAILED
- Excessive healing loops triggered

**Diagnosis:**
```bash
# Get plan metrics
curl http://localhost:8000/api/hxo/report/{plan_id}

# Check failure reasons
sqlite3 bridge_backend/.hxo/checkpoints.db \
  "SELECT error_msg, COUNT(*) FROM shards WHERE phase='failed' GROUP BY error_msg"
```

**Common Causes:**
1. **Resource exhaustion** → Too many concurrent shards
2. **Timeout too aggressive** → Shards need more time
3. **Executor bugs** → Code errors in executor logic

**Solutions:**
```bash
# Reduce concurrency
export HXO_MAX_CONCURRENCY=32  # Down from 64

# Increase shard timeout
export HXO_SHARD_TIMEOUT_MS=30000  # 30 seconds

# Increase SLO
export HXO_DEFAULT_SLO_MS=180000  # 3 minutes

# Restart backend
pm2 restart bridge-backend
```

---

### Issue: Guardian Halt Triggered

**Symptoms:**
- Logs show: "Guardian halt triggered for plan {id}"
- Plan status: `GUARDIAN_HALTED`
- Email/alert received about recursion limit

**Diagnosis:**
```bash
# Check healing depth
curl http://localhost:8000/api/hxo/plan/{plan_id}/healing-history

# View Guardian events
curl http://localhost:8000/api/hxo/guardian/events?plan_id={plan_id}
```

**Cause:** Healing loop exceeded `HXO_HEAL_DEPTH_LIMIT` (default: 5)

**Solution:**
```bash
# Review healing chain to identify root cause
curl http://localhost:8000/api/hxo/plan/{plan_id}/healing-chain

# If legitimate, increase limit (use caution)
export HXO_HEAL_DEPTH_LIMIT=7

# Cancel halted plan
curl -X POST http://localhost:8000/api/hxo/plan/{plan_id}/cancel

# Fix root cause and resubmit
```

---

### Issue: Merkle Certification Failures

**Symptoms:**
- Truth Engine rejects Merkle proofs
- Plans complete but not certified
- Audit trail shows certification failures

**Diagnosis:**
```bash
# Check Truth Engine status
curl http://localhost:8000/api/truth/status

# Verify Merkle tree
curl http://localhost:8000/api/hxo/plan/{plan_id}/merkle-tree
```

**Common Causes:**
1. **Shard result corruption** → Data integrity issue
2. **Truth Engine unavailable** → Service down
3. **Consensus timeout** → Network/performance issue

**Solutions:**
```bash
# Verify shard results integrity
curl http://localhost:8000/api/hxo/plan/{plan_id}/verify-shards

# Increase federation timeout
export HXO_FEDERATION_TIMEOUT=10000  # 10 seconds

# Retry certification
curl -X POST http://localhost:8000/api/hxo/plan/{plan_id}/certify

# If persistent, check Truth Engine logs
tail -f bridge_backend/logs/truth.log
```

---

### Issue: Zero-Downtime Upgrade Fails

**Symptoms:**
- Schema migration during deployment fails
- Services experience downtime
- Blueprint reports conflicts

**Diagnosis:**
```bash
# Check Blueprint migration status
curl http://localhost:8000/api/blueprint/migrations/status

# Check active plans during upgrade
curl http://localhost:8000/api/hxo/status | jq '.active_plans'
```

**Solutions:**
```bash
# Ensure ZDU is enabled
export HXO_ZDU_ENABLED=true

# Wait for active plans to complete before schema changes
curl http://localhost:8000/api/hxo/wait-for-idle?timeout=300

# If stuck, perform graceful shutdown
curl -X POST http://localhost:8000/api/hxo/graceful-shutdown
```

---

### Issue: TERC Memory Pressure

**Symptoms:**
- High memory usage
- OOM kills
- Slow event lookups

**Diagnosis:**
```bash
# Check TERC size
curl http://localhost:8000/api/hxo/terc/stats

# Memory usage
free -h
ps aux | grep python | grep bridge
```

**Solution:**
```bash
# Reduce TERC limit
export HXO_EVENT_CACHE_LIMIT=5000  # Down from 10000

# Clear old events
curl -X POST http://localhost:8000/api/hxo/terc/prune?older_than=3600

# Restart backend
pm2 restart bridge-backend
```

---

## Performance Tuning

### Optimize for Throughput

```bash
# Increase concurrency
export HXO_MAX_CONCURRENCY=128

# Reduce autosplit threshold (split sooner)
export HXO_AUTOSPLIT_P95_MS=5000

# Increase autosplit factor (more parallelism)
export HXO_AUTOSPLIT_FACTOR=8
```

### Optimize for Reliability

```bash
# Reduce concurrency (less load)
export HXO_MAX_CONCURRENCY=32

# Increase timeouts
export HXO_SHARD_TIMEOUT_MS=30000
export HXO_DEFAULT_SLO_MS=180000

# Enable all safety features
export HXO_ZERO_TRUST=true
export HXO_QUANTUM_HASHING=true
export HXO_CONSENSUS_MODE=HARMONIC
```

### Optimize for Cost

```bash
# Reduce resource usage
export HXO_MAX_CONCURRENCY=16
export HXO_MAX_SHARDS=100000
export HXO_EVENT_CACHE_LIMIT=1000

# Disable expensive features (development only!)
export HXO_PREDICTIVE_MODE=false
export HXO_ALIR_ENABLED=false
```

---

## Health Checks

### Engine Link Health

```bash
# Check all engine links
curl http://localhost:8000/api/hxo/links/health

# Test specific link
curl http://localhost:8000/api/hxo/links/health/autonomy
```

### Database Health

```bash
# Check checkpoint DB
sqlite3 bridge_backend/.hxo/checkpoints.db "PRAGMA integrity_check"

# Vacuum if needed
sqlite3 bridge_backend/.hxo/checkpoints.db "VACUUM"

# Check size
du -h bridge_backend/.hxo/checkpoints.db
```

### Shard Health

```bash
# View shard distribution
curl http://localhost:8000/api/hxo/metrics/shard-distribution

# Check for stuck shards
curl http://localhost:8000/api/hxo/metrics/stuck-shards

# Retry stuck shards
curl -X POST http://localhost:8000/api/hxo/retry-stuck-shards
```

---

## Recovery Procedures

### Recover Incomplete Plans After Crash

HXO automatically rehydrates incomplete plans on startup. To manually trigger:

```bash
# List incomplete plans
curl http://localhost:8000/api/hxo/incomplete-plans

# Rehydrate specific plan
curl -X POST http://localhost:8000/api/hxo/rehydrate/{plan_id}

# Rehydrate all
curl -X POST http://localhost:8000/api/hxo/rehydrate-all
```

### Rollback Failed Deployment

```bash
# Get rollback points
curl http://localhost:8000/api/hxo/plan/{plan_id}/rollback-points

# Trigger rollback
curl -X POST http://localhost:8000/api/hxo/plan/{plan_id}/rollback \
  -H "Content-Type: application/json" \
  -d '{"checkpoint": "checkpoint_id_here"}'
```

### Clear Stale Data

```bash
# Remove completed plans older than 30 days
curl -X DELETE http://localhost:8000/api/hxo/cleanup?older_than_days=30

# Remove failed plans older than 7 days
curl -X DELETE http://localhost:8000/api/hxo/cleanup/failed?older_than_days=7
```

---

## Debug Mode

Enable verbose logging:

```bash
# Enable debug logs
export LOG_LEVEL=debug
export HXO_DEBUG=true

# Restart
pm2 restart bridge-backend

# Tail logs
tail -f bridge_backend/logs/hxo.log
```

---

## Emergency Procedures

### Stop All HXO Operations

```bash
# Emergency shutdown
curl -X POST http://localhost:8000/api/hxo/emergency-shutdown

# Verify stopped
curl http://localhost:8000/api/hxo/status
```

### Disable HXO Temporarily

```bash
export HXO_ENABLED=false
pm2 restart bridge-backend
```

### Reset HXO Completely

⚠️ **WARNING: This deletes all plans, shards, and checkpoints!**

```bash
# Backup first
cp bridge_backend/.hxo/checkpoints.db /tmp/hxo_backup_$(date +%s).db

# Reset
rm -rf bridge_backend/.hxo/*
curl -X POST http://localhost:8000/api/hxo/reset

# Restart
pm2 restart bridge-backend
```

---

## Support

If issues persist:

1. **Collect diagnostics:**
   ```bash
   curl http://localhost:8000/api/hxo/diagnostics > hxo_diagnostics.json
   ```

2. **Review logs:**
   ```bash
   tail -n 1000 bridge_backend/logs/hxo.log > hxo_logs.txt
   ```

3. **Check Genesis events:**
   ```bash
   curl http://localhost:8000/api/hxo/terc?limit=100 > terc_events.json
   ```

4. **Submit issue** with diagnostics attached

---

**Status:** ✅ Complete  
**Last Updated:** 2025-10-11
