# Autonomy Engine Integration Guide

## Overview

The Autonomy Engine is now comprehensively integrated across the entire SR-AIbridge backend, connecting to all engines, tools, runtime systems, and infrastructure components. This integration enables autonomous monitoring, auto-healing, guardrail enforcement, and coordinated responses across the entire system.

## Architecture

### Event Flow

```
All Engines/Tools/Systems → Genesis Bus → Autonomy Engine → Auto-Healing/Coordination
    ↓                                           ↑
Six Super Engines ──────────────────────────────┘
Specialized Engines ────────────────────────────┘
Core Systems ───────────────────────────────────┘
Tools & Runtime ────────────────────────────────┘
```

### Integration Coverage

The Autonomy Engine now integrates with:

1. **Six Super Engines** (CalculusCore, QHelmSingularity, AuroraForge, ChronicleLoom, ScrollTongue, CommerceForge)
2. **Specialized Engines** (Screen, Indoctrination, Agents Foundry, Creativity, Parser, Recovery)
3. **Core Systems** (Fleet, Custody, Console, Captains, Guardians, Registry, Doctrine)
4. **Tools** (Firewall Intelligence, Network Diagnostics, Health Monitoring)
5. **Runtime** (Deploy, Parity, Metrics, TDE-X)
6. **Heritage** (Triage, Federation, MAS)

## Integration Points

#### 1. Triage Integration

The autonomy engine now subscribes to all triage events:

- **`triage.api`** - API health check results
- **`triage.endpoint`** - Endpoint availability results  
- **`triage.diagnostics`** - Diagnostics federation reports

**Event Publishers:**
- `bridge_backend/tools/triage/api_triage.py`
- `bridge_backend/tools/triage/endpoint_triage.py`
- `bridge_backend/tools/triage/diagnostics_federate.py`

**Event Handler:**
```python
async def handle_triage_event(event: Dict[str, Any]):
    # Autonomy responds to triage findings for auto-healing
    await genesis_bus.publish("genesis.heal", {
        "type": "autonomy.triage_response",
        "source": "autonomy",
        "triage_event": event,
    })
```

#### 2. Federation Integration

The autonomy engine coordinates with federation for distributed healing:

- **`federation.events`** - Task forwarding and acknowledgments
- **`federation.heartbeat`** - Node health monitoring

**Event Publishers:**
- `bridge_backend/bridge_core/heritage/federation/federation_client.py`

**Event Handler:**
```python
async def handle_federation_event(event: Dict[str, Any]):
    # Autonomy coordinates with federation for distributed healing
    await genesis_bus.publish("genesis.intent", {
        "type": "autonomy.federation_sync",
        "source": "autonomy",
        "federation_event": event,
    })
```

#### 3. Parity Integration

The autonomy engine auto-fixes parity issues:

- **`parity.check`** - Parity analysis results
- **`parity.autofix`** - Auto-fix execution results

**Event Publishers:**
- `bridge_backend/tools/parity_engine.py`
- `bridge_backend/tools/parity_autofix.py`
- `bridge_backend/runtime/deploy_parity.py`

**Event Handler:**
```python
async def handle_parity_event(event: Dict[str, Any]):
    # Autonomy auto-fixes parity issues
    await genesis_bus.publish("genesis.heal", {
        "type": "autonomy.parity_fix",
        "source": "autonomy",
        "parity_event": event,
    })
```

#### 4. Six Super Engines Integration

The autonomy engine monitors all Six Super Engines:

**ScrollTongue (Language Processing):**
- **`scrolltongue.analysis`** - Language analysis results
- **`scrolltongue.translation`** - Translation events
- **`scrolltongue.pattern`** - Pattern detection results

**CommerceForge (Commerce/Trading):**
- **`commerceforge.trade`** - Trading operations
- **`commerceforge.market`** - Market analysis
- **`commerceforge.portfolio`** - Portfolio updates

**AuroraForge (Visual/Creative):**
- **`auroraforge.visual`** - Visual asset creation
- **`auroraforge.creative`** - Creative generation
- **`auroraforge.render`** - Rendering operations

**ChronicleLoom (Temporal/Historical):**
- **`chronicleloom.chronicle`** - Chronicle creation
- **`chronicleloom.timeline`** - Timeline events
- **`chronicleloom.event`** - Historical events

**CalculusCore (Mathematical):**
- **`calculuscore.computation`** - Mathematical computations
- **`calculuscore.optimization`** - Optimization results
- **`calculuscore.analysis`** - Analytical results

**QHelmSingularity (Quantum/Advanced):**
- **`qhelmsingularity.quantum`** - Quantum computations
- **`qhelmsingularity.advanced`** - Advanced algorithms
- **`qhelmsingularity.simulation`** - Simulation results

**Event Handler:**
```python
async def handle_super_engine_event(event: Dict[str, Any]):
    await genesis_bus.publish("genesis.intent", {
        "type": "autonomy.{engine}_analysis",
        "source": "autonomy",
        "{engine}_event": event,
    })
```

#### 5. Specialized Engines Integration

**Screen Engine:**
- **`screen.interaction`** - User interactions
- **`screen.render`** - Rendering events

**Indoctrination Engine:**
- **`indoctrination.training`** - Training sessions
- **`indoctrination.knowledge`** - Knowledge updates

**Agents Foundry:**
- **`agents_foundry.agent_created`** - Agent creation
- **`agents_foundry.agent_deployed`** - Agent deployment

#### 6. Core Systems Integration

**Fleet Management:**
- **`fleet.command`** - Fleet commands
- **`fleet.status`** - Fleet status updates

**Custody System:**
- **`custody.state`** - State snapshots
- **`custody.transfer`** - State transfers

**Console:**
- **`console.command`** - Console commands
- **`console.output`** - Console output

**Captains:**
- **`captains.policy`** - Policy updates
- **`captains.decision`** - Decision events

**Guardians:**
- **`guardians.validation`** - Validation events (blocks dangerous autonomy actions)
- **`guardians.alert`** - Security alerts

**Registry:**
- **`registry.update`** - Registry updates
- **`registry.query`** - Registry queries

**Doctrine:**
- **`doctrine.compliance`** - Compliance checks
- **`doctrine.violation`** - Violation alerts (triggers autonomy healing)

#### 7. Tools & Runtime Integration

**Firewall Intelligence:**
- **`firewall.threat`** - Threat detection (threat_level > 5 triggers healing)
- **`firewall.analysis`** - Firewall analysis

**Network Diagnostics:**
- **`network.diagnostics`** - Network diagnostics
- **`network.status`** - Network status (errors trigger healing)

**Health Monitoring:**
- **`health.check`** - Health checks
- **`health.status`** - Health status (degraded/unhealthy triggers healing)

**Runtime/Deploy:**
- **`runtime.deploy`** - Deployment events
- **`runtime.status`** - Runtime status (failures trigger healing)

**Metrics:**
- **`metrics.snapshot`** - Metrics snapshots
- **`metrics.anomaly`** - Anomaly detection (triggers healing)

**Event Publishers:**
- `bridge_backend/tools/firewall_intel/`
- `bridge_backend/tools/network_diagnostics/`
- `bridge_backend/tools/health/`
- `bridge_backend/runtime/`

## Configuration

### Environment Variables

- **`GENESIS_MODE`** - Enable/disable Genesis bus (default: `enabled`)
- **`GENESIS_STRICT_POLICY`** - Enforce topic validation (default: `true`)

### Feature Flags

All integration features are enabled by default when Genesis mode is active.

## Usage Examples

### Triage Auto-Healing

When a triage check fails, the autonomy engine automatically receives the event and can trigger healing actions:

```bash
# Run API triage (publishes to triage.api)
python3 bridge_backend/tools/triage/api_triage.py

# Autonomy engine receives event and initiates healing
# Check autonomy logs: grep "autonomy.triage_response" logs/
```

### Federation Coordination

When federation heartbeats are sent, autonomy can coordinate distributed operations:

```python
from bridge_backend.bridge_core.heritage.federation.federation_client import FederationClient

client = FederationClient()
await client.send_heartbeat()  # Publishes to federation.heartbeat
# Autonomy engine receives and coordinates
```

### Parity Auto-Fix

When parity issues are detected, autonomy receives the report and can trigger fixes:

```bash
# Run parity check (publishes to parity.check)
python3 bridge_backend/tools/parity_engine.py

# Run auto-fix (publishes to parity.autofix)
python3 bridge_backend/tools/parity_autofix.py

# Autonomy engine receives events and coordinates fixes
```

## Testing

### Unit Tests

Run the autonomy integration tests:

```bash
cd bridge_backend
python3 -m pytest tests/test_autonomy_integration.py -v
```

### Integration Validation

Validate the integration setup:

```bash
python3 << 'SCRIPT'
import sys
sys.path.insert(0, 'bridge_backend')

from genesis.bus import GenesisEventBus

bus = GenesisEventBus()
required_topics = [
    "triage.api", "triage.endpoint", "triage.diagnostics",
    "federation.events", "federation.heartbeat",
    "parity.check", "parity.autofix"
]

for topic in required_topics:
    if topic in bus._valid_topics:
        print(f"✅ {topic}")
    else:
        print(f"❌ {topic} - MISSING")
SCRIPT
```

## Monitoring

### Event Tracing

Enable Genesis tracing to monitor autonomy events:

```bash
export GENESIS_TRACE_LEVEL=3
```

### Logs

Check autonomy event handling in logs:

```bash
grep "autonomy.triage_response\|autonomy.federation_sync\|autonomy.parity_fix" logs/*.log
```

## Troubleshooting

### Genesis Bus Disabled

If events aren't being received:

```bash
# Check Genesis mode
echo $GENESIS_MODE  # Should be "enabled"

# Enable if needed
export GENESIS_MODE=enabled
```

### Missing Topics

If topic validation fails:

```bash
# Check strict policy
echo $GENESIS_STRICT_POLICY  # "true" or "false"

# Disable strict mode for debugging
export GENESIS_STRICT_POLICY=false
```

### Event Publishing Errors

Events are published with error handling - check logs for warnings:

```bash
grep "Failed to publish\|genesis bus not available" logs/*.log
```

## Version History

- **v1.0.0** - Initial autonomy integration with triage, federation, and parity

## Related Documentation

- [Genesis Architecture](GENESIS_ARCHITECTURE.md)
- [Triage Federation](docs/TRIAGE_FEDERATION.md)
- [Bridge Autofix Engine](docs/BRIDGE_AUTOFIX_ENGINE.md)
- [Genesis Linkage Guide](GENESIS_LINKAGE_GUIDE.md)
