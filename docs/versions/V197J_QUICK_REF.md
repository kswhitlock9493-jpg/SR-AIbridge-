# v1.9.7j Quick Reference — Bridge Autonomy Diagnostic Pulse

## 🚀 Quick Start

### Run Self-Test Manually

```bash
# With auto-healing (default)
python3 -m bridge_backend.cli.genesisctl self_test_full --heal

# Without auto-healing
python3 -m bridge_backend.cli.genesisctl self_test_full --no-heal
```

### View Latest Report

```bash
cat bridge_backend/logs/selftest_reports/latest.json
```

### Check Specific Engine

```bash
jq '.events | map(select(.engine == "EnvRecon"))' bridge_backend/logs/selftest_reports/latest.json
```

## 📊 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SELFTEST_ENABLED` | `true` | Enable/disable self-test |
| `AUTO_HEAL_ON` | `true` | Enable/disable auto-healing |
| `AUTOHEAL_MAX_RETRIES` | `3` | Max healing retry attempts |
| `AUTOHEAL_RETRY_DELAY` | `1.0` | Delay between retries (seconds) |

## 🧩 Architecture

### Components

1. **Self-Test Controller** - Orchestrates full synthetic deploy tests
2. **Auto-Heal Trigger** - Launches targeted micro-repairs
3. **Genesis Integration** - Event bus topics for monitoring
4. **Truth Certification** - Verifies all healing actions

### Healing Strategies

| Strategy | Engines | Purpose |
|----------|---------|---------|
| **ARIE** | EnvRecon, EnvScribe, Firewall | Configuration healing |
| **Chimera** | Chimera, Leviathan, Federation | Deployment repair |
| **Cascade** | Truth, Cascade, Genesis, HXO | System recovery |
| **Generic** | All others | Basic reinitialization |

## 📋 Genesis Event Topics

- `selftest.run.start` - Test started
- `selftest.run.complete` - Test completed
- `selftest.autoheal.trigger` - Healing initiated
- `selftest.autoheal.complete` - Healing completed

## 📊 Expected Metrics

| Metric | Target |
|--------|--------|
| Total Engines | 31 |
| Certified by Truth | 31 |
| Auto-Heals Executed | ≤ 3 |
| Verification Status | ✅ Stable |
| Average Runtime | < 0.5s |

## 🔍 Common Tasks

### Check Test Status

```bash
jq '.summary.status' bridge_backend/logs/selftest_reports/latest.json
```

### Count Failed Engines

```bash
jq '.events | map(select(.result | contains("❌"))) | length' bridge_backend/logs/selftest_reports/latest.json
```

### List Healing Events

```bash
jq '.events | map(select(.action == "repair_patch_applied"))' bridge_backend/logs/selftest_reports/latest.json
```

### Get Healing Statistics

```bash
jq '.summary | {verified: .engines_verified, total: .engines_total, heals: .autoheal_invocations}' bridge_backend/logs/selftest_reports/latest.json
```

## 🔒 Security & Governance

| Role | Capability |
|------|-----------|
| Admiral | Full command (start/stop test, approve cert) |
| Captain+ | Execute tests & view reports |
| Observer | Read-only results |

## 🧪 Testing

### Run Self-Test Tests

```bash
python3 -m pytest tests/test_selftest_v197j.py -v
```

### Validate Workflow

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/bridge_selftest.yml')); print('✅ Valid')"
```

## 📚 Documentation

- **Overview**: `docs/SELFTEST_OVERVIEW.md`
- **Auto-Heal Logic**: `docs/SELFTEST_HEALING_AUTOTRIGGER.md`
- **Report Schema**: `docs/SELFTEST_REPORT_SCHEMA.md`

## 🛠️ Troubleshooting

### Self-Test Disabled

```bash
export SELFTEST_ENABLED=true
python3 -m bridge_backend.cli.genesisctl self_test_full
```

### Auto-Heal Not Working

```bash
export AUTO_HEAL_ON=true
python3 -m bridge_backend.cli.genesisctl self_test_full --heal
```

### Increase Retry Attempts

```bash
export AUTOHEAL_MAX_RETRIES=5
export AUTOHEAL_RETRY_DELAY=2.0
python3 -m bridge_backend.cli.genesisctl self_test_full
```

## 🔄 GitHub Actions Integration

The workflow runs automatically:
- ✅ On every push to `main`
- ✅ Every 72 hours via scheduled cron
- ✅ Manual trigger via Actions tab

View workflow: `.github/workflows/bridge_selftest.yml`

## 📈 Report Schema

```json
{
  "test_id": "bridge_selftest_YYYYMMDD_HHMMSS",
  "summary": {
    "engines_total": 31,
    "engines_verified": 31,
    "autoheal_invocations": 0,
    "status": "Stable",
    "runtime_ms": 350
  },
  "events": [...],
  "timestamp": "2024-10-12T12:34:56.789Z"
}
```

## ⚡ Performance Tips

1. Run with `--no-heal` for faster diagnostics
2. Use `jq` for efficient report querying
3. Check `latest.json` instead of searching by timestamp
4. Monitor `runtime_ms` for performance regressions

## 🎯 Key Features

✅ **Autonomous**: Self-deploys, self-tests, self-heals, self-certifies
✅ **Comprehensive**: Validates all 31 engines
✅ **Certified**: Truth Engine verification required
✅ **Auditable**: Complete event trail in Genesis ledger
✅ **Continuous**: Runs every 72 hours automatically
✅ **Observable**: Full metrics in Steward dashboard

---

**Version**: v1.9.7j  
**Status**: Production Ready ✅  
**Last Updated**: 2024-10-12
