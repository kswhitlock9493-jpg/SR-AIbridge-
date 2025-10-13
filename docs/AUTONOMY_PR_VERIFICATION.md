# Autonomy PR Verification
## Truth Signing + Merge Logic

---

## Overview

The Autonomy Node's self-PR capability requires robust verification to ensure:
1. PRs are authentic and untampered
2. Changes are certified by the Truth Engine
3. Only authorized roles can approve merges
4. Signature integrity is maintained throughout lifecycle

This document describes the complete verification and signing process.

---

## 🔐 Truth Signature System

### Signature Generation

**Algorithm:** SHA256 hash truncated to 16 characters

**Process:**
1. PR body created with metadata and changes
2. Body content hashed using SHA256
3. First 16 hex characters extracted as signature
4. Signature appended to PR body in footer

**Example:**
```
Original Body: "## PR Title\n\n### Changes\n- Fix config\n..."
SHA256 Hash: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6..."
Signature: "a1b2c3d4e5f6g7h8"
```

### Signature Verification

**Steps:**
1. Extract signature from PR body footer
2. Remove signature section to get original body
3. Recalculate SHA256 hash of original body
4. Compare calculated hash with stored signature
5. Return `True` if match, `False` otherwise

**Code Location:** `.github/autonomy_node/signer.py::verify_signature()`

---

## 🛡️ RBAC Authorization

### Role Hierarchy

1. **Admiral** - Full authority
   - Can approve all PRs
   - Can configure reflex settings
   - Can override verification

2. **Captain** - Limited authority
   - Can approve standard PRs
   - Cannot override security checks
   - Requires Admiral approval for critical changes

3. **Crew/Guest** - No authority
   - Cannot approve PRs
   - Read-only access
   - Must request Admiral/Captain review

### RBAC Verification Flow

```python
def verify_rbac(role: str) -> bool:
    """Check if role has PR approval authority"""
    if not RBAC_ENABLED:
        return True  # Bypass in development
    
    allowed_roles = ["admiral", "captain"]
    return role.lower() in allowed_roles
```

### Environment Variables

- `RBAC_ENABLED` - Enable/disable RBAC (default: `true`)
- `RBAC_STRICT_MODE` - Require Admiral for all merges (default: `false`)
- `RBAC_BYPASS_TOKEN` - Emergency bypass token (use with caution)

---

## ✅ Merge Readiness Checks

### Pre-Merge Validation

Before a PR can be merged, it must pass all checks:

1. **Signature Validation**
   - Truth signature present
   - Signature matches current body
   - No tampering detected

2. **RBAC Approval**
   - Approved by authorized role
   - No conflicting approvals
   - Approval timestamp valid

3. **Truth Certification**
   - Changes certified by Truth Engine
   - Certification not expired
   - No certification warnings

4. **Report Integrity**
   - Original report still valid
   - Fixes still applicable
   - No merge conflicts

### Merge Decision Matrix

| Signature Valid | RBAC Approved | Truth Certified | Result |
|----------------|---------------|-----------------|---------|
| ✅ | ✅ | ✅ | **MERGE** |
| ✅ | ✅ | ❌ | BLOCK - Needs Truth |
| ✅ | ❌ | ✅ | BLOCK - Needs RBAC |
| ❌ | ✅ | ✅ | BLOCK - Invalid Sig |
| ❌ | ❌ | ❌ | BLOCK - All Failed |

---

## 🔄 Verification Lifecycle

### 1. PR Creation
```
┌─────────────────┐
│ Generate PR     │
│ Body + Metadata │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Calculate Hash  │
│ (SHA256)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Append Signature│
│ to Body         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create Signed   │
│ Envelope        │
└─────────────────┘
```

### 2. PR Submission
```
┌─────────────────┐
│ Signed PR Data  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Verify RBAC     │
│ Permissions     │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Valid?  │
    └────┬────┘
         │
   ┌─────┴─────┐
   │           │
   ▼           ▼
┌──────┐    ┌──────┐
│Submit│    │Reject│
│to GH │    │      │
└──────┘    └──────┘
```

### 3. Merge Verification
```
┌─────────────────┐
│ PR Opened       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extract         │
│ Signature       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Verify Signature│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check RBAC      │
│ Approval        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Validate Truth  │
│ Certification   │
└────────┬────────┘
         │
    ┌────┴────┐
    │All Pass?│
    └────┬────┘
         │
   ┌─────┴─────┐
   │           │
   ▼           ▼
┌──────┐    ┌──────┐
│Merge │    │Block │
│      │    │      │
└──────┘    └──────┘
```

---

## 🔍 Audit Trail

### Logged Events

Every verification step is logged:

1. **Signature Generation**
   - Timestamp
   - Body hash
   - Signature created

2. **RBAC Check**
   - Role queried
   - Permission result
   - User/token info

3. **Truth Certification**
   - Certification request
   - Certification result
   - Warning messages

4. **Merge Decision**
   - All check results
   - Final decision
   - Merge timestamp

### Log Format

```json
{
  "timestamp": "2025-10-13T03:12:14Z",
  "event": "signature_verification",
  "pr_id": "autonomy/reflex#42",
  "signature": "a1b2c3d4e5f6g7h8",
  "valid": true,
  "rbac_approved": true,
  "truth_certified": true,
  "merge_decision": "approved"
}
```

---

## 🚨 Security Considerations

### Signature Tampering

**Risk:** Attacker modifies PR body after signing

**Mitigation:**
- Signature verification fails on any body change
- PR blocked until re-signed by Truth Engine
- Audit log captures tampering attempt

### RBAC Bypass

**Risk:** Unauthorized user gains approval rights

**Mitigation:**
- RBAC checks at multiple layers
- Role assignments audited regularly
- Emergency bypass requires Admiral token
- All bypasses logged

### Truth Engine Compromise

**Risk:** Truth Engine certificates false positives

**Mitigation:**
- Multi-layer validation (signature + RBAC + Truth)
- Truth Engine has its own integrity checks
- Manual review required for critical changes
- Admiral can override with documented reason

---

## 📊 Verification Metrics

### Success Indicators

- **Signature Valid Rate:** > 99%
- **RBAC Approval Time:** < 5 minutes
- **Truth Certification Rate:** > 95%
- **False Positive Rate:** < 1%

### Monitoring Queries

```python
# Check recent verification failures
get_verification_failures(last_24h=True)

# Audit RBAC decisions
audit_rbac_approvals(days=7)

# Review Truth certifications
review_truth_certifications(status="failed")
```

---

## 🧪 Testing Verification

### Unit Tests

Located in `bridge_backend/tests/test_reflex_loop.py`:

```python
def test_signature_generation():
    """Verify signature correctly generated"""
    body = "Test PR body"
    signed = signer.sign(body)
    assert "sig" in signed
    assert len(signed["sig"]) == 16

def test_signature_validation():
    """Verify signature validation works"""
    body = "Test PR body"
    signed = signer.sign(body)
    assert signer.verify_signature(signed) == True

def test_rbac_authorization():
    """Verify RBAC checks work"""
    assert signer.verify_rbac("admiral") == True
    assert signer.verify_rbac("captain") == True
    assert signer.verify_rbac("guest") == False
```

---

## 📝 Best Practices

1. **Always Verify Signatures**
   - Never trust PR body without verification
   - Re-verify after any PR updates
   - Log all verification attempts

2. **Maintain RBAC Discipline**
   - Regular role audits
   - Principle of least privilege
   - Document role changes

3. **Monitor Truth Certifications**
   - Review certification failures
   - Investigate false positives
   - Update Truth rules as needed

4. **Audit Regularly**
   - Weekly verification log review
   - Monthly RBAC audit
   - Quarterly security assessment

---

**Version:** v1.9.7o  
**Status:** ✅ Production Ready  
**Scope:** Truth Engine + RBAC + Reflex Loop  
**Goal:** Ensure autonomous PRs maintain security and integrity
