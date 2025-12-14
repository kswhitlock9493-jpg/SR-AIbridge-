# Bridge Health Record System — Quick Reference

## 🩺 v1.9.7l Overview

Automated health tracking with persistent metrics and live status badges.

---

## 🚀 Quick Commands

### Generate Health Record
```bash
python3 bridge_backend/metrics/health_record.py \
  --selftest bridge_backend/logs/selftest_reports/latest.json \
  --umbra bridge_backend/logs/umbra_reports/latest.json \
  --output-dir bridge_backend/logs/health_history/
```

### Generate Badge
```bash
python3 bridge_backend/cli/badgegen.py \
  --input bridge_backend/logs/health_history/latest.json \
  --out-md docs/badges/bridge_health.md \
  --out-svg docs/badges/bridge_health.svg
```

### View Latest Health
```bash
cat bridge_backend/logs/health_history/latest.json
cat bridge_backend/logs/health_history/latest.md
```

---

## 📊 Health Score Formula

| Component | Weight | Formula |
|-----------|--------|---------|
| **Selftest Pass Rate** | 50% | `(passed / total) * 50` |
| **Umbra Issues** | 30% | `score - ((criticals * 10) + (warnings * 3))` |
| **Heal Success** | 20% | `(healed / total_attempts) * 20` |

**Final Score**: `max(0, min(100, score))`

---

## 🎨 Badge Colors

| Score Range | Color | Status | Emoji |
|-------------|-------|--------|-------|
| ≥ 95% | 🟢 Green | Passing | `brightgreen` |
| 80-94% | 🟡 Yellow | Warning | `yellow` |
| < 80% | 🔴 Red | Critical | `red` |

---

## 📂 File Locations

```
bridge_backend/
├── metrics/
│   ├── __init__.py
│   └── health_record.py         # Health aggregation
├── cli/
│   └── badgegen.py              # Badge generation
└── logs/
    └── health_history/
        ├── latest.json          # Current health snapshot
        ├── latest.md            # Current health markdown
        └── health_*.json        # Historical records (90 days)

docs/
└── badges/
    ├── bridge_health.svg        # Live badge (auto-updated)
    ├── bridge_health.md         # Badge documentation
    └── README.md                # Directory info
```

---

## 🔄 Data Retention

| Age | Action |
|-----|--------|
| New | Store as `health_YYYYMMDD_HHMMSS.json` |
| 7 days | Auto-compress to `.json.gz` |
| 90 days | Auto-delete |
| Latest | Always keep as `latest.json` |

---

## 🧪 Testing

```bash
# Run all health record tests
pytest bridge_backend/tests/test_health_record.py -v

# Run all badge tests
pytest bridge_backend/tests/test_badgegen.py -v

# Run both
pytest bridge_backend/tests/test_health_record.py bridge_backend/tests/test_badgegen.py -v
```

**Expected**: 33 tests pass (17 + 16)

---

## 📋 Sample Output

### Health Record JSON
```json
{
  "timestamp": "2025-10-13T00:10:00Z",
  "bridge_health_score": 100,
  "auto_heals": 0,
  "truth_certified": true,
  "status": "passing"
}
```

### Badge Display
```markdown
![Bridge Health](docs/badges/bridge_health.svg)
```

Result: 🟢 Bridge Health: 100% (Truth Certified)

---

## 🔧 CI Integration

The workflow automatically:
1. Runs self-tests and Umbra triage
2. Generates health record
3. Creates badge SVG/Markdown
4. Commits badge updates to repo

**Triggers**:
- Pull requests
- Push to main
- Every 72 hours
- Manual dispatch

---

## 🛠️ Troubleshooting

### Badge not updating
```bash
# Check latest health record exists
ls -l bridge_backend/logs/health_history/latest.json

# Manually regenerate badge
python3 bridge_backend/cli/badgegen.py \
  --input bridge_backend/logs/health_history/latest.json \
  --out-md docs/badges/bridge_health.md \
  --out-svg docs/badges/bridge_health.svg
```

### Missing health data
```bash
# Check source reports exist
ls -l bridge_backend/logs/selftest_reports/latest.json
ls -l bridge_backend/logs/umbra_reports/latest.json

# Manually generate health record
python3 bridge_backend/metrics/health_record.py \
  --selftest bridge_backend/logs/selftest_reports/latest.json \
  --umbra bridge_backend/logs/umbra_reports/latest.json \
  --output-dir bridge_backend/logs/health_history/
```

### Low health score
Check the breakdown:
```bash
cat bridge_backend/logs/health_history/latest.json | jq '{score: .bridge_health_score, selftest: .selftest, umbra: .umbra}'
```

---

## 🔐 Security Notes

- Health records do NOT contain secrets
- Badge generation runs under RBAC captain+
- Only truth-certified reports are recorded
- Historical data excluded from git (in `.gitignore`)

---

## 📈 Future Enhancements

- [ ] Health trend charts
- [ ] Email alerts on critical status
- [ ] Steward dashboard integration
- [ ] Historical health reports
- [ ] Slack/Discord notifications

---

**Version**: v1.9.7l  
**Status**: ✅ Complete  
**Documentation**: [V197L_IMPLEMENTATION_SUMMARY.md](V197L_IMPLEMENTATION_SUMMARY.md)
