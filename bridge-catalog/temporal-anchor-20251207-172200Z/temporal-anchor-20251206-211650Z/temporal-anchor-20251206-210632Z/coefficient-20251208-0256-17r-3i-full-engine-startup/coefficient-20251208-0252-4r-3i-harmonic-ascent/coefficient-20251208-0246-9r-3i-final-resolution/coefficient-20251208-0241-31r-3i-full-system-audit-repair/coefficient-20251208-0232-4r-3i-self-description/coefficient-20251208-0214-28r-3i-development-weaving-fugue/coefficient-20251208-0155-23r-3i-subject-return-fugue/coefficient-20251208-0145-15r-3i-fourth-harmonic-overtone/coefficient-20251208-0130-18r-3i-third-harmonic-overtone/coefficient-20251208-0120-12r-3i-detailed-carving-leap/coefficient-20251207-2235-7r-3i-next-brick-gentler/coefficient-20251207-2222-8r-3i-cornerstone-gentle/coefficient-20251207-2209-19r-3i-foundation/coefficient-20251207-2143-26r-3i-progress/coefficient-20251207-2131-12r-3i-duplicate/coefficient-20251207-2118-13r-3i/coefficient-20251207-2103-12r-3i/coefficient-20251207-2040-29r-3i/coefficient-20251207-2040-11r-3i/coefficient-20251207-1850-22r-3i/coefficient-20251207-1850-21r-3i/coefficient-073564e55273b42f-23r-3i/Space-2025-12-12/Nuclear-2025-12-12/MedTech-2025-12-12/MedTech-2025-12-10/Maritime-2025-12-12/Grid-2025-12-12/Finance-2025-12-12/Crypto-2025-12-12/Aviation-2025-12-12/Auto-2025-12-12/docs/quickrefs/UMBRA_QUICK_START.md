# Umbra Unified Triage Mesh - Quick Start

## 🚀 Getting Started in 5 Minutes

### 1. Enable Umbra (Intent-Only Mode)

Add to your `.env`:
```bash
UMBRA_ENABLED=true
UMBRA_ALLOW_HEAL=false  # Intent-only: generates plans but doesn't execute
```

Restart your application.

### 2. Test Signal Ingestion

```bash
curl -X POST http://localhost:8000/api/umbra/signal \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "deploy",
    "source": "test",
    "message": "Test deploy failure",
    "severity": "warning"
  }'
```

### 3. View Tickets

```bash
# Via API
curl http://localhost:8000/api/umbra/tickets

# Via CLI
python3 -m bridge_backend.cli.umbractl tickets
```

### 4. Run Triage Sweep

```bash
python3 -m bridge_backend.cli.umbractl run --report
```

### 5. View Report

```bash
cat bridge_backend/logs/umbra_reports/latest.json
```

## 🎯 Common Tasks

### Configure Webhooks

**Netlify**:
1. Netlify Dashboard → Site Settings → Build & Deploy → Deploy notifications
2. Add webhook: `https://your-backend.com/webhooks/netlify`
3. (Optional) Set `NETLIFY_DEPLOY_WEBHOOK_SECRET` in `.env`

**Render**:
1. Render Dashboard → Service → Settings → Webhooks
2. Add webhook: `https://your-backend.com/webhooks/render`
3. (Optional) Set `RENDER_WEBHOOK_SECRET` in `.env`

**GitHub**:
1. GitHub Repo → Settings → Webhooks
2. Add webhook: `https://your-backend.com/webhooks/github`
3. Events: Workflow runs, Check suites, Deployment statuses
4. (Optional) Set `GITHUB_WEBHOOK_SECRET` in `.env`

### Enable Autonomous Healing

```bash
# In .env
UMBRA_ALLOW_HEAL=true
AUTO_HEAL_ON=true
UMBRA_RBAC_MIN_ROLE=admiral
```

⚠️ **Warning**: Only enable in production after thorough testing in staging!

### View Tickets by Status

```bash
# Open tickets
python3 -m bridge_backend.cli.umbractl tickets --status open

# Healed tickets
python3 -m bridge_backend.cli.umbractl tickets --status healed

# All tickets
python3 -m bridge_backend.cli.umbractl tickets
```

### Execute Healing Manually

```bash
# Get ticket ID from list
python3 -m bridge_backend.cli.umbractl tickets

# Heal specific ticket
python3 -m bridge_backend.cli.umbractl ticket UM-2025-10-12-0001 --action heal
```

## 📊 Understanding Health Scores

| Score | Status | Action |
|-------|--------|--------|
| 95-100% | ✅ Excellent | Safe to merge |
| 80-94% | ✅ Good | Review and merge |
| 60-79% | ⚠️ Fair | Fix issues before merge |
| 0-59% | ❌ Poor | Do not merge |

Health score factors:
- **50%**: Self-test pass rate
- **30%**: Umbra incident severity
- **20%**: Heal success rate

## 🔧 Key Configuration

### Minimal Configuration
```bash
UMBRA_ENABLED=true
UMBRA_ALLOW_HEAL=false
```

### Recommended Production
```bash
UMBRA_ENABLED=true
UMBRA_ALLOW_HEAL=true
UMBRA_ALLOW_UNVERIFIED_WEBHOOKS=false
UMBRA_PARITY_STRICT=true
UMBRA_RBAC_MIN_ROLE=admiral
UMBRA_HEALTH_ERROR_THRESHOLD=5
UMBRA_HEALTH_WARN_THRESHOLD=2

# Set these if using webhooks
RENDER_WEBHOOK_SECRET=your_secret
NETLIFY_DEPLOY_WEBHOOK_SECRET=your_secret
GITHUB_WEBHOOK_SECRET=your_secret
```

## 🛠️ Troubleshooting

### No tickets appearing?
- Check `UMBRA_ENABLED=true`
- Verify signals are being sent
- Check logs: `bridge_backend/logs/`

### Webhooks not working?
- Verify webhook URL is correct
- Check webhook secret matches
- Or set `UMBRA_ALLOW_UNVERIFIED_WEBHOOKS=true` (not for production)

### Heal plans not executing?
- Set `UMBRA_ALLOW_HEAL=true`
- Ensure user has Admiral role
- Check Truth certification is passing

### PR comments not appearing?
- Workflow needs `pull-requests: write` permission
- Check `actions/github-script@v7` is working
- Verify summary.md file is generated

## 📚 Documentation

- [Overview](./UMBRA_OVERVIEW.md) - Architecture and concepts
- [Operations](./UMBRA_OPERATIONS.md) - Detailed operational guide
- [Migration](./TRIAGE_MESH_MIGRATION.md) - Migrating from old systems
- [PR Health](./PR_HEALTH_SUMMARY.md) - Understanding PR annotations

## 🎓 Learning Path

1. **Day 1**: Enable intent-only mode, observe tickets
2. **Day 2-3**: Configure webhooks, test signal ingestion
3. **Day 4-5**: Review heal plans, understand correlation
4. **Week 2**: Enable healing in staging
5. **Week 3**: Monitor staging, adjust thresholds
6. **Week 4**: Enable healing in production with strict RBAC

## ⚡ Quick Commands Reference

```bash
# Status
curl http://localhost:8000/api/umbra/status

# Ingest signal
curl -X POST http://localhost:8000/api/umbra/signal -d '{"kind":"deploy","source":"test","message":"Test","severity":"info"}'

# List tickets
python3 -m bridge_backend.cli.umbractl tickets

# Run sweep
python3 -m bridge_backend.cli.umbractl run --report

# View latest report
python3 -m bridge_backend.cli.umbractl report --latest

# Generate PR summary
python3 bridge_backend/cli/selftest_summary.py \
  --selftest logs/selftest_reports/latest.json \
  --umbra logs/umbra_reports/latest.json \
  --out-md summary.md \
  --out-json summary.json
```

## 🔒 Security Best Practices

1. ✅ Always use webhook secrets in production
2. ✅ Keep `UMBRA_RBAC_MIN_ROLE=admiral`
3. ✅ Enable `UMBRA_PARITY_STRICT=true`
4. ✅ Require Truth certification
5. ✅ Never set `UMBRA_ALLOW_UNVERIFIED_WEBHOOKS=true` in production
6. ✅ Review heal plans before enabling autonomous mode
7. ✅ Monitor Genesis events for audit trail
8. ✅ Archive reports for compliance

## 💡 Pro Tips

- Start with intent-only mode to build confidence
- Use Genesis events for real-time monitoring
- Archive old reports to prevent disk filling
- Tune thresholds based on your environment
- Review PR health scores as part of code review
- Use CLI for quick diagnostics
- Enable strict parity for critical environments
- Test rollback procedures regularly

## 🆘 Need Help?

1. Check logs in `bridge_backend/logs/umbra_reports/`
2. Review Genesis events for detailed flow
3. Use `umbractl` for diagnostics
4. Consult full documentation in `docs/`
5. Check existing test files for examples

## 🎉 Success Indicators

You're using Umbra successfully when:
- ✅ Tickets appear automatically for deploy failures
- ✅ Related incidents are correlated into single tickets
- ✅ Heal plans make sense for the issue type
- ✅ PR health scores reflect actual system state
- ✅ Autonomous healing resolves issues without manual intervention
- ✅ Rollbacks work when healing fails
- ✅ Truth certification validates all actions
- ✅ Team trusts the health scores for merge decisions
