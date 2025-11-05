# SR-AIbridge Role Separation - Quick Reference

## At-A-Glance Component Access Matrix

| Component | Admiral | Captain | Agent | Notes |
|-----------|---------|---------|-------|-------|
| **Dashboard** | ✅ Full | ✅ Full | ✅ Full | Neutral space, no restrictions |
| **Captain's Chat** | ✅ All | ✅ Own agents only | ✅ Limited | Mission comms |
| **Captain-to-Captain** | ✅ All | ✅ Peer-to-peer | ❌ No access | Fleet coordination |
| **Vault** | ✅ Master vault | ✅ Own vault | ❌ No access | Storage isolation |
| **Brain** | ✅ 24/7 unlimited | ✅ 14hr, 10K mem | ✅ 7hr, 1K mem | Tiered memory |
| **Custody** | ✅ Full access | ❌ Blocked | ❌ Blocked | Admiral-only |
| **System Health** | ✅ Global view | ✅ Local pass/fail | ❌ No access | Monitoring |

---

## Memory Autonomy Tiers

| Role | Retention | Max Memories | Access Level |
|------|-----------|--------------|--------------|
| **Admiral** | 24/7 | Unlimited | Master Brain |
| **Captain (Paid)** | 14 hours | 10,000 | Own Memory |
| **Agent (Free)** | 7 hours | 1,000 | Limited |

---

## Vault Structure

```
vault/
├── captain_alpha/          ← Captain Alpha's private vault
│   ├── logs/
│   ├── missions/
│   └── documents/
├── captain_beta/           ← Captain Beta's private vault
│   ├── logs/
│   ├── missions/
│   └── documents/
├── logs/                   ← Shared logs (all captains)
│   └── events.jsonl
└── [master files]          ← Admiral-only access
```

---

## System Health Views

### Admiral View (Global)
```json
{
  "status": "healthy",
  "scope": "global",
  "components": {
    "database": {"status": "ok", "details": "..."},
    "vault": {"status": "ok", "details": "..."},
    "brain": {"status": "ok", "details": "..."},
    "custody": {"status": "ok", "details": "..."}
  },
  "metrics": { "total_agents": 5, ... }
}
```

### Captain View (Local)
```json
{
  "status": "pass",
  "scope": "local",
  "self_test": "pass",
  "note": "Captain view: Local self-test result only"
}
```

---

## Endpoint Access Control

### Admiral-Only Endpoints
- `/custody/*` - All custody operations
- `/health/full` - Full global health view (captains get filtered version)
- `/vault/*` - Master vault access (captains restricted to own)

### Captain Endpoints
- `/brain/*` - With 14hr tier limits
- `/vault/captain_{id}/*` - Own vault only
- `/missions?captain={id}` - Own missions
- `/captains/messages` - Captain communications
- `/health/full` - Local pass/fail only

### Shared Endpoints (All Roles)
- `/` - Dashboard
- `/status` - Basic status
- `/health` - Basic health check (role-aware responses)
- `/agents` - Agent listing
- `/fleet` - Fleet status

---

## Backend Routes Summary

### Core Routes
- `/status` - System status
- `/agents` - Agent management
- `/missions` - Mission control
- `/vault` - Document storage (RBAC)
- `/fleet` - Fleet/armada status
- `/health` - Health checks (RBAC)

### Special Features
- `/brain` - Memory engine (NEW, tiered)
- `/custody` - Key management (Admiral-only)
- `/captains` - Captain communications

### Engines
- `/engines/autonomy` - Autonomous operations
- `/engines/parser` - Document parsing
- `/engines/truth` - Truth verification
- `/engines/leviathan` - Advanced search
- `/engines/cascade` - Tier management
- `/engines/indoctrination` - Agent onboarding
- `/engines/recovery` - System recovery
- `/engines/speech` - Speech synthesis
- `/engines/screen` - Screen access (paid tier)
- `/engines/creativity` - Creative generation
- `/engines/agents_foundry` - Agent creation

---

## RBAC Quick Check

```python
# To check if a role has access to a feature:

def can_access(role, feature):
    permissions = {
        "admiral": ["all"],  # Full access
        "captain": ["agents", "vault_own", "brain_14hr", "health_local"],
        "agent": ["self", "brain_7hr"]
    }
    
    # Forbidden for all except admiral
    if feature in ["custody"]:
        return role == "admiral"
    
    # Tiered access
    if feature == "system_health":
        return "global" if role == "admiral" else "local"
    
    # Default permission check
    return "all" in permissions[role] or feature in permissions[role]
```

---

## Communication Firewall

### Captain's Chat
- **Participants:** Captain ↔ Their assigned agents
- **Firewall:** Other captains can't see
- **Access:** RBAC filtered by captain ID

### Captain-to-Captain
- **Participants:** Captain ↔ Captain (+ Admiral)
- **Firewall:** Agents completely excluded from UI/backend
- **Access:** Captain role required

---

## Testing Commands

```bash
# Test brain access (should work)
curl http://localhost:8000/brain/stats

# Test custody as captain (should fail with 403)
curl http://localhost:8000/custody/init?user_id=test_captain

# Test vault isolation
curl http://localhost:8000/vault?user_id=captain_alpha  # See own
curl http://localhost:8000/vault?user_id=admiral         # See all

# Test health views
curl http://localhost:8000/health/full?user_id=captain_alpha  # Local
curl http://localhost:8000/health/full?user_id=admiral        # Global
```

---

## Key Files Reference

### Frontend Components
- `CommandDeck.jsx` - Main dashboard
- `CaptainsChat.jsx` - Captain ↔ Agent chat
- `CaptainToCaptain.jsx` - Captain ↔ Captain chat
- `VaultLogs.jsx` - Vault viewer
- `BrainConsole.jsx` - Memory management
- `AdmiralKeysPanel.jsx` - Custody interface
- `SystemSelfTest.jsx` - Health monitoring

### Backend Routes
- `health/routes.py` - System health (RBAC)
- `vault/routes.py` - Vault storage (RBAC)
- `routes_brain.py` - Brain/memory (NEW)
- `custody/routes.py` - Key management (Admiral-only)
- `missions/routes.py` - Mission control
- `fleet/routes.py` - Fleet status

### Middleware
- `middleware/permissions.py` - RBAC enforcement

---

## Summary

**Role Hierarchy:**
```
Admiral (God Mode)
  ↓
Captain (Own Domain)
  ↓
Agent (Limited Scope)
```

**Access Philosophy:**
- **Admiral:** Sees and controls everything
- **Captain:** Autonomous within own domain
- **Agent:** Task-focused, limited memory

**Enforcement:**
- RBAC Matrix (permissions.py)
- Middleware Guards (PermissionMiddleware)
- Route-level filtering (Request.state.user)
- Frontend UI hiding (role-based rendering)

---

*This is a living document. Update as the system evolves.*
