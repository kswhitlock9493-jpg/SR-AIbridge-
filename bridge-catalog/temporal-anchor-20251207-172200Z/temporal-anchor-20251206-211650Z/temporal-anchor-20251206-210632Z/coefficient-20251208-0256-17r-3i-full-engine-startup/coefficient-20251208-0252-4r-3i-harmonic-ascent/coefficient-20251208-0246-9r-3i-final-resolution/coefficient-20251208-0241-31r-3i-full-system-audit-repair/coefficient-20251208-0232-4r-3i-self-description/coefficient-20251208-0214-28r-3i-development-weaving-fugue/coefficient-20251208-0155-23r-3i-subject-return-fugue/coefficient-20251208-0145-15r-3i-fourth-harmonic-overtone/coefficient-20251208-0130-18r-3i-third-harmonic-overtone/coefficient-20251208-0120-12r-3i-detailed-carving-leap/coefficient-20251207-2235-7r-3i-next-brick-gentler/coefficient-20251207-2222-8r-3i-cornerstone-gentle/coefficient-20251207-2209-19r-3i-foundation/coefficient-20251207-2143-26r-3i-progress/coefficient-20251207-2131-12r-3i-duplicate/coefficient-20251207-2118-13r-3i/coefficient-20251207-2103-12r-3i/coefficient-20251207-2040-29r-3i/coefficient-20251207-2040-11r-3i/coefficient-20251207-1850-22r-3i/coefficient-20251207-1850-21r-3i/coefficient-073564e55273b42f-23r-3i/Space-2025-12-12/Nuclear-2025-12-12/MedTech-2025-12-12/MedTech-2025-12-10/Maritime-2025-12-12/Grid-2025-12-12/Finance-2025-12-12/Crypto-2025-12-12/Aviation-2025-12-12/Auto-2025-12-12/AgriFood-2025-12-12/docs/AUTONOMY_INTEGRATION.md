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

#### 8. Heritage & MAS Integration

**Multi-Agent System (MAS):**
- **`mas.agent`** - Agent events
- **`mas.coordination`** - Agent coordination (publishes to genesis.intent)
- **`mas.task`** - Task assignments
- **`mas.failure`** - Agent failures (triggers healing)

**Heritage Agents:**
- **`heritage.agent`** - Legacy agent events
- **`heritage.bridge`** - Bridge events

**Self-Healing:**
- **`heal.events`** - Self-healing events (publishes to genesis.heal)

**Event Publishers:**
- `bridge_backend/bridge_core/heritage/mas/`
- `bridge_backend/bridge_core/heritage/agents/`
- `bridge_backend/bridge_core/heritage/federation/`

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

### Super Engines Analysis

Using ScrollTongue with autonomy monitoring:

```python
from bridge_backend.bridge_core.engines import ScrollTongue
from bridge_backend.bridge_core.engines.adapters.tools_runtime_autonomy_link import publish_health_event

# Initialize engine
scroll = ScrollTongue()

# Perform analysis (can publish to scrolltongue.analysis)
result = scroll.inscribe("Test Document", "This is test content")

# Autonomy monitors the analysis
# Check with: grep "autonomy.scrolltongue_analysis" logs/
```

### Health Monitoring with Auto-Healing

Publishing health events that trigger autonomy:

```python
from bridge_backend.bridge_core.engines.adapters.tools_runtime_autonomy_link import publish_health_event

# Healthy status - publishes to genesis.fact
await publish_health_event("api_server", "healthy", {
    "uptime": 3600,
    "requests": 1000
})

# Degraded status - triggers autonomy healing
await publish_health_event("database", "degraded", {
    "connections": 95,  # Near limit
    "latency": 250
})
```

### Firewall Threat Response

High-threat firewall events trigger immediate autonomy response:

```python
from bridge_backend.bridge_core.engines.adapters.tools_runtime_autonomy_link import publish_firewall_event

# Low threat - analysis only
await publish_firewall_event(threat_level=3, analysis={
    "source_ip": "192.0.2.1",
    "request_count": 100
})

# High threat - triggers autonomy healing
await publish_firewall_event(threat_level=8, analysis={
    "source_ip": "198.51.100.1",
    "attack_type": "sql_injection",
    "requests_blocked": 500
})
```

### MAS Agent Coordination

Multi-Agent System coordination with autonomy:

```python
from bridge_backend.bridge_core.engines.adapters.heritage_mas_autonomy_link import publish_mas_event

# Normal coordination - publishes to genesis.intent
await publish_mas_event("coordination", {
    "agents": ["agent1", "agent2"],
    "task": "data_processing",
    "status": "in_progress"
})

# Agent failure - triggers autonomy healing
await publish_mas_event("failure", {
    "kind": "agent_failure",
    "agent_id": "agent3",
    "error": "timeout",
    "task": "analysis"
})
```

### Guardians Safety Validation

Guardians validate and can block dangerous autonomy actions:

```python
from bridge_backend.genesis.bus import genesis_bus

# Safe action - passes validation
await genesis_bus.publish("guardians.validation", {
    "type": "read_action",
    "resource": "user_data",
    "action": "query"
})

# Dangerous action - blocked by guardians
await genesis_bus.publish("guardians.validation", {
    "type": "recursive_delete",  # Contains "recursive" keyword
    "resource": "all_data",
    "action": "delete"
})
# Results in autonomy.action_blocked event
```

### Doctrine Compliance

Doctrine violations trigger autonomy healing:

```python
from bridge_backend.genesis.bus import genesis_bus

# Compliance check - publishes to genesis.fact
await genesis_bus.publish("doctrine.compliance", {
    "rule": "data_retention",
    "status": "compliant",
    "details": {"checked": 1000, "violations": 0}
})

# Violation - triggers autonomy healing
await genesis_bus.publish("doctrine.violation", {
    "type": "violation",
    "rule": "access_control",
    "severity": "high",
    "details": {"unauthorized_access": "admin_panel"}
})
```

### Network Diagnostics

Network issues trigger autonomy healing:

```python
from bridge_backend.bridge_core.engines.adapters.tools_runtime_autonomy_link import publish_network_event

# Normal diagnostics - publishes to genesis.fact
await publish_network_event("diagnostics", {
    "status": "ok",
    "latency": 50,
    "packet_loss": 0
})

# Network error - triggers autonomy healing
await publish_network_event("status", {
    "status": "error",
    "error": "connection_timeout",
    "latency": 5000,
    "retries": 3
})
```

### Runtime Deploy Events

Deployment events with autonomy monitoring:

```python
from bridge_backend.bridge_core.engines.adapters.tools_runtime_autonomy_link import publish_runtime_event

# Successful deploy - publishes to genesis.intent
await publish_runtime_event("deploy", {
    "type": "success",
    "version": "1.9.7",
    "environment": "production"
})

# Deploy failure - triggers autonomy healing
await publish_runtime_event("deploy", {
    "type": "deploy_failure",
    "version": "1.9.7",
    "error": "migration_failed",
    "rollback": True
})
```

## Testing

### Unit Tests

Run the comprehensive autonomy integration tests:

```bash
cd bridge_backend
python3 -m pytest tests/test_autonomy_comprehensive_integration.py -v
```

Run the original autonomy integration tests:

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

# Original topics
original_topics = [
    "triage.api", "triage.endpoint", "triage.diagnostics",
    "federation.events", "federation.heartbeat",
    "parity.check", "parity.autofix"
]

# Super Engines topics
super_engine_topics = [
    "scrolltongue.analysis", "scrolltongue.translation", "scrolltongue.pattern",
    "commerceforge.trade", "commerceforge.market", "commerceforge.portfolio",
    "auroraforge.visual", "auroraforge.creative", "auroraforge.render",
    "chronicleloom.chronicle", "chronicleloom.timeline", "chronicleloom.event",
    "calculuscore.computation", "calculuscore.optimization", "calculuscore.analysis",
    "qhelmsingularity.quantum", "qhelmsingularity.advanced", "qhelmsingularity.simulation"
]

# Core Systems topics
core_topics = [
    "fleet.command", "fleet.status",
    "custody.state", "custody.transfer",
    "console.command", "console.output",
    "captains.policy", "captains.decision",
    "guardians.validation", "guardians.alert",
    "registry.update", "registry.query",
    "doctrine.compliance", "doctrine.violation"
]

# Tools/Runtime topics
tools_topics = [
    "firewall.threat", "firewall.analysis",
    "network.diagnostics", "network.status",
    "health.check", "health.status",
    "runtime.deploy", "runtime.status",
    "metrics.snapshot", "metrics.anomaly"
]

# Heritage/MAS topics
heritage_topics = [
    "mas.agent", "mas.coordination", "mas.task", "mas.failure",
    "heritage.agent", "heritage.bridge", "heal.events"
]

all_topics = original_topics + super_engine_topics + core_topics + tools_topics + heritage_topics

print(f"Validating {len(all_topics)} autonomy integration topics...")
missing = []
for topic in all_topics:
    if topic in bus._valid_topics:
        print(f"✅ {topic}")
    else:
        print(f"❌ {topic} - MISSING")
        missing.append(topic)

print(f"\n{'='*60}")
if missing:
    print(f"❌ {len(missing)} topics missing: {', '.join(missing)}")
    sys.exit(1)
else:
    print(f"✅ All {len(all_topics)} topics registered successfully!")
    print(f"{'='*60}")
    print("\nIntegration Coverage:")
    print(f"  - Original: {len(original_topics)} topics")
    print(f"  - Super Engines: {len(super_engine_topics)} topics")
    print(f"  - Core Systems: {len(core_topics)} topics")
    print(f"  - Tools/Runtime: {len(tools_topics)} topics")
    print(f"  - Heritage/MAS: {len(heritage_topics)} topics")
SCRIPT
```

### Event Flow Testing

Test event propagation through the autonomy system:

```bash
python3 << 'SCRIPT'
import sys
import asyncio
sys.path.insert(0, 'bridge_backend')

from genesis.bus import genesis_bus

async def test_autonomy_flow():
    received = []
    
    async def capture(event):
        received.append(event)
    
    # Subscribe to autonomy outputs
    genesis_bus.subscribe("genesis.heal", capture)
    genesis_bus.subscribe("genesis.intent", capture)
    genesis_bus.subscribe("genesis.fact", capture)
    
    # Test health degradation → healing
    await genesis_bus.publish("health.status", {
        "component": "test",
        "status": "degraded"
    })
    
    await asyncio.sleep(0.2)
    
    heal_events = [e for e in received if e.get("type") == "autonomy.health_degraded"]
    
    if heal_events:
        print("✅ Health degradation → Autonomy healing: WORKING")
    else:
        print("❌ Health degradation → Autonomy healing: FAILED")
    
    # Test firewall threat → healing
    received.clear()
    await genesis_bus.publish("firewall.threat", {
        "threat_level": 9
    })
    
    await asyncio.sleep(0.2)
    
    threat_events = [e for e in received if e.get("type") == "autonomy.firewall_threat"]
    
    if threat_events:
        print("✅ Firewall threat → Autonomy healing: WORKING")
    else:
        print("❌ Firewall threat → Autonomy healing: FAILED")

asyncio.run(test_autonomy_flow())
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
