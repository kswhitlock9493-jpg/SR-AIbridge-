# Node Failsafe Guide

## 🛡️ Emergency Recovery & Fallback Procedures

This guide covers failsafe mechanisms, emergency procedures, and recovery strategies for the Embedded Autonomy Node.

## Table of Contents

- [Overview](#overview)
- [Failure Scenarios](#failure-scenarios)
- [Recovery Procedures](#recovery-procedures)
- [Emergency Controls](#emergency-controls)
- [Monitoring & Alerts](#monitoring--alerts)
- [Rollback Procedures](#rollback-procedures)

## Overview

The Embedded Autonomy Node is designed with multiple layers of failsafe protection:

1. **Circuit Breakers**: Prevent cascading failures
2. **Graceful Degradation**: Continue with reduced functionality
3. **Automatic Rollback**: Revert problematic changes
4. **Offline Mode**: Operate without external dependencies
5. **Manual Override**: Admiral-level emergency controls

## Failure Scenarios

### Scenario 1: Genesis Bus Unavailable

**Symptoms**:
- Genesis registration fails
- No telemetry published
- "Genesis Bus not enabled" warnings

**Impact**: Low (Node continues in offline mode)

**Automatic Response**:
```python
if not genesis_bus.is_enabled():
    logger.warning("Genesis Bus unavailable, switching to offline mode")
    store_report_locally()
```

**Manual Recovery**:
1. Check external Bridge status
2. Verify network connectivity
3. Review Genesis Bus logs
4. Wait for automatic reconnection

**Prevention**:
- Monitor Genesis Bus health
- Set up redundant message brokers
- Configure appropriate timeouts

---

### Scenario 2: Parser Crashes

**Symptoms**:
- Node run fails with exception
- Incomplete scan results
- Missing findings in report

**Impact**: Medium (Scan incomplete)

**Automatic Response**:
```python
try:
    findings = parser.scan_repo()
except Exception as e:
    logger.error(f"Parser failed: {e}")
    findings = {}  # Continue with empty findings
```

**Manual Recovery**:
1. Review parser error logs
2. Check for malformed files
3. Add problematic directories to exclusion list
4. Manually trigger re-scan

**Prevention**:
- Add robust error handling
- Exclude known problematic paths
- Limit file size scanned
- Add timeout protection

---

### Scenario 3: Truth Certification Fails

**Symptoms**:
- Repairs blocked
- "Certifier warning" messages
- Changes not applied

**Impact**: High (Safety feature working as designed)

**Automatic Response**:
```python
if not v.get("status") == "ok":
    logger.warning(f"Certifier warning: {k} requires review")
    # Changes NOT applied
    return
```

**Manual Recovery**:
1. Review certification warnings
2. Manually inspect proposed changes
3. Override if safe (Admiral only)
4. Update repair patterns if needed

**Prevention**:
- Improve repair pattern quality
- Add test coverage for repairs
- Review certification criteria
- Update Truth Micro-Certifier rules

---

### Scenario 4: Configuration Corruption

**Symptoms**:
- Node fails to start
- Invalid JSON errors
- Missing configuration keys

**Impact**: Critical (Node cannot run)

**Automatic Response**:
```python
try:
    with open("node_config.json") as f:
        config = json.load(f)
except Exception as e:
    logger.error(f"Config corrupted: {e}")
    config = DEFAULT_CONFIG  # Use safe defaults
```

**Manual Recovery**:
1. Restore from git history:
   ```bash
   git checkout HEAD~1 -- .github/autonomy_node/node_config.json
   ```
2. Verify JSON syntax:
   ```bash
   python3 -m json.tool .github/autonomy_node/node_config.json
   ```
3. Commit fixed configuration
4. Re-run workflow

**Prevention**:
- Validate JSON before committing
- Use schema validation
- Keep backup copies
- Implement config version control

---

### Scenario 5: Report Storage Full

**Symptoms**:
- Cannot write reports
- Disk space warnings
- Old reports not being pruned

**Impact**: Medium (Loss of audit trail)

**Automatic Response**:
```python
# Prune old reports if over limit
max_backups = config.get("max_report_backups", 10)
if len(existing_reports) > max_backups:
    prune_oldest_reports()
```

**Manual Recovery**:
1. Manually delete old reports:
   ```bash
   cd .github/autonomy_node/reports
   ls -t | tail -n +11 | xargs rm
   ```
2. Adjust `max_report_backups` in config
3. Verify disk space availability

**Prevention**:
- Set appropriate retention limits
- Monitor storage usage
- Implement automatic cleanup
- Use log rotation

---

### Scenario 6: Infinite Repair Loop

**Symptoms**:
- Same files repaired repeatedly
- High workflow run frequency
- Identical reports across runs

**Impact**: Critical (Resource waste, potential damage)

**Automatic Response**:
```python
# Truth Micro-Certifier prevents this
if repair_already_applied(file):
    logger.warning(f"Repair loop detected for {file}")
    mark_as_ok()  # Prevent re-application
```

**Manual Recovery**:
1. **IMMEDIATELY**: Disable workflow:
   ```yaml
   # Comment out trigger in autonomy_node.yml
   # on:
   #   push:
   #   schedule:
   ```
2. Review recent commits for loop cause
3. Fix repair pattern logic
4. Add loop detection
5. Re-enable workflow with safeguards

**Prevention**:
- Implement change tracking
- Add repair cooldown periods
- Enhanced Truth Micro-Certifier
- Circuit breaker patterns

---

## Recovery Procedures

### Emergency Shutdown

**When to use**: Critical failure, data corruption risk, infinite loop

**Procedure**:

1. **Disable Workflow**:
   ```bash
   # Edit .github/workflows/autonomy_node.yml
   # Change 'on:' to 'on: []' or comment out triggers
   git add .github/workflows/autonomy_node.yml
   git commit -m "Emergency: Disable autonomy node"
   git push
   ```

2. **Cancel Running Jobs**:
   - Go to GitHub Actions tab
   - Find running autonomy-node jobs
   - Click "Cancel workflow"

3. **Verify Shutdown**:
   - Check no new runs starting
   - Wait 5 minutes to confirm
   - Review last run logs

4. **Investigate**:
   - Review recent reports
   - Check error logs
   - Identify root cause
   - Plan fix

5. **Re-enable** (when safe):
   - Apply fix
   - Test manually first
   - Re-enable workflow
   - Monitor closely

### Partial Recovery

**When to use**: One component failing but others functional

**Procedure**:

1. **Identify Failed Component**:
   ```bash
   # Review logs
   python3 .github/autonomy_node/core.py
   ```

2. **Disable Component**:
   ```python
   # In core.py
   def run(self):
       findings = parser.scan_repo()
       # fixes = blueprint.repair(findings)  # DISABLED
       # truth.verify(fixes)  # DISABLED
       cascade.sync_state()  # Keep working components
   ```

3. **Test Partial Functionality**:
   ```bash
   python3 .github/autonomy_node/core.py
   ```

4. **Deploy Partial Fix**:
   ```bash
   git add .github/autonomy_node/core.py
   git commit -m "Temporary: Disable failing component"
   git push
   ```

5. **Fix & Re-enable**:
   - Fix broken component
   - Test thoroughly
   - Re-enable in core.py
   - Deploy and monitor

### Configuration Reset

**When to use**: Configuration issues, unknown state

**Procedure**:

1. **Backup Current Config**:
   ```bash
   cp .github/autonomy_node/node_config.json \
      .github/autonomy_node/node_config.json.backup
   ```

2. **Restore Defaults**:
   ```json
   {
     "autonomy_interval_hours": 6,
     "max_report_backups": 10,
     "truth_certification": true,
     "self_heal_enabled": false,
     "genesis_registration": false
   }
   ```

3. **Disable Risky Features**:
   - Set `self_heal_enabled: false`
   - Set `genesis_registration: false`

4. **Test Basic Functionality**:
   ```bash
   python3 .github/autonomy_node/core.py
   ```

5. **Gradually Re-enable**:
   - Enable one feature at a time
   - Test after each change
   - Monitor for issues

## Emergency Controls

### Admiral Override

**Purpose**: Emergency manual control for critical situations

**Requirements**: Admiral role + emergency authorization

**Available Overrides**:

1. **Force Disable**:
   ```bash
   # Set in node_config.json
   {
     "self_heal_enabled": false,
     "emergency_shutdown": true
   }
   ```

2. **Force Offline Mode**:
   ```bash
   # Set environment variable in workflow
   env:
     GENESIS_MODE: "disabled"
   ```

3. **Skip Truth Certification**:
   ```bash
   # DANGEROUS - Only for emergencies
   {
     "truth_certification": false,
     "override_reason": "Emergency repair required"
   }
   ```

4. **Manual Rollback**:
   ```bash
   git revert <commit-hash>
   git push
   ```

### Circuit Breaker Reset

**When to use**: After circuit breaker trip

**Procedure**:

1. **Check Circuit Status**:
   ```bash
   # Review recent reports
   cat .github/autonomy_node/reports/summary_*.json
   ```

2. **Identify Trigger**:
   - Too many failures?
   - Truth certification failures?
   - Resource exhaustion?

3. **Fix Root Cause**

4. **Reset Circuit**:
   ```python
   # In node_config.json
   {
     "circuit_breaker_reset": true,
     "reset_timestamp": "2025-10-13T00:00:00Z"
   }
   ```

5. **Monitor Recovery**

## Monitoring & Alerts

### Health Check Commands

```bash
# Check node status
python3 .github/autonomy_node/core.py

# Verify configuration
python3 -m json.tool .github/autonomy_node/node_config.json

# Review recent reports
ls -lt .github/autonomy_node/reports/

# Check workflow runs
gh run list --workflow=autonomy_node.yml
```

### Alert Conditions

Monitor for these conditions:

1. **Consecutive Failures**: > 3 runs fail
2. **No Reports Generated**: > 24 hours without report
3. **Repair Loop**: Same files repaired > 5 times
4. **Storage Growth**: Reports directory > 10 MB
5. **Truth Failures**: > 50% of repairs fail certification

### Notification Setup

```python
# In core.py, add alert hook
if consecutive_failures > 3:
    await genesis_bus.publish("autonomy_node.alert.critical", {
        "type": "consecutive_failures",
        "count": consecutive_failures,
        "action_required": "manual_review"
    })
```

## Rollback Procedures

### Automatic Rollback

Triggered by Truth Micro-Certifier failure:

```python
if not truth.verify(fixes):
    logger.error("Truth certification failed, rolling back")
    cascade.rollback_last_change()
```

### Manual Rollback

**Level 1: Revert Last Run**:
```bash
# Find commit
git log --oneline | grep "autonomy_node"

# Revert
git revert <commit-hash>
git push
```

**Level 2: Revert Configuration**:
```bash
git checkout HEAD~1 -- .github/autonomy_node/node_config.json
git commit -m "Rollback: Restore previous config"
git push
```

**Level 3: Disable Node**:
```bash
# Rename workflow to disable
git mv .github/workflows/autonomy_node.yml \
       .github/workflows/autonomy_node.yml.disabled
git commit -m "Emergency: Disable autonomy node"
git push
```

**Level 4: Complete Removal**:
```bash
# Remove all node files
git rm -r .github/autonomy_node/
git rm .github/workflows/autonomy_node.yml
git commit -m "Emergency: Remove autonomy node"
git push
```

### Cascade Integration

For changes applied by the node:

```python
from bridge_backend.engines.cascade.service import CascadeEngine

cascade = CascadeEngine()
result = await cascade.rollback(patch_id="autonomy_node_<timestamp>")
```

## Best Practices

1. **Test Before Deploying**: Always test changes manually
2. **Monitor Closely**: Especially after configuration changes
3. **Keep Backups**: Of configurations and reports
4. **Document Changes**: In commit messages and reports
5. **Gradual Rollout**: Enable features incrementally
6. **Have Rollback Plan**: Before applying risky changes
7. **Review Regularly**: Check reports and logs weekly
8. **Update Documentation**: Keep failsafe guide current

## Contact & Escalation

For critical issues:

1. **Level 1**: Check this guide
2. **Level 2**: Review documentation
3. **Level 3**: Admiral manual intervention
4. **Level 4**: Repository owner escalation

## See Also

- [Embedded Autonomy Node Documentation](EMBEDDED_AUTONOMY_NODE.md)
- [GitHub Mini-Bridge Overview](GITHUB_MINI_BRIDGE_OVERVIEW.md)
- [Cascade Engine Documentation](../bridge_backend/bridge_core/engines/cascade/README.md)
- [Truth Engine Documentation](../bridge_backend/bridge_core/engines/truth/README.md)
