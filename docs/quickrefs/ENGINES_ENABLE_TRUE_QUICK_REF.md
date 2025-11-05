# engines_enable_true Quick Reference

## 🚀 Quick Commands

### Activate All Engines
```bash
python3 -m bridge_backend.cli.genesisctl engines_enable_true
```

### Check Engine Status
```bash
python3 -m bridge_backend.cli.genesisctl engines_status
```

### Environment Management
```bash
# Audit environment variables
python3 -m bridge_backend.cli.genesisctl env audit

# Sync to GitHub
python3 -m bridge_backend.cli.genesisctl env sync --target github --from render

# Auto-heal environment drift
python3 -m bridge_backend.cli.genesisctl env heal
```

---

## 📝 Environment Variables

```bash
# Primary activation flag
ENGINES_ENABLE_TRUE=true

# Genesis framework
GENESIS_MODE=enabled
LINK_ENGINES=true
BLUEPRINTS_ENABLED=true

# Individual engines (all default to true)
STEWARD_ENABLED=true
HXO_ENABLED=true
HXO_NEXUS_ENABLED=true
ARIE_ENABLED=true
AUTONOMY_ENABLED=true
ENVSCRIBE_ENABLED=true
```

---

## 🔧 Engine Categories

### Core Engines (6)
- Truth (Admiral)
- Cascade (Admiral)
- Genesis (Admiral)
- HXO Nexus (Admiral)
- HXO (Admiral)
- Autonomy (Admiral)

### Super Engines (6)
- ARIE (Admiral)
- Chimera (Admiral)
- EnvRecon (Captain)
- EnvScribe (Captain)
- Steward (Admiral)
- Firewall (All)

### Orchestration (3)
- Blueprint (Admiral)
- Leviathan (Admiral)
- Federation (Admiral)

### Utility Engines (15)
- Parser (Captain)
- Doctrine (Admiral)
- Custody (Admiral)
- ChronicleLoom (All)
- AuroraForge (Admiral)
- CommerceForge (Captain)
- ScrollTongue (All)
- QHelmSingularity (Admiral)
- Creativity (All)
- Indoctrination (Captain)
- Screen (All)
- Speech (All)
- Recovery (Admiral)
- AgentsFoundry (Captain)
- Filing (All)

### Integration (1)
- Engine Linkage (Admiral)

**Total: 31 Engines**

---

## 🔒 RBAC Roles

| Role | Permissions | Access Level |
|------|-------------|--------------|
| Admiral | `["*"]` | Full control (healing, deployment, config mutation) |
| Captain | `["read", "execute", "deploy"]` | Read + Execute + Deploy |
| Observer | `["read"]` | Read-only |

---

## 📊 Activation Report Format

```json
{
  "summary": {
    "engines_total": 31,
    "engines_activated": 31,
    "engines_skipped": 0,
    "truth_certified": 31,
    "blocked_by_rbac": 0,
    "auto_heal": "enabled"
  },
  "activated_engines": ["..."],
  "skipped_engines": [],
  "errors": [],
  "timestamp": "2025-10-12T17:44:01Z"
}
```

---

## 🧪 Python API Usage

```python
from bridge_backend.genesis import activate_all_engines, get_activation_status

# Activate all engines
report = activate_all_engines()
print(f"Activated: {report.engines_activated}/{report.engines_total}")
print(report.report())

# Get current status
status = get_activation_status()
print(f"Active engines: {status['summary']['active']}")
```

---

## 🔍 Troubleshooting

### Check if an engine is enabled
```bash
echo $STEWARD_ENABLED
```

### Disable a specific engine
```bash
export STEWARD_ENABLED=false
```

### Re-enable all engines
```bash
export ENGINES_ENABLE_TRUE=true
```

### View activation logs
```bash
cat bridge_backend/logs/engine_activation_report.json | python3 -m json.tool
```

---

## 📚 Related Documentation

- [Full Implementation Guide](./ENGINES_ENABLE_TRUE_v196w.md)
- [Genesis Architecture](./GENESIS_ARCHITECTURE.md)
- [Genesis Linkage Guide](./GENESIS_LINKAGE_GUIDE.md)
- [Unified Genesis v1.9.7c](./V197C_UNIFIED_GENESIS.md)

---

## ⚡ Key Features

✅ **Automatic Activation** - All engines start by default on boot
✅ **RBAC Protected** - Admiral-only operations enforced
✅ **Truth Certified** - All engines pass certification checks
✅ **Self-Reporting** - Real-time status via Genesis bus
✅ **Auto-Healing** - Environment drift automatically corrected
✅ **Zero Manual Steps** - Complete autonomous operation

---

## 👑 "The Bridge stands fully awakened."
