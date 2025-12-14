# Elysium Guardian

## 🪶 Elysium - Continuous Passive Guardian System

Elysium is the Bridge's continuous monitoring and health maintenance engine that runs the full autonomy cycle on a schedule.

### Purpose

- **Monitor** repository health continuously
- **Execute** full autonomy cycles automatically
- **Maintain** zero-drift state
- **Ensure** self-sustaining operation

### Architecture

```
┌─────────────────────────────────────┐
│   Elysium Guardian                  │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Scheduler (every 6 hours)   │   │
│  └───────────┬─────────────────┘   │
│              ↓                      │
│  ┌─────────────────────────────┐   │
│  │ Cycle Orchestrator          │   │
│  └───────────┬─────────────────┘   │
│              ↓                      │
│  ┌──────────────────┐              │
│  │ 1. Sanctum       │  Predict     │
│  └──────────────────┘              │
│  ┌──────────────────┐              │
│  │ 2. Forge         │  Repair      │
│  └──────────────────┘              │
│  ┌──────────────────┐              │
│  │ 3. ARIE          │  Certify     │
│  └──────────────────┘              │
│  ┌──────────────────┐              │
│  │ 4. Truth         │  Validate    │
│  └──────────────────┘              │
│              ↓                      │
│  ┌─────────────────────────────┐   │
│  │ Genesis Event Publication   │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Features

#### 1. Scheduled Cycles

Runs complete health cycles at regular intervals:
- Default: Every 6 hours
- Configurable via `ELYSIUM_INTERVAL_HOURS`
- Immediate first run on deployment

#### 2. Full Autonomy Pipeline

Each cycle executes:
1. **Sanctum** - Predictive simulation
2. **Forge** - Configuration repair
3. **ARIE** - Code integrity audit
4. **Truth** - Complete certification

#### 3. Continuous Monitoring

- Passive observation (no user action required)
- Self-healing capabilities
- Automatic drift detection
- Zero-downtime maintenance

#### 4. Genesis Integration

- Publishes `elysium.cycle.complete` events
- Subscribes to failure events
- Maintains audit trail
- Enables real-time monitoring

### Usage

#### Automatic (Post-Merge)

After merging to main, run:

```bash
python3 -m bridge_backend.engines.elysium.core
```

This boots Elysium Guardian and begins continuous monitoring.

#### Programmatic

```python
from bridge_backend.engines.elysium.core import ElysiumGuardian

guardian = ElysiumGuardian()

# Start continuous monitoring
guardian.start()

# Or run async
await guardian.start_async()

# Manual cycle trigger
results = await guardian.run_manual_cycle()
```

#### CLI

```bash
cd bridge_backend/engines/elysium
python3 core.py
```

#### GitHub Actions

Elysium runs in the Total Autonomy workflow:

```yaml
- name: Run Elysium Continuous Guardian
  run: |
    cd bridge_backend/engines/elysium
    python3 core.py
  env:
    ELYSIUM_ENABLED: "true"
    ELYSIUM_INTERVAL_HOURS: "6"
```

### Configuration

Environment variables:

```bash
# Enable/disable Elysium
ELYSIUM_ENABLED=true

# Cycle interval (hours)
ELYSIUM_INTERVAL_HOURS=6

# Run immediately on start
ELYSIUM_RUN_IMMEDIATELY=true

# Genesis bus integration
GENESIS_MODE=enabled
```

### Cycle Flow

Each Elysium cycle:

```python
async def run_cycle():
    # 1. Sanctum simulation
    sanctum_report = await sanctum.run_predeploy_check()
    
    # 2. Forge repair (if needed)
    forge_report = await forge.run_full_repair()
    
    # 3. ARIE integrity audit
    arie_summary = arie.run(dry_run=True)
    
    # 4. Truth certification
    cert = await truth.certify(cycle_results, {"ok": True})
    
    # 5. Publish to Genesis
    await genesis_bus.publish("elysium.cycle.complete", {
        "status": "stable",
        "certified": cert["certified"],
        "sanctum": {...},
        "forge": {...},
        "arie": {...}
    })
```

### Cycle Results

Each cycle produces a comprehensive report:

```json
{
  "timestamp": "2025-10-13T00:15:00Z",
  "status": "stable",
  "certified": true,
  "sanctum": {
    "status": "passed",
    "errors": []
  },
  "forge": {
    "issues_found": 2,
    "issues_fixed": 2
  },
  "arie": {
    "findings_count": 5,
    "duration": 1.23
  }
}
```

### Example Output

```
🪶 Elysium: Continuous monitoring thread initialized.
🪶 Elysium: Active - will run every 6 hours
🌐 Elysium cycle starting — full system audit...
🧭 Elysium: Running Sanctum simulation...
🛠️ Elysium: Running Forge repair...
🧠 Elysium: Running ARIE integrity audit...
✅ Elysium: Truth certified cycle completion
🪶 Elysium cycle complete - system stable
```

### Monitoring

Subscribe to Elysium events:

```python
from bridge_backend.genesis.bus import genesis_bus

def handle_cycle_complete(event):
    print(f"Cycle status: {event['status']}")
    print(f"Certified: {event['certified']}")
    
    if event['status'] != 'stable':
        # Alert or take action
        pass

genesis_bus.subscribe("elysium.cycle.complete", handle_cycle_complete)
```

### Integration with Other Systems

#### Cascade Orchestration

Elysium works with Cascade for:
- Rollback support on failed cycles
- Orchestrated healing sequences
- Automated decision making

#### Governance

- **Admiral-only** manual trigger capability
- **Captain** can view cycle reports
- **Observer** gets read-only summaries

#### Truth Engine

Every cycle must be Truth-certified:
- Validates all component results
- Ensures compliance
- Provides audit signature

### Scheduling Strategy

**Why 6 hours?**
- Frequent enough to catch drift early
- Infrequent enough to avoid overhead
- Balances monitoring vs. resource usage

**Custom intervals:**
```bash
# Every 3 hours (aggressive)
ELYSIUM_INTERVAL_HOURS=3

# Every 12 hours (conservative)
ELYSIUM_INTERVAL_HOURS=12

# Daily
ELYSIUM_INTERVAL_HOURS=24
```

### Safety Features

1. **Error isolation** - Component failures don't stop the cycle
2. **Truth gating** - All changes require certification
3. **Genesis audit** - Complete event history
4. **Graceful degradation** - Continues even if one engine fails

### Troubleshooting

**Elysium not running?**
- Check `ELYSIUM_ENABLED=true`
- Verify Python async loop is running
- Review Genesis Bus status

**Cycles failing?**
- Check individual engine status
- Review component error logs
- Verify Truth Engine availability

**Too frequent/infrequent?**
- Adjust `ELYSIUM_INTERVAL_HOURS`
- Consider system load
- Monitor resource usage

**Manual cycle trigger:**
```python
guardian = ElysiumGuardian()
results = await guardian.run_manual_cycle()
```

### Best Practices

1. **Let it run** - Don't disable unless absolutely necessary
2. **Monitor events** - Subscribe to `elysium.cycle.complete`
3. **Review results** - Check cycle reports regularly
4. **Tune interval** - Adjust based on system needs
5. **Trust certification** - Honor Truth Engine decisions

### Post-Merge Activation

After merging v1.9.7m:

```bash
# SSH into server or run in deployment
python3 -m bridge_backend.engines.elysium.core

# Or add to startup script
# This boots Elysium Guardian instantly
```

### Related

- [Sanctum Overview](SANCTUM_OVERVIEW.md)
- [Forge Auto-Repair Guide](FORGE_AUTOREPAIR_GUIDE.md)
- [ARIE Sanctum Loop](ARIE_SANCTUM_LOOP.md)
- [Total Autonomy Protocol](TOTAL_AUTONOMY_PROTOCOL.md)
