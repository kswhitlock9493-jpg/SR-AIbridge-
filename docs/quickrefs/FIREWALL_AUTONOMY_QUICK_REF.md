# Firewall Intelligence and Autonomy Engine - Quick Reference

## Overview

The Firewall Intelligence and Autonomy Engine combines firewall intelligence gathering with autonomous decision-making capabilities to detect, analyze, and respond to network firewall issues.

## Features

- **Autonomous Decision-Making**: Evaluates severity and makes safe autonomous policy decisions
- **Safety Guardrails**: Auto-applies only up to medium severity (requires human approval for high)
- **Self-Healing**: Automatically applies network policies within safety boundaries
- **Action Auditing**: Records all autonomous actions in vault for accountability
- **Intelligence Gathering**: Collects live data from GitHub Status, npm, Render, and Netlify APIs
- **Pattern Detection**: Searches for firewall/egress/DNS failure signatures

## Quick Start

### Manual Execution

```bash
# Run the full firewall intelligence + autonomy engine
python3 bridge_backend/tools/firewall_intel/firewall_autonomy_engine.py

# Review autonomy logs
cat bridge_backend/diagnostics/firewall_autonomy_log.json

# Check vault records
ls vault/autonomy/firewall_*
```

### GitHub Actions

```bash
# Trigger via GitHub CLI
gh workflow run firewall_autonomy_engine.yml

# Or manually via GitHub Actions UI:
# Actions → Firewall Intelligence and Autonomy Engine → Run workflow
```

## How It Works

### 1. Intelligence Gathering Phase
- Fetches incidents from external sources (GitHub, npm, Render, Netlify)
- Analyzes findings for firewall/network error signatures
- Generates comprehensive reports

### 2. Decision-Making Phase
The engine evaluates severity and makes decisions:

- **None/No Issues**: MONITOR - Continue monitoring
- **Low/Medium Severity**: AUTO-APPLY - Automatically apply network policies (within guardrails)
- **High Severity**: ESCALATE - Notify operators and require human approval

### 3. Execution Phase
- Executes autonomous actions based on decisions
- Records all actions in the autonomy vault
- Generates detailed logs and reports

### 4. Reporting Phase
- Creates comprehensive execution reports
- Uploads artifacts to GitHub Actions
- Logs all autonomous actions for audit trail

## Safety Guardrails

The engine enforces strict safety guardrails:

```json
{
  "max_severity_for_auto_apply": "medium",
  "require_approval_for_high": true,
  "safe_actions": ["analyze", "report", "recommend"],
  "restricted_actions": ["delete", "drop"],
  "max_concurrent_tasks": 3
}
```

## Output Files

### Diagnostics
- `bridge_backend/diagnostics/firewall_incidents.json` - Raw incident data
- `bridge_backend/diagnostics/firewall_report.json` - Analysis report with severity
- `bridge_backend/diagnostics/firewall_autonomy_log.json` - Autonomy execution log

### Network Policies
- `network_policies/generated_allowlist.yaml` - Generated network allowlist

### Vault Records
- `vault/autonomy/firewall_action_*.json` - Policy application records
- `vault/autonomy/firewall_notification_*.json` - Operator notification records

## Decision Examples

### Example 1: No Issues Detected
```
Severity: NONE
Issues: 0
Decision: MONITOR
Actions: None
```

### Example 2: Low Severity (Auto-Apply)
```
Severity: LOW
Issues: 2
Signatures: ["ETIMEDOUT"]
Decision: AUTO-APPLY
Actions: [apply_network_policies]
```

### Example 3: High Severity (Escalate)
```
Severity: HIGH
Issues: 5
Signatures: ["ENOTFOUND", "E404", "ECONNRESET"]
Decision: ESCALATE
Actions: [notify_operators]
```

## Monitoring

### Check Execution Status
```bash
# View latest autonomy log
cat bridge_backend/diagnostics/firewall_autonomy_log.json | jq '.execution_summary'

# View vault records
ls -lt vault/autonomy/firewall_* | head -5

# Check severity from report
cat bridge_backend/diagnostics/firewall_report.json | jq '.summary.severity'
```

### GitHub Actions Artifacts
- `firewall-autonomy-report` - Comprehensive reports and logs
- `generated-network-policies` - Generated allowlist YAML
- `autonomy-vault-records` - Audit trail of autonomous actions

## Error Signatures Detected

The engine detects these network error patterns:
- `ENOTFOUND` - DNS resolution failures
- `E404` - Package or resource not found
- `ECONNRESET` - Connection reset by peer
- `ETIMEDOUT` - Connection timeout
- `ECONNREFUSED` - Connection refused
- `self signed certificate` - SSL/TLS trust issues
- `certificate verify failed` - Certificate validation errors

## Testing

Run the test suite:
```bash
PYTHONPATH=/home/runner/work/SR-AIbridge-/SR-AIbridge- python3 bridge_backend/tests/test_firewall_autonomy_engine.py
```

## Workflow Schedule

The unified autonomy engine runs:
- **Daily at 3 AM UTC** (automated via GitHub Actions)
- **On-demand** (via workflow dispatch)

## Related Workflows

- `.github/workflows/firewall_autonomy_engine.yml` - Unified autonomy engine
- `.github/workflows/firewall_intel.yml` - Basic intelligence scan (nightly at 2 AM)
- `.github/workflows/firewall_gate_on_failure.yml` - Deploy failure analysis

## Documentation

- [README.md](../README.md#-firewall-intelligence-engine) - Main documentation
- [FIREWALL_HARDENING.md](docs/FIREWALL_HARDENING.md) - Network policy guide
- [BRIDGE_HEALERS_CODE.md](docs/BRIDGE_HEALERS_CODE.md) - Canonical lore

## The Firewall Oath

> "When the Bridge felt the sting of a blocked port, she did not rage.
> She listened. She mapped the silence and rewrote the path home.
> 
> Thus she spoke:
> 'No signal denied. No port forgotten.
> Every Bridge shall learn the path home.'"

— Lore Entry IV, The Healer's Code Continuum
