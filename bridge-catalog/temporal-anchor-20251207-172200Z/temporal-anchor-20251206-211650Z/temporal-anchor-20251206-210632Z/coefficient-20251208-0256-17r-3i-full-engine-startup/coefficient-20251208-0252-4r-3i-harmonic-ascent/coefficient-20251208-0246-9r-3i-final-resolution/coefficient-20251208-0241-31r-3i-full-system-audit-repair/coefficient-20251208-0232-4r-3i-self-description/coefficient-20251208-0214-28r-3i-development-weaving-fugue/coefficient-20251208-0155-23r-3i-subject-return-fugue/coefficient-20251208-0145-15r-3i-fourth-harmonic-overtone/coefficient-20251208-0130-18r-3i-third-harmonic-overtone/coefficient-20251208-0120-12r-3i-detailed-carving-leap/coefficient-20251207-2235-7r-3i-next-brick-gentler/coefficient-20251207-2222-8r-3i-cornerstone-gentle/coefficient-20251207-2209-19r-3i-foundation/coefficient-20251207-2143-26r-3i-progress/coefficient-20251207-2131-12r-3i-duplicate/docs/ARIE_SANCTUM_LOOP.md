# ARIE + Sanctum Integration Loop

## 🔄 The Predict → Repair → Certify Loop

This document describes how ARIE and Sanctum work together in the Total Autonomy Protocol.

### Overview

The ARIE-Sanctum loop creates a continuous improvement cycle:

```
┌──────────────────────┐
│ Sanctum Simulation  │  → Predict config issues
└──────────┬──────────┘
           ↓
┌──────────────────────┐
│ Forge Auto-Repair   │  → Fix configuration
└──────────┬──────────┘
           ↓
┌──────────────────────┐
│ ARIE Integrity Scan │  → Audit code quality
└──────────┬──────────┘
           ↓
┌──────────────────────┐
│ Truth Certification │  → Certify all changes
└──────────┬──────────┘
           ↓
┌──────────────────────┐
│ Elysium Guardian    │  → Monitor continuously
└──────────────────────┘
           ↓
      (Repeat every 6h)
```

### Responsibilities

#### Sanctum: Configuration Layer
- Validates deployment configuration
- Checks Netlify/Render setup
- Verifies route integrity
- Detects build health issues

#### Forge: Repair Layer
- Fixes missing config files
- Repairs environment drift
- Creates default configurations
- Maintains deployment readiness

#### ARIE: Code Quality Layer
- Scans for deprecated code
- Detects unused imports
- Finds configuration smells
- Identifies duplicate files

#### Truth: Certification Layer
- Validates all repairs
- Certifies code changes
- Ensures compliance
- Provides audit trail

### Integration Flow

#### 1. Pre-Deploy (Sanctum)

```python
# Sanctum runs simulation
sanctum = SanctumEngine()
report = await sanctum.run_predeploy_check()

if report.has_errors():
    # Publish failure event
    await genesis_bus.publish("sanctum.predeploy.failure", report.to_dict())
    
    # Trigger Forge repair
    forge.run_full_repair(scan_only=False)
```

#### 2. Auto-Repair (Forge)

```python
# Forge scans and repairs
forge = ForgeEngine()
repair_report = await forge.run_full_repair(scan_only=False)

# Certify repairs
cert = await truth.certify(repair_report, {"ok": True})

# Publish to Genesis
await genesis_bus.publish("forge.repair.applied", {
    "count": repair_report["fixed"],
    "certified": cert["certified"]
})
```

#### 3. Code Audit (ARIE)

```python
# ARIE runs integrity scan
arie = ARIEEngine()
summary = arie.run(dry_run=True, apply=False)

# Truth certification happens internally
# Results published to Genesis
await genesis_bus.publish("arie.audit.complete", summary)
```

#### 4. Continuous Monitor (Elysium)

```python
# Elysium runs full cycle
guardian = ElysiumGuardian()
cycle_result = await guardian.run_cycle()

# Includes all of: Sanctum → Forge → ARIE → Truth
await genesis_bus.publish("elysium.cycle.complete", cycle_result)
```

### Event Chain

When a configuration issue is detected:

```
1. sanctum.predeploy.failure
   ↓
2. forge.repair.applied
   ↓
3. arie.audit.complete
   ↓
4. elysium.cycle.complete
```

### Use Cases

#### Case 1: Missing Configuration File

1. **Sanctum** detects missing `_headers`
2. **Forge** creates default `_headers` file
3. **Truth** certifies the creation
4. **ARIE** scans for any related issues
5. **Elysium** confirms system stable

#### Case 2: Deprecated Code

1. **ARIE** finds `datetime.utcnow()` usage
2. **ARIE** auto-fixes to `datetime.now(UTC)`
3. **Truth** certifies the change
4. **Sanctum** verifies build still works
5. **Elysium** monitors for drift

#### Case 3: Environment Drift

1. **Forge** detects missing `.env`
2. **Forge** creates from `.env.example`
3. **Truth** certifies the file
4. **Sanctum** validates configuration
5. **Elysium** continues monitoring

### Policy Hierarchy

Different policies determine what gets fixed:

| Policy | Sanctum | Forge | ARIE |
|--------|---------|-------|------|
| **LINT_ONLY** | ✅ Report | ❌ No fix | ✅ Report |
| **SAFE_EDIT** | ✅ Report | ✅ Config | ✅ Safe fixes |
| **REFACTOR** | ✅ Report | ✅ Config | ✅ Code changes |
| **ARCHIVE** | ✅ Report | ✅ Config | ✅ File removal |

### Genesis Bus Topics

All engines publish to Genesis:

```python
# Sanctum topics
"sanctum.predeploy.success"
"sanctum.predeploy.failure"

# Forge topics
"forge.repair.applied"

# ARIE topics (existing)
"arie.audit"
"arie.fix.applied"
"arie.fix.rollback"

# Elysium topics
"elysium.cycle.complete"
```

### Truth Certification

Every step is certified:

```python
# Sanctum certification
sanctum_cert = await truth.certify(sim_report, {"ok": True})

# Forge certification
forge_cert = await truth.certify(repair_report, {"ok": True})

# ARIE certification
arie_cert = await truth.certify(arie_summary, {"ok": True})

# Full cycle certification
cycle_cert = await truth.certify(cycle_results, {"ok": True})
```

### Monitoring

Subscribe to Genesis events to monitor the loop:

```python
from bridge_backend.genesis.bus import genesis_bus

# Monitor Sanctum
genesis_bus.subscribe("sanctum.predeploy.failure", handle_sanctum_failure)

# Monitor Forge
genesis_bus.subscribe("forge.repair.applied", handle_forge_repair)

# Monitor ARIE
genesis_bus.subscribe("arie.audit.complete", handle_arie_audit)

# Monitor full cycle
genesis_bus.subscribe("elysium.cycle.complete", handle_cycle_complete)
```

### Best Practices

1. **Trust the loop** - Don't bypass Sanctum/Forge
2. **Review certifications** - Check Truth Engine approvals
3. **Monitor Genesis events** - Track the event chain
4. **Set appropriate policies** - Use SAFE_EDIT in production
5. **Run cycles regularly** - Let Elysium maintain health

### Troubleshooting

**Loop not running?**
- Check `GENESIS_MODE=enabled`
- Verify all engines are enabled
- Review Genesis Bus event history

**Repairs not being applied?**
- Check policy settings
- Verify Truth Engine is active
- Review certification failures

**Too many false positives?**
- Adjust ARIE analyzers
- Tune Sanctum thresholds
- Review Forge repair templates

### Related

- [Sanctum Overview](SANCTUM_OVERVIEW.md)
- [Forge Auto-Repair Guide](FORGE_AUTOREPAIR_GUIDE.md)
- [ARIE Operations](ARIE_OPERATIONS.md)
- [Elysium Guardian](ELYSIUM_GUARDIAN.md)
