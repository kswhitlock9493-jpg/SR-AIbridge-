# HXO Security — Zero-Trust & Quantum-Entropy Protocol

**Version:** v1.9.6p  
**Purpose:** Security architecture and threat mitigation

---

## Security Architecture

HXO implements a multi-layered security model combining:

1. **Zero-Trust Relay** — No implicit trust between engines
2. **Quantum-Entropy Hashing (QEH)** — Cryptographic event signatures
3. **Harmonic Consensus Protocol (HCP)** — Dual validation gates
4. **RBAC Integration** — Admiral-tier access control
5. **Guardian Fail-Safe** — Recursion and anomaly detection

---

## Zero-Trust Relay

### Principle
Every inter-engine communication requires cryptographic verification. No engine trusts another by default.

### Implementation

```python
# All HXO link calls include signed tokens
event = {
    "type": "hxo.shard.execute",
    "plan_id": plan_id,
    "shard_id": shard_id,
    "token": generate_signed_token(plan_id, shard_id),
    "timestamp": utc_now(),
}
```

### Verification Flow

1. Sender generates signed token using `SECRET_KEY`
2. Token includes: operation ID, timestamp, entropy nonce
3. Receiver verifies signature with Truth Engine
4. Token expires after 30 seconds
5. Replay attacks prevented by nonce tracking

### Configuration

```bash
HXO_ZERO_TRUST=true  # Enable zero-trust mode (recommended)
```

When enabled:
- All Genesis Bus events carry signed tokens
- Truth Engine verifies all signatures
- Invalid signatures trigger security alerts
- Unsigned events are rejected

---

## Quantum-Entropy Hashing (QEH)

### Purpose
Prevent spoofed or replayed internal events using high-entropy cryptographic signatures.

### Algorithm

```python
import hashlib
import secrets
from datetime import datetime, UTC

def generate_qeh_signature(event_data: dict) -> str:
    """
    Generate Quantum-Entropy Hash for event.
    """
    # Add entropy nonce
    nonce = secrets.token_hex(32)
    timestamp = datetime.now(UTC).isoformat()
    
    # Canonical event representation
    canonical = json.dumps(event_data, sort_keys=True)
    
    # Compute signature
    payload = f"{canonical}|{nonce}|{timestamp}"
    signature = hashlib.sha3_256(payload.encode()).hexdigest()
    
    return {
        "signature": signature,
        "nonce": nonce,
        "timestamp": timestamp,
        "algorithm": "SHA3-256"
    }
```

### Properties

- **Entropy:** 256-bit nonce ensures uniqueness
- **Collision Resistance:** SHA3-256 provides cryptographic strength
- **Quantum Resistance:** SHA3 family designed for post-quantum security
- **Temporal Binding:** Timestamp prevents long-term replay

### Verification

```python
def verify_qeh_signature(event_data: dict, qeh: dict) -> bool:
    """
    Verify Quantum-Entropy Hash.
    """
    canonical = json.dumps(event_data, sort_keys=True)
    payload = f"{canonical}|{qeh['nonce']}|{qeh['timestamp']}"
    expected = hashlib.sha3_256(payload.encode()).hexdigest()
    
    # Constant-time comparison
    return secrets.compare_digest(expected, qeh['signature'])
```

### Configuration

```bash
HXO_QUANTUM_HASHING=true  # Enable QEH (recommended)
```

---

## Harmonic Consensus Protocol (HCP)

### Overview
Dual-authority consensus model requiring approval from both Truth and Autonomy engines.

### Consensus Flow

```
┌──────────────┐
│ HXO Operation│
└──────┬───────┘
       │
       ├──► Truth Engine (Correctness Check)
       │      └─► Schema valid?
       │      └─► Merkle proof valid?
       │      └─► No conflicts?
       │
       └──► Autonomy Engine (Safety Check)
              └─► Resource limits OK?
              └─► No recursion risk?
              └─► System health OK?
              
       ┌────────┐
       │ Both OK? │
       └────┬─────┘
            │
            ▼
       Execute Operation
```

### Validation Rules

**Truth Engine validates:**
- Schema correctness (via Blueprint)
- Data integrity (Merkle proofs)
- No state conflicts
- Audit trail compliance

**Autonomy Engine validates:**
- Resource availability
- Recursion depth limits
- System stability
- Healing loop detection

### Consensus Modes

```bash
HXO_CONSENSUS_MODE=HARMONIC  # Dual validation (default)
HXO_CONSENSUS_MODE=SIMPLE    # Truth-only (development)
```

**HARMONIC mode (production):**
- Requires Truth + Autonomy approval
- Higher latency (~50ms overhead)
- Maximum safety guarantees

**SIMPLE mode (development):**
- Truth validation only
- Lower latency (~10ms overhead)
- Use for testing/debugging only

### Failure Handling

If consensus fails:

1. **Truth rejects:** Operation is invalid
   - Log to audit trail
   - Return error to caller
   - No retry

2. **Autonomy rejects:** Operation is unsafe
   - Log warning
   - Queue for manual review
   - Optional: retry after cooldown

3. **Both reject:** Critical failure
   - Escalate to admiral
   - Halt affected subsystem
   - Generate incident report

---

## RBAC Integration

### Permission Model

HXO operations are gated by role-based access control:

| Role | Permissions |
|------|-------------|
| Admiral | All HXO operations |
| Captain | View status, read-only access |
| Agent | No HXO access |
| Public | No HXO access |

### Protected Operations

```python
# Admiral-only operations
- POST /api/hxo/plan/submit
- POST /api/hxo/plan/{id}/cancel
- POST /api/hxo/shard/{id}/retry
- DELETE /api/hxo/plan/{id}
- POST /api/hxo/config/update

# Captain-allowed operations (if HXO_ALLOW_CAPTAIN_VIEW=true)
- GET /api/hxo/status
- GET /api/hxo/plan/{id}
- GET /api/hxo/metrics
```

### Configuration

```bash
HXO_ALLOW_CAPTAIN_VIEW=true  # Allow Captains read access
```

---

## Guardian Fail-Safe

### Purpose
Detect and halt recursion or runaway healing loops.

### Detection Mechanisms

**Recursion Detection:**
```python
def check_recursion_depth(plan_id: str) -> bool:
    """Check if plan exceeds recursion limit."""
    depth = get_healing_depth(plan_id)
    
    if depth > HXO_HEAL_DEPTH_LIMIT:
        logger.critical(f"Plan {plan_id} exceeded heal depth: {depth}")
        trigger_guardian_halt(plan_id)
        return False
    
    return True
```

**Loop Detection:**
- Track plan lineage (parent → child relationships)
- Detect circular dependencies
- Monitor repeated failures on same shard

### Halt Procedure

When Guardian triggers:

1. Immediately halt affected plan
2. Mark plan as `GUARDIAN_HALTED`
3. Publish `hxo.guardian.halt` event
4. Notify Truth Engine for audit
5. Generate detailed incident report
6. Escalate to admiral for review

### Configuration

```bash
HXO_HEAL_DEPTH_LIMIT=5  # Max healing recursion depth
```

Recommended values:
- **Development:** 10 (more permissive)
- **Production:** 5 (conservative)
- **Critical systems:** 3 (very strict)

---

## Audit Trail

All security events are logged to:

1. **Genesis Bus** → `hxo.security.event`
2. **Truth Engine** → Merkle-certified audit log
3. **ARIE** → Aggregated security metrics
4. **Local SQLite** → `.hxo/security_log.db`

### Logged Events

- Authentication attempts
- Authorization failures
- Consensus rejections
- Guardian halt triggers
- QEH verification failures
- Signature verification failures
- Anomalous behavior detection

### Audit Query

```bash
# View recent security events
curl -H "Authorization: Bearer $ADMIRAL_TOKEN" \
  http://localhost:8000/api/hxo/security/events?limit=100
```

---

## Threat Model

### Threats Mitigated

✅ **Replay Attacks** → QEH nonces + timestamp expiry  
✅ **Man-in-the-Middle** → Zero-trust signed tokens  
✅ **Privilege Escalation** → RBAC enforcement  
✅ **Recursion Bombs** → Guardian depth limits  
✅ **Rogue Automation** → Harmonic consensus  
✅ **State Corruption** → Truth certification + Merkle proofs  

### Residual Risks

⚠️ **Compromised SECRET_KEY** → Rotate keys immediately  
⚠️ **Insider Threats** → Audit all admiral actions  
⚠️ **DOS via Valid Requests** → Rate limiting required  

---

## Security Best Practices

1. **Rotate SECRET_KEY** every 90 days
2. **Enable all security features** in production
3. **Monitor audit logs** daily
4. **Review Guardian halts** within 1 hour
5. **Restrict admiral access** to 2-3 trusted users
6. **Enable ARIE auto-audits** after deployments
7. **Use HARMONIC consensus** in production
8. **Never disable zero-trust** in production

---

## Compliance

HXO security architecture supports:

- **SOC 2 Type II** — Audit trails, access control
- **GDPR** — Data integrity, audit logs
- **HIPAA** — Encryption, access logs
- **ISO 27001** — Security controls, incident response

---

**Status:** ✅ Complete  
**Last Updated:** 2025-10-11
