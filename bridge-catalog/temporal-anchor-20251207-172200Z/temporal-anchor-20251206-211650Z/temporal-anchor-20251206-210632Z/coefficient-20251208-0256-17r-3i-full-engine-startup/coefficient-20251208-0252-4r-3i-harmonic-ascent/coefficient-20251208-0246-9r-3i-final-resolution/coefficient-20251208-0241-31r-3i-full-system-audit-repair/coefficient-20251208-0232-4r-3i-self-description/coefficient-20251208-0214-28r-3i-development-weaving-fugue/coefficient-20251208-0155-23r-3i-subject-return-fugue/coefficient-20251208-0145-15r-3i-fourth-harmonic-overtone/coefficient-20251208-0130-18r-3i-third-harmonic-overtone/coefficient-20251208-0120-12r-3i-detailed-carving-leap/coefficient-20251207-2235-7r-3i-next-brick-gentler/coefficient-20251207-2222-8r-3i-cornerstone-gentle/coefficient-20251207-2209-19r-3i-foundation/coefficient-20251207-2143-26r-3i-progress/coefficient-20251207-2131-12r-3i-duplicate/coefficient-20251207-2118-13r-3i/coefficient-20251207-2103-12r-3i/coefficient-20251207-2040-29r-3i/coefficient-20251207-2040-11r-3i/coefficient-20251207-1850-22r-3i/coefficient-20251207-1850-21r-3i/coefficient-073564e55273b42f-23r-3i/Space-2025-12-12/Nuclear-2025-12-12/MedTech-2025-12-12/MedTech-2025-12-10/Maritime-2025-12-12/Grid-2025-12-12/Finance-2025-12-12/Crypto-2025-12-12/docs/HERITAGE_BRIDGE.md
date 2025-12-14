# Heritage Bridge Integration Guide

## Overview

The Heritage subsystem integrates the original "skeleton bridge" into SR-AIbridge as a first-class subsystem, providing:

- **Unified Event Bus**: Central event routing with Truth/Parser/Cascade hooks
- **MAS Components**: Multi-Agent System with fault injection and self-healing
- **Federation**: Cross-bridge task forwarding and heartbeat signaling
- **Agent Anchors**: Prim and Claude legacy agent implementations
- **Demo Presets**: Shakedown, MAS healing, and Federation demonstrations

## Architecture

### Directory Structure

```
bridge_backend/bridge_core/heritage/
├── __init__.py
├── event_bus.py              # Unified event bus
├── routes.py                 # FastAPI routes
├── mas/
│   ├── __init__.py
│   ├── adapters.py           # BridgeMASAdapter, SelfHealingMASAdapter
│   └── fault_injector.py     # FaultInjector
├── federation/
│   ├── __init__.py
│   ├── federation_client.py  # Federation client
│   └── live_ws.py            # WebSocket server
├── agents/
│   ├── __init__.py
│   ├── profiles.py           # Agent profiles
│   └── legacy_agents.py      # PrimAnchor, ClaudeAnchor
└── demos/
    ├── __init__.py
    ├── shakedown.py          # Shakedown demo
    ├── mas_demo.py           # MAS healing demo
    └── federation_demo.py    # Federation demo
```

### Event Bus Topics

The unified event bus supports the following topics:

- `bridge.events` - Bridge MAS events
- `heal.events` - Self-healing events
- `fault.events` - Fault injection events
- `federation.events` - Federation events
- `anchor.events` - Agent anchor events
- `demo.events` - Demo control events
- `heritage.events` - General heritage events
- `metrics.update` - Metrics updates

### Integration Points

#### Truth Engine Hook

```python
from bridge_core.heritage.event_bus import bus

def truth_validator(event: dict) -> dict:
    # Validate and enrich event with truth
    return event

bus.set_truth_validator(truth_validator)
```

#### Parser Engine Hook

```python
from bridge_core.heritage.event_bus import bus

def parser_normalizer(event: dict) -> dict:
    # Normalize event structure
    return event

bus.set_parser_normalizer(parser_normalizer)
```

#### Cascade Hooks

```python
from bridge_core.heritage.event_bus import bus

async def cascade_pre_hook(event: dict) -> dict:
    # Pre-processing
    return event

async def cascade_post_hook(event: dict) -> dict:
    # Post-processing
    return event

bus.add_cascade_pre(cascade_pre_hook)
bus.add_cascade_post(cascade_post_hook)
```

## API Endpoints

### Heritage Routes

#### Start Demo

```http
POST /heritage/demo/{mode}
```

Modes: `shakedown`, `mas`, `federation`

#### List Demo Modes

```http
GET /heritage/demo/modes
```

#### WebSocket Stats

```
WS /heritage/ws/stats
```

Real-time event streaming for Command Deck UI.

#### Heritage Status

```http
GET /heritage/status
```

## Usage Examples

### Subscribe to Events

```python
from bridge_core.heritage.event_bus import bus

async def my_handler(event: dict):
    print(f"Received event: {event}")

bus.subscribe("heritage.events", my_handler)
```

### Publish Events

```python
from bridge_core.heritage.event_bus import bus

await bus.publish("heritage.events", {
    "kind": "my.custom.event",
    "timestamp": datetime.utcnow().isoformat(),
    "payload": {"data": "example"}
})
```

### MAS Adapter Usage

```python
from bridge_core.heritage.mas.adapters import BridgeMASAdapter, SelfHealingMASAdapter

# Create adapter
log = []
mas = BridgeMASAdapter(order_write=lambda m: log.append(m))
healing = SelfHealingMASAdapter(mas, retry_delay=1.0, max_retries=3)

# Handle incoming message
await healing.handle_incoming({
    "event_type": "task.start",
    "task_id": "t1",
    "timestamp": "2024-01-01T00:00:00Z"
})
```

### Fault Injection

```python
from bridge_core.heritage.mas.fault_injector import FaultInjector

def write_log(msg):
    print(msg)

# Create fault injector
fi = FaultInjector(
    base_write=write_log,
    corrupt_rate=0.1,
    drop_rate=0.05
)

# Inject faults
await fi({"type": "log", "task_id": "t1"})
```

### Federation Client

```python
from bridge_core.heritage.federation.federation_client import FederationClient

# Create client
client = FederationClient(node_id="my-bridge")

# Forward task
await client.forward_task(
    task_id="t1",
    task_type="analysis",
    payload={"data": "test"},
    target_node="remote-bridge"
)

# Send heartbeat
await client.send_heartbeat(["remote-bridge"])
```

## Testing

All heritage components have comprehensive tests:

```bash
cd bridge_backend
pytest tests/test_heritage_bus.py
pytest tests/test_fault_injection.py
pytest tests/test_mas_healing.py
pytest tests/test_federation_smoke.py
```

## Compatibility

- **SQLite & PostgreSQL**: No migrations required
- **Python**: 3.8+
- **FastAPI**: 0.100.0+
- **asyncio**: Native support

## Feature Flags

Optional environment variables:

- `ENABLE_HERITAGE_DECK=true` - Enable Heritage Deck UI
- `ENABLE_FAULTS=true` - Enable fault injection
- `ENABLE_FEDERATION=true` - Enable federation features
