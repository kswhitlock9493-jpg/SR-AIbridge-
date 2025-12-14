# ARIE Security Guide

## Security Model

ARIE implements a defense-in-depth security model with multiple layers:

1. **RBAC (Role-Based Access Control)** via Permission Engine
2. **Immutable Audit Trail** via patch journal and Genesis events
3. **Truth-First Certification** before marking changes as final
4. **Restricted File Operations** with policy-based gates

---

## RBAC Capabilities

### arie:scan

**Description**: Run integrity scans

**Default Roles**: captain, admiral

**Operations**:
- `GET /api/arie/report`
- `GET /api/arie/config`
- `POST /api/arie/run` with `dry_run=true`
- CLI: `ariectl scan`

**Risk Level**: Low (read-only)

**Example**:
```python
# Check capability
if await permission_engine.check(user_role, "arie:scan"):
    summary = await arie.run(dry_run=True)
```

---

### arie:fix

**Description**: Apply automated fixes

**Default Roles**: admiral

**Operations**:
- `POST /api/arie/run` with `apply=true`
- CLI: `ariectl apply`

**Risk Level**: Medium to High (modifies code)

**Guardrails**:
- Policy restrictions (SAFE_EDIT vs REFACTOR vs ARCHIVE)
- Truth Engine certification required
- Auto-rollback on failed certification
- Genesis event audit trail

**Example**:
```python
# Requires admiral role
if await permission_engine.check(user_role, "arie:fix"):
    summary = await arie.run(policy=PolicyType.SAFE_EDIT, apply=True)
else:
    raise PermissionError("arie:fix capability required")
```

---

### arie:rollback

**Description**: Rollback applied patches

**Default Roles**: admiral

**Operations**:
- `POST /api/arie/rollback`
- CLI: `ariectl rollback`

**Risk Level**: High (reverts code changes)

**Guardrails**:
- Patch must exist in journal
- Rollback availability flag checked
- Genesis event published
- File state verified

**Example**:
```python
if await permission_engine.check(user_role, "arie:rollback"):
    rollback = await arie.rollback(patch_id, force=False)
```

---

### arie:configure

**Description**: Update ARIE configuration

**Default Roles**: admiral

**Operations**:
- `POST /api/arie/config`

**Risk Level**: High (changes system behavior)

**Configurable Settings**:
- Default policy
- Auto-fix on deploy
- Patch backlog size
- Enabled analyzers

**Example**:
```python
if await permission_engine.check(user_role, "arie:configure"):
    await arie.update_config(new_config)
```

---

## Audit Trail

### Patch Journal

**Location**: `bridge_backend/.arie/patchlog/`

**Format**: JSON files, one per patch

**Contents**:
```json
{
  "id": "patch_2025-10-11T20:30:00_abc123",
  "plan_id": "plan_...",
  "timestamp": "2025-10-11T20:30:00Z",
  "files_modified": ["file1.py", "file2.py"],
  "diff": "...",
  "certified": true,
  "certificate_id": "cert_xyz789",
  "rollback_available": true,
  "metadata": {
    "policy": "SAFE_EDIT",
    "user": "admiral_kyle"
  }
}
```

**Immutability**: Write-once, never modified

**Retention**: Controlled by `ARIE_MAX_PATCH_BACKLOG`

**Access Control**: File system permissions (restrict to admin)

---

### Genesis Events

All ARIE operations publish to Genesis bus:

**Events**:
- `arie.audit` - Every scan
- `arie.fix.intent` - Before applying fixes
- `arie.fix.applied` - After successful fix
- `arie.fix.rollback` - Rollback operations
- `arie.alert` - Critical issues

**Retention**: Configurable via `GENESIS_EVENT_RETENTION_DAYS`

**Subscribers**: 
- SIEM systems
- Audit dashboards
- Compliance reports

---

## Truth Engine Certification

### Certification Process

1. **Post-Fix**: ARIE applies changes
2. **Hash Calculation**: Compute SHA256 of modified files
3. **Truth Request**: Submit to Truth Engine
4. **Verification**: Truth runs tests and validates
5. **Certificate**: Truth issues certificate or fails
6. **Finalization**: 
   - Success: Mark patch as certified
   - Failure: Auto-rollback

### Certification Failure

If Truth Engine fails certification:

```python
if not certification.certified:
    # ARIE automatically triggers rollback
    rollback = await arie.rollback(patch.id, force=False)
    
    # Publish alert
    await bus.publish("arie.alert", {
        "type": "certification_failed",
        "message": f"Patch {patch.id} failed certification: {certification.reason}",
        "severity": "high"
    })
```

### Bypass Protection

Truth certification **cannot be bypassed** except:
- Manual override with `arie:configure` + `ARIE_STRICT_ROLLBACK=false`
- Admiral-level emergency procedures
- Truth Engine unavailable (auto-approve with warning)

---

## Policy-Based Security

### Policy Risk Levels

| Policy | Risk | File Ops | Approval | Certification |
|--------|------|----------|----------|---------------|
| LINT_ONLY | None | None | No | No |
| SAFE_EDIT | Low | Edit | No | Yes |
| REFACTOR | Medium | Edit | Recommended | Yes |
| ARCHIVE | High | Delete/Move | Required | Yes |

### Policy Enforcement

```python
def enforce_policy(user_role, policy):
    if policy == PolicyType.ARCHIVE:
        if user_role != "admiral":
            raise PermissionError("ARCHIVE requires admiral role")
        
        if not confirm_approval():
            raise ValueError("ARCHIVE requires explicit approval")
    
    elif policy == PolicyType.REFACTOR:
        if user_role not in ["admiral", "captain"]:
            raise PermissionError("REFACTOR requires captain+ role")
        
        log_warning("REFACTOR policy - review changes carefully")
```

---

## Restricted Operations

### File System Access

ARIE can only access:
- Repository files (within repo root)
- Patch journal directory
- No system files
- No parent directories

**Enforcement**:
```python
def validate_path(file_path: Path):
    repo_root = Path.cwd()
    
    # Resolve to absolute path
    abs_path = file_path.resolve()
    
    # Ensure within repo
    if not abs_path.is_relative_to(repo_root):
        raise SecurityError("Path outside repository")
    
    # Block sensitive paths
    blocked = {".git", ".env", "keys/", "credentials/"}
    if any(b in abs_path.parts for b in blocked):
        raise SecurityError("Access to sensitive path denied")
```

### Git Operations

ARIE uses git for rollback but:
- No push operations
- No branch switching
- No remote operations
- Read-only access to history

**Allowed**:
```bash
git checkout HEAD~1 -- <file>  # Restore from previous commit
git diff                        # View changes
```

**Blocked**:
```bash
git push       # ❌
git reset      # ❌
git branch     # ❌
git remote     # ❌
```

---

## Secrets Protection

### Environment Variables

ARIE never:
- Logs ENV values
- Stores ENV in patches
- Transmits ENV over network
- Writes ENV to reports

**ConfigSmellAnalyzer** only reports:
- ENV access without defaults
- No actual values captured

### Credentials

ARIE excludes from scanning:
- `.env` files
- `keys/` directory
- `credentials/` directory
- Any file matching `*secret*`, `*password*`, `*token*`

---

## Network Security

ARIE operates entirely locally:
- No third-party API calls
- No external dependencies
- No network transmission of code
- All operations within repository

**Genesis Integration**:
- Internal event bus only
- No external publish/subscribe

---

## Monitoring and Alerts

### Security Events to Monitor

1. **Failed Rollbacks**
   ```python
   bus.subscribe("arie.fix.rollback", lambda evt:
       alert_if_failed(evt)
   )
   ```

2. **High-Risk Policy Usage**
   ```python
   bus.subscribe("arie.fix.intent", lambda evt:
       alert_if_policy(evt, ["REFACTOR", "ARCHIVE"])
   )
   ```

3. **Certification Failures**
   ```python
   bus.subscribe("arie.alert", lambda evt:
       page_oncall_if(evt["type"] == "certification_failed")
   )
   ```

4. **Unusual Activity**
   ```python
   # Multiple fixes in short time
   # Large number of files modified
   # Permission escalation attempts
   ```

---

## Incident Response

### Suspected Unauthorized Changes

1. **Immediately disable ARIE**:
   ```bash
   export ARIE_ENABLED=false
   ```

2. **Review patch journal**:
   ```bash
   cat bridge_backend/.arie/patchlog/*.json | jq '.metadata.user'
   ```

3. **Check Genesis events**:
   ```python
   events = await bus.get_history("arie.*")
   suspicious = [e for e in events if not verify_user(e)]
   ```

4. **Rollback if necessary**:
   ```bash
   python3 -m bridge_backend.cli.ariectl rollback --patch <patch_id>
   ```

5. **Audit permissions**:
   ```python
   await permission_engine.audit("arie:*")
   ```

---

## Compliance

### SOC 2 / ISO 27001

ARIE provides:
- **Audit trails** - All operations logged
- **Access controls** - RBAC enforced
- **Change management** - Approval workflows
- **Rollback capability** - Incident recovery
- **Immutable logs** - Genesis events + patch journal

### GDPR

ARIE does not:
- Process personal data
- Store user information
- Transmit data externally
- Require user consent

### Security Certifications

For certification audits, provide:
1. Patch journal files
2. Genesis event history
3. Permission policies
4. Rollback procedures
5. Truth certification records

---

## Best Practices

1. **Least Privilege**: Grant `arie:scan` to most, `arie:fix` to few
2. **Approval Workflows**: Require approval for REFACTOR and ARCHIVE
3. **Regular Audits**: Review patch journal monthly
4. **Monitor Alerts**: Watch `arie.alert` topic continuously
5. **Test Rollbacks**: Practice rollback procedures regularly
6. **Backup Critical**: Backup before ARCHIVE operations
7. **Limit Auto-Fix**: Keep `ARIE_AUTO_FIX_ON_DEPLOY_SUCCESS=false` in production
8. **Review Certifications**: Check Truth Engine results
9. **Rotate Tokens**: If using tokens for CI, rotate regularly
10. **Document Changes**: Log reason for manual overrides

---

## Security Checklist

- [ ] RBAC policies configured
- [ ] Patch journal permissions restricted
- [ ] Genesis event retention set
- [ ] Truth Engine certification enabled
- [ ] Monitoring alerts configured
- [ ] Rollback procedures tested
- [ ] Secrets excluded from scanning
- [ ] Auto-fix disabled in production
- [ ] Audit trail reviewed regularly
- [ ] Incident response plan documented
