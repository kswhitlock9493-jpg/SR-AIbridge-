# HXO Deployment Guide — Render/Netlify/GitHub

**Version:** v1.9.6p  
**Purpose:** Production deployment procedures for HXO Ascendant

---

## Overview

HXO v1.9.6p supports deployment across:
- **Render** — Backend API and database
- **Netlify** — Frontend deployment
- **GitHub Actions** — CI/CD automation

---

## Prerequisites

### Required Secrets

Add these to your deployment platform:

```bash
# Core
SECRET_KEY=<generate-secure-random-32-chars>
SEED_SECRET=<generate-secure-random-32-chars>

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# HXO Configuration
HXO_ENABLED=true
HXO_MAX_SHARDS=1000000
HXO_HEAL_DEPTH_LIMIT=5
HXO_ZERO_TRUST=true
HXO_PREDICTIVE_MODE=true
HXO_EVENT_CACHE_LIMIT=10000
HXO_QUANTUM_HASHING=true
HXO_ZDU_ENABLED=true
HXO_ALIR_ENABLED=true
HXO_CONSENSUS_MODE=HARMONIC
HXO_FEDERATION_TIMEOUT=5000
HXO_AUTO_AUDIT_AFTER_DEPLOY=true
```

---

## Render Deployment

### 1. Backend Service

**Service Configuration:**

```yaml
# render.yaml
services:
  - type: web
    name: sr-aibridge-backend
    runtime: python
    region: oregon
    plan: standard
    buildCommand: |
      cd bridge_backend
      pip install -r requirements.txt
    startCommand: |
      cd bridge_backend
      uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4
    envVars:
      - key: HXO_ENABLED
        value: true
      - key: HXO_MAX_CONCURRENCY
        value: 64
      - key: HXO_ZERO_TRUST
        value: true
      - key: HXO_CONSENSUS_MODE
        value: HARMONIC
      - key: GENESIS_ENABLED
        value: true
      - key: DATABASE_URL
        fromDatabase:
          name: sr-aibridge-db
          property: connectionString
```

**Timeout Mitigation:**

HXO automatically shards work to avoid Render's 30-minute build timeout:

```python
# HXO automatically handles this
# No manual intervention needed
# Plans > 30 min are automatically sharded
```

### 2. Database Service

```yaml
# render.yaml (continued)
databases:
  - name: sr-aibridge-db
    databaseName: sr_aibridge_main
    user: sr_bridge_user
    plan: standard
    region: oregon
```

**Database Initialization:**

```bash
# Render will auto-run migrations via start command
# Or manually trigger:
curl -X POST https://your-app.onrender.com/api/system/migrate
```

---

## Netlify Deployment

### Frontend Configuration

**netlify.toml:**

```toml
[build]
  base = "bridge-frontend"
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "20"
  VITE_API_URL = "https://sr-aibridge-backend.onrender.com"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[functions]
  node_bundler = "esbuild"
```

**Environment Variables:**

```bash
# In Netlify dashboard, add:
VITE_API_URL=https://your-backend.onrender.com
VITE_HXO_ENABLED=true
```

### Deploy Trigger

HXO can trigger Netlify deployments via Genesis events:

```bash
# Enable deploy hooks
export NETLIFY_DEPLOY_HOOK=https://api.netlify.com/build_hooks/...

# HXO will auto-trigger on successful backend deploy
```

---

## GitHub Actions Integration

### CI/CD Workflow

Create `.github/workflows/hxo_deploy.yml`:

```yaml
name: HXO Ascendant Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          cd bridge_backend
          pip install -r requirements.txt
          pip install pytest
      
      - name: Run HXO tests
        run: |
          cd bridge_backend
          pytest tests/test_hxo_planner.py -v
      
      - name: Validate HXO Federation
        run: |
          cd bridge_backend
          python -m bridge_backend.cli.hxoctl verify --deep --certify
  
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Render Deploy
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
      
      - name: Wait for deploy
        run: sleep 60
      
      - name: Run post-deploy ARIE audit
        if: env.HXO_AUTO_AUDIT_AFTER_DEPLOY == 'true'
        run: |
          curl -X POST https://your-backend.onrender.com/api/arie/scan \
            -H "Authorization: Bearer ${{ secrets.ADMIRAL_TOKEN }}"
```

### Required Secrets

In GitHub repository settings → Secrets:

```
RENDER_DEPLOY_HOOK
NETLIFY_DEPLOY_HOOK
ADMIRAL_TOKEN
```

---

## Zero-Downtime Deployment

### Strategy

HXO v1.9.6p supports zero-downtime deployments via:

1. **Blue-Green Deployment**
2. **Rolling Updates**
3. **Schema Migration Coordination**

### Blue-Green Setup

```yaml
# render.yaml
services:
  - type: web
    name: sr-aibridge-blue
    # ... config ...
  
  - type: web
    name: sr-aibridge-green
    # ... config ...
```

**Deployment Flow:**

```bash
# 1. Deploy to Green (inactive)
curl -X POST $RENDER_DEPLOY_HOOK_GREEN

# 2. Wait for HXO health check
curl https://green.onrender.com/api/hxo/status

# 3. Verify federation links
curl https://green.onrender.com/api/hxo/links/health

# 4. Switch traffic
# Update DNS/load balancer to Green

# 5. Drain Blue
curl -X POST https://blue.onrender.com/api/hxo/graceful-shutdown
```

### Rolling Update

For single-service deployments:

```bash
# 1. Trigger deploy
curl -X POST $RENDER_DEPLOY_HOOK

# 2. HXO automatically:
#    - Completes active plans
#    - Checkpoints state
#    - Gracefully shuts down
#    - New version starts
#    - Rehydrates incomplete plans
```

---

## Schema Migrations

### Before Deployment

```bash
# 1. Generate migration
cd bridge_backend
alembic revision --autogenerate -m "Add HXO v1.9.6p tables"

# 2. Review migration
cat alembic/versions/xxx_add_hxo_tables.py

# 3. Test locally
alembic upgrade head

# 4. Commit migration
git add alembic/versions/
git commit -m "Add HXO v1.9.6p schema migration"
```

### During Deployment

HXO's Zero-Downtime Upgrade (ZDU) handles schema migrations:

```python
# HXO automatically:
# 1. Detects schema version mismatch
# 2. Waits for active plans to complete
# 3. Applies migration
# 4. Resumes operations
```

**Manual Override:**

```bash
# If migration takes > 5 minutes, increase timeout
export HXO_MIGRATION_TIMEOUT=600  # 10 minutes

# Or run migration separately before deploy
alembic upgrade head
```

---

## Post-Deployment Verification

### 1. Health Checks

```bash
# Overall status
curl https://your-app.onrender.com/health

# HXO specific
curl https://your-app.onrender.com/api/hxo/status

# Engine federation
curl https://your-app.onrender.com/api/hxo/links/health
```

### 2. Run ARIE Audit

```bash
curl -X POST https://your-app.onrender.com/api/arie/scan \
  -H "Authorization: Bearer $ADMIRAL_TOKEN"
```

### 3. Verify Metrics

```bash
# Genesis Bus
curl https://your-app.onrender.com/api/genesis/metrics

# HXO telemetry
curl https://your-app.onrender.com/api/hxo/metrics
```

### 4. Test Plan Submission

```bash
curl -X POST https://your-app.onrender.com/api/hxo/create-and-submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Admiral" \
  -d '{
    "name": "test_deploy",
    "stages": [
      {"id": "test", "kind": "deploy.pack", "slo_ms": 60000}
    ]
  }'
```

---

## Monitoring

### Render Metrics

Enable Render's built-in monitoring:

```yaml
# render.yaml
services:
  - type: web
    name: sr-aibridge-backend
    healthCheckPath: /health
    autoDeploy: true
    
    # Alert thresholds
    alerts:
      - type: cpu
        threshold: 80
      - type: memory
        threshold: 80
```

### Custom Alerts

HXO publishes alerts to Genesis Bus:

```bash
# Subscribe to alerts
curl https://your-app.onrender.com/api/genesis/subscribe/hxo.alert
```

**Alert Types:**
- `guardian.halt` — Recursion limit reached
- `consensus.failure` — Harmonic consensus failed
- `certification.failure` — Truth certification failed
- `federation.degraded` — Engine link unhealthy

---

## Rollback Procedure

### Quick Rollback

In Render dashboard:
1. Go to service → Deploys
2. Find previous successful deploy
3. Click "Rollback to this version"

### HXO-Aware Rollback

```bash
# 1. Get rollback points
curl https://your-app.onrender.com/api/hxo/deployments/rollback-points

# 2. Trigger rollback
curl -X POST https://your-app.onrender.com/api/hxo/rollback \
  -H "Content-Type: application/json" \
  -d '{"deployment_id": "deploy_xxx"}'

# 3. Wait for completion
curl https://your-app.onrender.com/api/hxo/status
```

---

## Performance Optimization

### Render-Specific

```bash
# Use standard+ plan for better CPU
# Enable persistent disk for SQLite checkpoints
# Use same region for DB and web service

# In render.yaml:
services:
  - type: web
    plan: standard
    disk:
      name: hxo-vault
      mountPath: /opt/render/project/src/bridge_backend/.hxo
      sizeGB: 10
```

### HXO Tuning

```bash
# Production settings
export HXO_MAX_CONCURRENCY=64
export HXO_SHARD_TIMEOUT_MS=15000
export HXO_AUTOSPLIT_P95_MS=8000

# For large deploys
export HXO_MAX_CONCURRENCY=128
export HXO_MAX_SHARDS=2000000
```

---

## Security Hardening

### Production Checklist

- [x] `HXO_ZERO_TRUST=true`
- [x] `HXO_QUANTUM_HASHING=true`
- [x] `HXO_CONSENSUS_MODE=HARMONIC`
- [x] `SECRET_KEY` rotated every 90 days
- [x] Database credentials in Render secrets
- [x] HTTPS enforced (automatic on Render)
- [x] CORS configured for frontend only
- [x] Rate limiting enabled
- [x] ARIE auto-audits enabled

### Secret Rotation

```bash
# 1. Generate new secret
NEW_SECRET=$(openssl rand -hex 32)

# 2. Update in Render dashboard
# Settings → Environment → SECRET_KEY

# 3. Trigger redeploy
curl -X POST $RENDER_DEPLOY_HOOK

# 4. Verify
curl https://your-app.onrender.com/health
```

---

## Troubleshooting Deployments

### Build Timeout

If build exceeds 30 minutes:

```bash
# HXO automatically shards long builds
# No action needed

# To verify sharding is working:
curl https://your-app.onrender.com/api/hxo/metrics | jq '.build_shards'
```

### Database Connection Errors

```bash
# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql+asyncpg://...

# Test connection
curl https://your-app.onrender.com/api/db/health
```

### Genesis Bus Not Starting

```bash
# Ensure enabled
export GENESIS_ENABLED=true

# Check logs
curl https://your-app.onrender.com/api/logs/genesis | tail -50
```

---

## Cost Optimization

### Render Costs

- **Standard plan:** ~$25/month (recommended for production)
- **Standard Plus:** ~$85/month (high-traffic production)
- **Database:** ~$7-50/month depending on size

### HXO Optimizations

```bash
# Reduce shard count to save CPU
export HXO_MAX_SHARDS=100000

# Reduce TERC to save memory
export HXO_EVENT_CACHE_LIMIT=5000

# Disable predictive features in low-traffic environments
export HXO_PREDICTIVE_MODE=false
export HXO_ALIR_ENABLED=false
```

---

## Deployment Checklist

Pre-Deploy:
- [ ] All tests passing
- [ ] ARIE audit clean
- [ ] Database migrations tested
- [ ] Secrets configured
- [ ] Rollback plan ready

Deploy:
- [ ] Trigger deployment
- [ ] Monitor health checks
- [ ] Verify engine federation
- [ ] Run smoke tests
- [ ] Check logs for errors

Post-Deploy:
- [ ] Run ARIE audit
- [ ] Verify metrics
- [ ] Test critical paths
- [ ] Monitor for 1 hour
- [ ] Update documentation

---

**Status:** ✅ Complete  
**Last Updated:** 2025-10-11
