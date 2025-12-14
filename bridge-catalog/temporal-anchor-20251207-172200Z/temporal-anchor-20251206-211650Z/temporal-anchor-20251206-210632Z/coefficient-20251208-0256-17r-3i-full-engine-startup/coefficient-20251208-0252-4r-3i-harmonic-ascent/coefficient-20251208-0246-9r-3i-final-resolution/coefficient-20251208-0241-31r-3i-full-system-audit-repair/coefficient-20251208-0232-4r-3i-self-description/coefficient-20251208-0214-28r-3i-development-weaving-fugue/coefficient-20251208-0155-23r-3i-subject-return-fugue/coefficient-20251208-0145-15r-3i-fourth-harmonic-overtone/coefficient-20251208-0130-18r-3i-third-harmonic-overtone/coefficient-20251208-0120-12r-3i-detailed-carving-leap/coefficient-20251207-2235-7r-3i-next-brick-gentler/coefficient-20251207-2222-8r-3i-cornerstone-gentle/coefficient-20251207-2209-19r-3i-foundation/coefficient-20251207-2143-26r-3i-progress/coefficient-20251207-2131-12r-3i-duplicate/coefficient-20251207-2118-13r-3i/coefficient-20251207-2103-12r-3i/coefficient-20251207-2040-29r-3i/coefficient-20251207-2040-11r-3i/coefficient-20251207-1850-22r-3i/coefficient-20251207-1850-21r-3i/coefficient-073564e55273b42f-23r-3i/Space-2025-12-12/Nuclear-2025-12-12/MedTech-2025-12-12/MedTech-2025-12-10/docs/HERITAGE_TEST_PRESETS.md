# Heritage Test Presets Guide

## Overview

Heritage subsystem includes three demo presets to showcase different capabilities:

1. **Shakedown**: Basic system stress test
2. **MAS**: Multi-Agent System fault injection and healing
3. **Federation**: Cross-bridge communication

## Running Demos

### From UI

Navigate to `/deck` and use the Demo Launchpad panel:
- Click "Shakedown" for basic test
- Click "MAS Healing" for fault injection demo
- Click "Federation" for federation demo

### From API

```bash
# Shakedown
curl -X POST http://localhost:8000/heritage/demo/shakedown

# MAS Healing
curl -X POST http://localhost:8000/heritage/demo/mas

# Federation
curl -X POST http://localhost:8000/heritage/demo/federation
```

### From Python

```python
from bridge_core.heritage.demos.shakedown import run_shakedown
from bridge_core.heritage.demos.mas_demo import run_mas
from bridge_core.heritage.demos.federation_demo import run_federation

# Run demos
await run_shakedown()
await run_mas()
await run_federation()
```

## Demo Details

### 1. Shakedown

**Purpose**: Basic system stress test with simulated events

**Duration**: ~3 seconds

**Events Generated**:
- Task created
- Task processing
- Task completed
- Agent status update
- System health check

**Expected Signals**:
- 5 heritage.shakedown.event messages
- demo.shakedown.start message
- demo.shakedown.complete message

**Success Criteria**:
- All events published successfully
- No errors in event bus
- Clean completion signal

### 2. MAS Healing

**Purpose**: Demonstrate fault injection and self-healing capabilities

**Duration**: ~2 seconds

**Components Tested**:
- FaultInjector (30% corrupt rate, 10% drop rate)
- BridgeMASAdapter
- SelfHealingMASAdapter

**Events Generated**:
- Valid MAS messages
- Invalid messages (triggers healing)
- Fault injection events
- Heal/resend request events

**Expected Signals**:
- heritage.mas.message events
- fault.events (corrupt, drop)
- heal.events (resend_request)
- demo.mas.complete message

**Success Criteria**:
- Invalid messages trigger heal.resend_request
- Fault injector corrupts/drops messages as configured
- Healing adapter handles invalid messages gracefully

### 3. Federation

**Purpose**: Demonstrate cross-bridge task forwarding and heartbeats

**Duration**: ~3 seconds

**Components Tested**:
- FederationClient
- Task forwarding
- Heartbeat signaling
- ACK handling

**Events Generated**:
- Heartbeat signals
- Task forward requests
- ACK responses

**Expected Signals**:
- federation.heartbeat events
- federation.task_forward events
- federation.ack events
- heritage.federation.operation events
- demo.federation.complete message

**Success Criteria**:
- Heartbeats sent successfully
- Tasks forwarded to target nodes
- ACKs received and handled

## Monitoring

### Event Stream

Watch the Event Stream Tap panel in Command Deck V1 for real-time event flow.

### Logs

Backend logs show detailed event processing:

```bash
cd bridge_backend
tail -f logs/heritage.log
```

### Metrics

Check metrics updates during demo runs:
- Task queue changes
- Agent health fluctuations
- Event counts

## Interpreting Results

### Shakedown Success

```
✅ 5 events processed
✅ All subsystems responsive
✅ Clean completion
```

### MAS Healing Success

```
✅ Faults injected (corrupt/drop)
✅ Healing triggered for invalid messages
✅ Resend requests generated
✅ Log entries created
```

### Federation Success

```
✅ Heartbeats sent
✅ Tasks forwarded
✅ ACKs handled
✅ 5 operations completed
```

## Troubleshooting

### Demo Doesn't Start

1. Check backend is running
2. Verify `/heritage/demo/{mode}` endpoint accessible
3. Check logs for errors

### No Events in UI

1. Verify WebSocket connection
2. Check event bus subscribers
3. Ensure demo completed successfully

### Fault Injection Not Working

1. Check fault rates in FaultInjector config
2. Verify fault.events are published
3. Review fault injector logs

## Custom Demos

Create your own demo presets:

```python
# bridge_core/heritage/demos/my_demo.py

import asyncio
from ..event_bus import bus
from datetime import datetime

async def run_my_demo():
    """Custom demo"""
    await bus.publish("demo.events", {
        "kind": "demo.custom.start",
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Your demo logic here
    
    await bus.publish("demo.events", {
        "kind": "demo.custom.complete",
        "timestamp": datetime.utcnow().isoformat()
    })
```

Register in routes:

```python
# bridge_core/heritage/routes.py

from .demos.my_demo import run_my_demo

@router.post("/demo/custom")
async def start_custom_demo():
    await run_my_demo()
    return {"status": "Started custom demo"}
```

## Best Practices

1. **Run demos in sequence**: Wait for completion before starting next
2. **Monitor event stream**: Watch for expected event patterns
3. **Check logs**: Verify no errors during demo execution
4. **Review metrics**: Ensure metrics update correctly
5. **Clear events**: Refresh UI between demo runs for clarity

## Future Enhancements

- [ ] Configurable demo parameters
- [ ] Demo recording and playback
- [ ] Automated test assertions
- [ ] Performance benchmarking
- [ ] Custom demo templates
