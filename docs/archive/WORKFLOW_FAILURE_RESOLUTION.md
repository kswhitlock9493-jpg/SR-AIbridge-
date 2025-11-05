# Workflow Failure Resolution Framework

## Overview

This framework provides automated tools and workflows to identify, diagnose, and resolve GitHub Actions workflow failures across the SR-AIBridge ecosystem. It implements the **Sovereign Diagnostic Sweep Initiative** for total workflow domination.

## Components

### 1. Browser Dependency Resolution

**Purpose**: Resolve firewall restrictions on browser downloads (Chrome/Chromium).

#### Reusable Workflow
- **File**: `.github/workflows/firewall-bypass.yml`
- **Usage**: Call from other workflows to set up browser dependencies
- **Features**:
  - Installs Playwright and Chromium
  - Configures environment variables to skip Puppeteer downloads
  - Works in firewall-restricted environments
  - Verifies browser installation

#### Composite Action
- **File**: `.github/actions/browser-setup/action.yml`
- **Usage**: Use as a step in workflows
- **Example**:
```yaml
steps:
  - uses: ./.github/actions/browser-setup
    with:
      skip-chromium: false
      install-deps: true
```

### 2. Sovereign Diagnostic Sweep

**Purpose**: Automatically scan all workflows for common failure patterns.

- **File**: `.github/workflows/sovereign-diagnostic-sweep.yml`
- **Triggers**:
  - Manual dispatch (`workflow_dispatch`)
  - Scheduled (every 6 hours)
- **Features**:
  - Scans all 60+ workflow files
  - Identifies deprecated actions
  - Detects browser configuration issues
  - Finds missing timeouts
  - Generates fix recommendations
  - Uploads diagnostic artifacts

### 3. Failure Pattern Analyzer

**Purpose**: Python tool to analyze workflow files for common failure patterns.

- **File**: `bridge_backend/tools/autonomy/failure_analyzer.py`
- **Usage**:
```bash
python3 bridge_backend/tools/autonomy/failure_analyzer.py \
  --input .github/workflows \
  --output bridge_backend/diagnostics/failure_analysis.json
```
- **Detects**:
  - Browser download blocks
  - Forge authentication failures
  - Container health timeouts
  - Deprecated actions
  - Missing dependencies
  - Timeout issues
  - Environment mismatches

### 4. PR Generator

**Purpose**: Generate automated fixes for detected workflow issues.

- **File**: `bridge_backend/tools/autonomy/pr_generator.py`
- **Usage**:
```bash
# Dry run (default)
python3 bridge_backend/tools/autonomy/pr_generator.py \
  --plan bridge_backend/diagnostics/autofix_plan.json

# Apply fixes
python3 bridge_backend/tools/autonomy/pr_generator.py \
  --plan bridge_backend/diagnostics/autofix_plan.json \
  --apply
```
- **Features**:
  - Auto-fixes deprecated actions
  - Adds browser configuration
  - Generates recommendations
  - Safe by default (dry-run mode)

### 5. Failure Patterns Configuration

**Purpose**: Centralized configuration of failure patterns and solutions.

- **File**: `bridge_backend/tools/autonomy/failure_patterns.py`
- **Patterns**:
  - `browser_download_blocked` (CRITICAL)
  - `forge_auth_failure` (HIGH)
  - `container_health_timeout` (MEDIUM)
  - `deprecated_actions` (LOW)
  - `missing_dependencies` (HIGH)
  - `timeout_issues` (MEDIUM)
  - `environment_mismatch` (MEDIUM)

## Quick Start

### Running Diagnostic Sweep

1. **Manual Trigger**:
   - Go to Actions tab in GitHub
   - Select "Sovereign Diagnostic Sweep"
   - Click "Run workflow"

2. **Review Results**:
   - Download "workflow-diagnostic-results" artifact
   - Check `workflow_scan_results.json` for detected issues
   - Check `autofix_plan.json` for fix recommendations

### Using Browser Setup in Workflows

**Before** (problematic):
```yaml
- name: Build frontend
  run: cd bridge-frontend && npm run build
```

**After** (fixed):
```yaml
- name: Setup Browsers
  uses: ./.github/actions/browser-setup
  
- name: Build frontend
  run: cd bridge-frontend && npm run build
```

### Running Local Analysis

```bash
# Analyze workflows
python3 bridge_backend/tools/autonomy/failure_analyzer.py

# Review the report
cat bridge_backend/diagnostics/failure_analysis.json

# Generate fixes (dry run)
python3 bridge_backend/tools/autonomy/pr_generator.py \
  --plan bridge_backend/diagnostics/autofix_plan.json
```

## Workflow Failure Patterns

### Pattern: Browser Download Blocked

**Symptoms**:
- `googlechromelabs.github.io` connection failures
- `storage.googleapis.com` timeouts
- Chromium download errors

**Solution**:
1. Use Playwright system browsers
2. Skip Puppeteer downloads
3. Configure environment variables

**Auto-fixable**: ✅ Yes

### Pattern: Forge Auth Failure

**Symptoms**:
- `FORGE_DOMINION_ROOT` missing
- `DOMINION_SEAL` not found
- Authentication errors

**Solution**:
1. Configure GitHub secrets
2. Add environment variables to workflows

**Auto-fixable**: ❌ No (requires secrets)

### Pattern: Deprecated Actions

**Symptoms**:
- Using `@v3` of actions
- Deprecation warnings

**Solution**:
1. Update to `@v4` or later
2. Review breaking changes

**Auto-fixable**: ✅ Yes

## Monitoring and Alerts

### Success Criteria

**Phase 1** (Immediate):
- ✅ 0 browser firewall failures
- ✅ All deprecated actions updated
- ✅ Browser setup standardized

**Phase 2** (Continuous):
- ✅ Autonomous healing active
- ✅ Zero critical failures
- ✅ All workflows passing

### Metrics

The diagnostic sweep provides:
- Total workflows scanned
- Issues by severity (Critical, High, Medium, Low)
- Auto-fixable vs. manual intervention required
- Affected files and recommended actions

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Sovereign Diagnostic Sweep                  │
│                  (Scheduled + Manual Trigger)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   Failure Pattern Analyzer    │
         │  (Scan .github/workflows)     │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │   Generate Fix Plan           │
         │   (autofix_plan.json)         │
         └───────────┬───────────────────┘
                     │
            ┌────────┴────────┐
            ▼                 ▼
    ┌──────────────┐  ┌──────────────┐
    │  Auto-Fix    │  │   Manual     │
    │  (Low/Med)   │  │   Review     │
    │              │  │   (High/Crit)│
    └──────────────┘  └──────────────┘
```

## Files Created

### Workflows
- `.github/workflows/firewall-bypass.yml` - Reusable browser setup workflow
- `.github/workflows/sovereign-diagnostic-sweep.yml` - Automated diagnostic sweep

### Actions
- `.github/actions/browser-setup/action.yml` - Browser setup composite action
- `.github/actions/workflow-forensics/action.yml` - Workflow analysis action

### Tools
- `bridge_backend/tools/autonomy/failure_analyzer.py` - Pattern analyzer
- `bridge_backend/tools/autonomy/pr_generator.py` - Fix generator
- `bridge_backend/tools/autonomy/failure_patterns.py` - Pattern definitions
- `bridge_backend/tools/autonomy/__init__.py` - Module initialization

### Output
- `bridge_backend/diagnostics/failure_analysis.json` - Analysis report
- `bridge_backend/diagnostics/autofix_plan.json` - Fix plan
- `bridge_backend/diagnostics/fix_summary.json` - Fix summary
- `bridge_backend/diagnostics/recommendations.md` - Human-readable recommendations

## Contributing

When adding new failure patterns:

1. Update `failure_patterns.py` with pattern definition
2. Add detection regex
3. Define fix template
4. Set priority and auto-fixable flag
5. Test with sample workflow

## Security

- All auto-fixes are logged
- Dry-run mode by default
- No secrets are modified by automation
- Manual approval required for HIGH/CRITICAL issues

## Support

For issues or questions:
1. Check the diagnostic artifacts
2. Review `recommendations.md`
3. Run local analysis with `--verbose` flag
4. Create an issue with the failure_analysis.json attached

---

**Status**: ✅ Operational
**Version**: 1.0.0
**Last Updated**: 2025-11-04
