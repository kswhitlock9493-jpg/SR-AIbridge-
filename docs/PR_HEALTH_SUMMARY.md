# PR Health Summary Format

## Overview

Every pull request and scheduled CI run gets an automated health summary comment powered by Umbra Triage Mesh. This document describes the format and interpretation of these summaries.

## Example Output

### Excellent Health (95-100%)

```markdown
### 🤖 Bridge Health: 100%

✅ **Excellent** - All systems nominal

**Self-Test Results:**
- Total: 150 tests
- Passed: 150 ✅
- Engines certified: 31/31 ✅

**Umbra Triage (last run):**
- No incidents detected ✅

**Truth Certification:** ✅

**Rollbacks:** 0

**Artifacts:** `bridge_diagnostic_bundle`
```

### Good Health (80-94%)

```markdown
### 🤖 Bridge Health: 87%

✅ **Good** - Minor issues detected

**Self-Test Results:**
- Total: 150 tests
- Passed: 145 ✅
- Failed: 5 ❌
- Engines certified: 31/31 ✅

**Umbra Triage (last run):**
- Warnings: 2 ⚠️
- Heal plans generated: 2 (intent-mode)

**Truth Certification:** ✅

**Rollbacks:** 0

**Artifacts:** `bridge_diagnostic_bundle`
```

### Fair Health (60-79%)

```markdown
### 🤖 Bridge Health: 72%

⚠️ **Fair** - Some issues need attention

**Self-Test Results:**
- Total: 150 tests
- Passed: 130 ✅
- Failed: 20 ❌
- Engines certified: 29/31 ✅

**Umbra Triage (last run):**
- Critical incidents: 1 ❌
- Warnings: 4 ⚠️
- Auto-heals applied: 3 🩹

**Truth Certification:** ✅

**Rollbacks:** 1

**Artifacts:** `bridge_diagnostic_bundle`
```

### Poor Health (<60%)

```markdown
### 🤖 Bridge Health: 45%

❌ **Poor** - Critical issues detected

**Self-Test Results:**
- Total: 150 tests
- Passed: 90 ✅
- Failed: 60 ❌
- Engines certified: 25/31 ✅

**Umbra Triage (last run):**
- Critical incidents: 5 ❌
- Warnings: 8 ⚠️
- Auto-heals applied: 4 🩹
- Failed heals: 2 ❌

**Truth Certification:** ❌

**Rollbacks:** 3

**Artifacts:** `bridge_diagnostic_bundle`
```

## Health Score Calculation

The health score (0-100) is calculated from three components:

### 1. Self-Test Pass Rate (50% weight)

```
score += (passed_tests / total_tests) * 50
```

Example:
- 100/100 tests passed = 50 points
- 80/100 tests passed = 40 points
- 50/100 tests passed = 25 points

### 2. Umbra Issue Penalties (30% weight)

```
penalty = (critical_count * 10) + (warning_count * 3)
score -= min(penalty, 30)
```

Example:
- 0 critical, 0 warnings = 0 penalty
- 1 critical, 2 warnings = 16 penalty
- 3 critical, 5 warnings = 45 penalty (capped at 30)

### 3. Heal Success Rate (20% weight)

```
if total_heal_attempts > 0:
    score += (healed / total_heal_attempts) * 20
else:
    score += 20  # No attempts = full credit
```

Example:
- 5/5 heals succeeded = 20 points
- 3/5 heals succeeded = 12 points
- 0/5 heals succeeded = 0 points

## Health Indicators

| Score | Indicator | Meaning |
|-------|-----------|---------|
| 95-100% | ✅ **Excellent** | All systems nominal, ready to merge |
| 80-94% | ✅ **Good** | Minor issues, safe to merge with review |
| 60-79% | ⚠️ **Fair** | Issues need attention before merge |
| 0-59% | ❌ **Poor** | Critical issues, do not merge |

## Components Breakdown

### Self-Test Results

```markdown
**Self-Test Results:**
- Total: {total_tests} tests
- Passed: {passed_tests} ✅
- Failed: {failed_tests} ❌       # Only shown if > 0
- Engines certified: {active}/{total} ✅
```

- **Total**: Number of self-test checks run
- **Passed**: Tests that passed
- **Failed**: Tests that failed (omitted if 0)
- **Engines certified**: Number of engines that passed certification

### Umbra Triage

```markdown
**Umbra Triage (last run):**
- No incidents detected ✅                        # If no issues
# OR
- Critical incidents: {count} ❌                  # If > 0
- Warnings: {count} ⚠️                            # If > 0
- Auto-heals applied: {count} 🩹                  # If > 0
- Heal plans generated: {count} (intent-mode)    # If plans but no heals
```

- **No incidents detected**: Clean run, no triage tickets
- **Critical incidents**: Number of critical-severity tickets
- **Warnings**: Number of warning-severity tickets
- **Auto-heals applied**: Number of successfully executed heal plans
- **Heal plans generated**: Plans created in intent-only mode

### Truth Certification

```markdown
**Truth Certification:** ✅    # Passed
**Truth Certification:** ❌    # Failed
```

Indicates whether Truth Engine certified all operations.

### Rollbacks

```markdown
**Rollbacks:** {count}
```

Number of automatic rollbacks due to failed heal attempts.

### Artifacts

```markdown
**Artifacts:** `bridge_diagnostic_bundle`
```

Link to downloadable artifacts containing:
- Self-test reports (`bridge_backend/logs/selftest_reports/`)
- Umbra reports (`bridge_backend/logs/umbra_reports/`)

## JSON Summary Format

The workflow also generates a JSON summary at `bridge_backend/logs/selftest_reports/summary.json`:

```json
{
  "timestamp": "2025-10-12T23:00:00.000Z",
  "health_score": 87,
  "selftest": {
    "total_tests": 150,
    "passed_tests": 145,
    "failed_tests": 5,
    "engines_total": 31,
    "engines_active": 31
  },
  "umbra": {
    "critical_count": 0,
    "warning_count": 2,
    "tickets_opened": 2,
    "tickets_healed": 0,
    "tickets_failed": 0,
    "heal_plans_generated": 2,
    "heal_plans_applied": 0,
    "rollbacks": 0
  }
}
```

This can be consumed by other tools for trend analysis, dashboards, etc.

## Interpreting Results

### When to Merge

**Safe to merge**:
- Health score ≥ 95%
- No critical incidents
- Truth certified
- Zero rollbacks

**Merge with review**:
- Health score 80-94%
- Only warnings (no criticals)
- Truth certified
- Minimal rollbacks

**Do not merge**:
- Health score < 80%
- Any critical incidents
- Truth certification failed
- Multiple rollbacks

### Common Scenarios

#### Scenario: New Feature PR

```
Health: 92%
- 3 new tests added, all passing
- 1 warning: "New endpoint not yet in health checks"
- Heal plan generated: "Add endpoint to HealthNet"
```

**Action**: Safe to merge. Warning is expected for new features.

#### Scenario: Dependency Update

```
Health: 67%
- 15 tests failing
- 2 critical: "Breaking API changes detected"
- 0 heals applied (incompatible changes)
```

**Action**: Do not merge. Dependency introduces breaking changes.

#### Scenario: Configuration Change

```
Health: 78%
- All tests passing
- 3 warnings: "Netlify/Render config drift"
- 3 heals applied successfully
```

**Action**: Review heal actions, then merge. Drift was automatically corrected.

#### Scenario: Autonomous Healing Success

```
Health: 100%
- All tests passing
- 1 critical detected and auto-healed
- Truth certified
```

**Action**: Safe to merge. Umbra detected and fixed the issue automatically.

## Viewing Detailed Reports

To see full details:

1. **Download Artifacts**:
   - Click "bridge_diagnostic_bundle" in workflow run
   - Extract ZIP file
   - Review JSON reports

2. **Self-Test Report**:
   - `selftest_reports/latest.json`
   - Contains all test results and engine status

3. **Umbra Report**:
   - `umbra_reports/latest.json`
   - Contains all tickets, incidents, heal plans

## Customization

To customize the summary format, edit:
- `bridge_backend/cli/selftest_summary.py`

Key functions:
- `calculate_health_score()` - Adjust scoring logic
- `generate_markdown_summary()` - Modify markdown format
- `generate_json_summary()` - Change JSON structure

## Troubleshooting

### Summary Not Generated

**Check**:
1. Workflow has permissions: `pull-requests: write`
2. Python script executed successfully
3. Input JSON files exist

### Wrong Health Score

**Verify**:
1. Self-test report has correct test counts
2. Umbra report has accurate incident counts
3. Scoring weights in `calculate_health_score()`

### Missing PR Comment

**Check**:
1. Workflow triggered on PR event
2. `actions/github-script@v7` step succeeded
3. Summary markdown file exists

## Best Practices

1. **Set CI as Required**: Make "Bridge Health" check required for PRs
2. **Monitor Trends**: Track health scores over time
3. **Investigate Drops**: Sudden score drops indicate real problems
4. **Review Artifacts**: Always check detailed reports for context
5. **Don't Game the Score**: Address root causes, not symptoms
