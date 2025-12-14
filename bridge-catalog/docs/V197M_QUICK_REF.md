# Total Autonomy Protocol - Quick Reference

## v1.9.7m Quick Start

### 🚀 What Is It?

The Total Autonomy Protocol gives the Bridge complete self-maintenance capabilities:
- **Predict** failures before deployment (Sanctum)
- **Repair** configuration automatically (Forge)
- **Certify** all changes (ARIE + Truth)
- **Monitor** continuously forever (Elysium)

### ⚡ Quick Commands

```bash
# Test Sanctum (predictive simulation)
cd bridge_backend/engines/sanctum && python3 core.py

# Test Forge (auto-repair)
cd bridge_backend/engines/forge && python3 core.py

# Run Elysium Guardian (full cycle)
cd bridge_backend/engines/elysium && python3 core.py

# Scan only (no fixes)
cd bridge_backend/engines/forge && python3 core.py --scan-only
```

### 🔧 Configuration

Essential environment variables:

```bash
# Enable all engines
SANCTUM_ENABLED=true
FORGE_ENABLED=true
ARIE_ENABLED=true
ELYSIUM_ENABLED=true

# Elysium monitoring
ELYSIUM_INTERVAL_HOURS=6
ELYSIUM_RUN_IMMEDIATELY=true

# Genesis integration
GENESIS_MODE=enabled
GENESIS_STRICT_POLICY=true
```

### 🌊 The Autonomy Cycle

```
1. Sanctum → Predict issues before deployment
2. Forge   → Fix configuration automatically
3. ARIE    → Audit code quality
4. Truth   → Certify all changes
5. Elysium → Monitor and repeat every 6h
```

### 📡 Genesis Events

Subscribe to these topics to monitor the Bridge:

```python
from bridge_backend.genesis.bus import genesis_bus

# Success/failure predictions
genesis_bus.subscribe("sanctum.predeploy.success", handler)
genesis_bus.subscribe("sanctum.predeploy.failure", handler)

# Auto-repair events
genesis_bus.subscribe("forge.repair.applied", handler)

# Full cycle completion
genesis_bus.subscribe("elysium.cycle.complete", handler)
```

### 🎯 Post-Merge Activation

After merging to main:

```bash
# Boot Elysium Guardian
python3 -m bridge_backend.engines.elysium.core
```

This starts continuous monitoring immediately.

### 🔍 Monitoring

Check system status:

```python
from bridge_backend.engines.elysium.core import ElysiumGuardian

guardian = ElysiumGuardian()
results = await guardian.run_manual_cycle()

print(f"Status: {results['status']}")
print(f"Certified: {results['certified']}")
```

### 🛡️ Safety Features

- **Truth certification** - All changes must be certified
- **Genesis audit trail** - Complete event history
- **Rollback support** - Via Cascade engine
- **Admiral-only controls** - RBAC enforced

### 📚 Documentation

- [Sanctum Overview](SANCTUM_OVERVIEW.md) - Predictive simulation
- [Forge Guide](FORGE_AUTOREPAIR_GUIDE.md) - Auto-repair system
- [ARIE Loop](ARIE_SANCTUM_LOOP.md) - Integration flow
- [Elysium Guardian](ELYSIUM_GUARDIAN.md) - Continuous monitoring
- [Full Protocol](TOTAL_AUTONOMY_PROTOCOL.md) - Complete reference

### ⚠️ Troubleshooting

**Cycle not running?**
- Check `ELYSIUM_ENABLED=true`
- Verify Genesis Bus is active
- Review component logs

**Auto-repair not working?**
- Ensure `FORGE_ENABLED=true`
- Check file permissions
- Verify Truth certification

**Need manual intervention?**
```bash
# Run repair in scan-only mode
cd bridge_backend/engines/forge
python3 core.py --scan-only
```

### ✅ Success Criteria

The Bridge is fully autonomous when:
- ✅ Zero manual deployments in 30 days
- ✅ Zero configuration failures
- ✅ 100% cycles Truth-certified
- ✅ Self-healing < 5 minutes
- ✅ 99.9%+ uptime

### 🎯 Version

- **Version:** v1.9.7m
- **Codename:** Total Autonomy Protocol
- **Status:** ✅ Operational
- **Cycle:** Predict → Heal → Certify → Observe
