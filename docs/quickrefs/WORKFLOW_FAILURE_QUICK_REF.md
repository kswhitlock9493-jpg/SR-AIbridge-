# Workflow Failure Resolution - Quick Reference

## 🚀 Quick Commands

### Analyze All Workflows
```bash
python3 bridge_backend/tools/autonomy/failure_analyzer.py
```

### Generate Fix Plan
```bash
python3 bridge_backend/tools/autonomy/pr_generator.py \
  --plan bridge_backend/diagnostics/autofix_plan.json
```

### Apply Fixes (Use with Caution)
```bash
python3 bridge_backend/tools/autonomy/pr_generator.py \
  --plan bridge_backend/diagnostics/autofix_plan.json \
  --apply
```

## 🔧 Common Fixes

### Fix Browser Downloads
Add to your workflow:
```yaml
- uses: ./.github/actions/browser-setup
```

### Fix Deprecated Actions
Replace:
- `actions/upload-artifact@v3` → `@v4`
- `actions/download-artifact@v3` → `@v4`
- `actions/setup-node@v3` → `@v4`
- `actions/setup-python@v4` → `@v5`

### Fix Missing Timeouts
Add to long-running steps:
```yaml
- name: Build
  run: npm run build
  timeout-minutes: 10
```

## 📊 Priority Levels

- 🔴 **CRITICAL**: Browser downloads, auth failures
- 🟠 **HIGH**: Missing dependencies, auth issues
- 🟡 **MEDIUM**: Timeouts, health checks
- 🟢 **LOW**: Deprecated actions, style issues

## 🎯 Failure Patterns

| Pattern | Auto-Fix | Priority |
|---------|----------|----------|
| Browser download blocked | ✅ Yes | CRITICAL |
| Forge auth failure | ❌ No | HIGH |
| Deprecated actions | ✅ Yes | LOW |
| Container timeout | ✅ Yes | MEDIUM |
| Missing dependencies | ✅ Yes | HIGH |

## 🛠️ Troubleshooting

### Browser Install Fails
1. Use browser-setup action
2. Set `PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true`
3. Use Playwright instead of Puppeteer

### Workflow Still Fails
1. Check diagnostic artifacts
2. Review `failure_analysis.json`
3. Read `recommendations.md`
4. Check GitHub secrets configuration

### Analysis Tool Errors
1. Ensure Python 3.11+
2. Install dependencies: `pip install PyYAML tabulate`
3. Run from repo root directory

## 📁 Key Files

| File | Purpose |
|------|---------|
| `failure_analysis.json` | Full analysis report |
| `autofix_plan.json` | Generated fix plan |
| `recommendations.md` | Human-readable fixes |
| `forensics_report.json` | Workflow forensics data |

## 🔍 GitHub Actions

### Run Diagnostic Sweep
1. Go to Actions tab
2. Select "Sovereign Diagnostic Sweep"
3. Click "Run workflow"
4. Download artifacts

### Use Browser Setup
```yaml
jobs:
  build:
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/browser-setup
      - run: npm run build
```

## ⚡ Environment Variables

### Browser Configuration
```bash
PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
PUPPETEER_SKIP_DOWNLOAD=true
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=false
PLAYWRIGHT_BROWSERS_PATH=0
```

### Forge Integration
```bash
FORGE_DOMINION_ROOT=${{ secrets.FORGE_DOMINION_ROOT }}
DOMINION_SEAL=${{ secrets.DOMINION_SEAL }}
```

## 📞 Support

1. Check [WORKFLOW_FAILURE_RESOLUTION.md](./WORKFLOW_FAILURE_RESOLUTION.md)
2. Review diagnostic artifacts
3. Create issue with `failure_analysis.json`

---

**Quick Tip**: Run analysis after every workflow change to catch issues early!
