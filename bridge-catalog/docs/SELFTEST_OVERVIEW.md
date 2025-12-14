# Self-Test Overview

## v1.9.7j — Bridge Autonomy Diagnostic Pulse

The Self-Test engine provides continuous validation and auto-healing for all Bridge subsystems.

## Architecture

### Core Components

1. **Self-Test Controller** (`bridge_backend/engines/selftest/core.py`)
   - Orchestrates full synthetic deploy tests
   - Monitors 31 engines through Genesis events
   - Publishes health metrics to Steward
   - Runs every 72 hours or on-demand

2. **Auto-Heal Trigger** (`bridge_backend/engines/selftest/autoheal_trigger.py`)
   - Detects failed checks in self-test reports
   - Launches targeted micro-repairs
   - Uses ARIE + Chimera + Cascade
   - Re-runs validation until Truth certifies

3. **Genesis Integration**
   - Event topics: `selftest.*`
   - Full bus integration
   - Truth certification required
   - Steward visualization

## Diagnostic Flow

```
Genesis ⟶ Chimera ⟶ Hydra ⟶ Leviathan ⟶ ARIE ⟶ EnvRecon ⟶ EnvScribe ⟶ Steward ⟶ Truth
                          ↓
                     Auto-Heal Trigger (if any step fails)
```

## Engine Registry

The self-test validates 31 engines:

**Core Infrastructure:**
- Truth
- Cascade
- Genesis
- HXO Nexus
- HXO
- Autonomy

**Super Engines:**
- ARIE
- Chimera
- EnvRecon
- EnvScribe
- Steward
- Firewall

**Orchestration:**
- Blueprint
- Leviathan
- Federation

**Utility Engines:**
- Parser, Doctrine, Custody
- ChronicleLoom, AuroraForge
- CommerceForge, ScrollTongue
- QHelmSingularity, Creativity
- Indoctrination, Screen, Speech
- Recovery, AgentsFoundry, Filing
- Hydra

## Usage

### Manual Invocation

```bash
python3 -m bridge_backend.cli.genesisctl self_test_full --heal
```

### Disable Auto-Healing

```bash
python3 -m bridge_backend.cli.genesisctl self_test_full --no-heal
```

### Environment Variables

- `SELFTEST_ENABLED` - Enable/disable self-test (default: true)
- `AUTO_HEAL_ON` - Enable/disable auto-healing (default: true)
- `AUTOHEAL_MAX_RETRIES` - Max healing attempts (default: 3)
- `AUTOHEAL_RETRY_DELAY` - Delay between retries in seconds (default: 1.0)

## Report Structure

```json
{
  "test_id": "bridge_selftest_20241012_123456",
  "summary": {
    "engines_total": 31,
    "engines_verified": 31,
    "autoheal_invocations": 2,
    "status": "Stable",
    "runtime_ms": 482
  },
  "events": [
    {
      "engine": "Hydra",
      "action": "health_check",
      "result": "✅"
    },
    {
      "engine": "EnvRecon",
      "action": "health_check",
      "result": "⚠️ auto-heal launched"
    },
    {
      "engine": "EnvRecon",
      "action": "repair_patch_applied",
      "result": "✅ certified",
      "strategy": "arie",
      "attempts": 1
    }
  ],
  "timestamp": "2024-10-12T12:34:56.789Z"
}
```

## Continuous Operation

### Automatic Schedule

- Every 72 hours via Genesis cron
- After every merge or deploy success event
- GitHub Actions workflow integration

### On Failure Detected

1. Self-Test publishes `selftest.autoheal.trigger`
2. ARIE repairs → Truth certifies → Steward visualizes
3. Genesis emits `selftest.autoheal.complete` once certified

## Security & Governance

| Role | Capability |
|------|-----------|
| Admiral | Full command (start/stop test, approve cert) |
| Captain+ | Execute tests & view reports |
| Observer | Read-only results |

RBAC + Truth enforcement ensure only authorized healing occurs.

## Metrics

| Metric | Expected Value |
|--------|----------------|
| Total Engines Checked | 31 |
| Certified by Truth | 31 |
| Auto-Heals Executed | ≤ 3 |
| Verification Status | ✅ Stable |
| Average Run Time | < 0.5 s |

## Integration Points

- **Genesis Bus**: Event publication and subscription
- **Truth Engine**: Certification of healing results
- **Steward**: Metrics visualization and audit logs
- **ARIE**: Configuration healing
- **Chimera**: Deployment healing
- **Cascade**: System recovery
