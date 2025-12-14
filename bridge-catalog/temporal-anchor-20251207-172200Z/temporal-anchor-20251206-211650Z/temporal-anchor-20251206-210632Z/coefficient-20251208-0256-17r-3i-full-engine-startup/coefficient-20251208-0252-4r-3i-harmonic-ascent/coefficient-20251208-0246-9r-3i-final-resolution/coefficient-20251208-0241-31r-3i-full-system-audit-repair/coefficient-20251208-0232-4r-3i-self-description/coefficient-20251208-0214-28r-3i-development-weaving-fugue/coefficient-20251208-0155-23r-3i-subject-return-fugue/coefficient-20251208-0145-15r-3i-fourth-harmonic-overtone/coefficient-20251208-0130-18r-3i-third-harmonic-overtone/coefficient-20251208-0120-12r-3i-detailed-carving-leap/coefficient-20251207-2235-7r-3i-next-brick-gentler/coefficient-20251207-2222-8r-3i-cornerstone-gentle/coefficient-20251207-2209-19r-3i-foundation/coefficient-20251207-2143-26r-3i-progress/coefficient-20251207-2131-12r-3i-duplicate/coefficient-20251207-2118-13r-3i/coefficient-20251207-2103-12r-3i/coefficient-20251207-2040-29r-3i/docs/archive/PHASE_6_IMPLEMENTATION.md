# Phase 6 — Chaos & Recovery Suite Implementation

## Overview

This implementation adds autonomous chaos injection and recovery capabilities to the SR-AIBridge federation, enabling continuous validation of failover mechanisms and self-healing operations.

## Components

### 1. Chaos Injector (`brh/chaos.py`)

**Purpose**: Simulates random container failures to test resilience and failover mechanisms.

**Features**:
- Configurable failure interval (default: 10 minutes)
- Configurable failure probability (default: 15%)
- Random container selection for termination
- Event logging integration
- Disabled by default for safety

**Configuration**:
```bash
BRH_CHAOS_ENABLED=true       # Enable chaos injection (default: false)
BRH_CHAOS_INTERVAL=600       # Interval in seconds (default: 600)
BRH_KILL_PROB=0.15          # Probability of killing a container (default: 0.15)
```

**Usage**:
```python
from brh import chaos
chaos.start()  # Starts chaos injector in background thread
```

### 2. Recovery Watchtower (`brh/recovery.py`)

**Purpose**: Monitors container health and ensures consistency with leader state.

**Features**:
- Leader-specific recovery (restarts failed containers)
- Witness-specific cleanup (releases stray containers)
- Automatic container health monitoring
- Event logging integration
- Enabled by default

**Configuration**:
```bash
BRH_RECOVERY_ENABLED=true    # Enable recovery watchtower (default: true)
```

**Usage**:
```python
from brh import recovery
recovery.start()  # Starts recovery watchtower in background thread
```

### 3. Event Logging System (`brh/api.py`)

**Purpose**: Provides centralized event logging and federation state monitoring.

**New Endpoints**:

#### `GET /federation/state`
Returns current federation state including leader and peer information.

**Response**:
```json
{
  "leader": "node-001",
  "peers": [
    {
      "node": "node-001",
      "epoch": 1699056000,
      "status": "alive",
      "uptime": "ok"
    }
  ]
}
```

#### `GET /events`
Returns recent events from the event log (last 50 events).

**Response**:
```json
[
  {
    "time": "2025-11-04T01:43:21.123456Z",
    "message": "CHAOS: killed container brh_api"
  },
  {
    "time": "2025-11-04T01:45:21.123456Z",
    "message": "RECOVERY: restarted container brh_api"
  }
]
```

**Event Logging Function**:
```python
from brh.api import log_event
log_event("Custom event message")
```

### 4. Federation Console UI (`bridge-frontend/src/components/FederationConsole.jsx`)

**Purpose**: Real-time visualization of federation state, events, and health.

**Features**:
- Live federation status display
- Current leader indicator
- Peer node cards with status
- Real-time event log feed
- Auto-refresh every 8 seconds
- Leader highlighting (green glow effect)

**Integration**:
```jsx
import FederationConsole from '../components/FederationConsole';

function MyPage() {
  return (
    <div>
      <FederationConsole />
    </div>
  );
}
```

### 5. Enhanced Consensus with Ledger Feedback (`brh/consensus.py`)

**Purpose**: Forwards consensus events to the Sovereign Ledger for immutable audit trail.

**Features**:
- Automatic ledger feedback on consensus
- Event logging for heartbeats and leader changes
- Promotion/demotion event tracking

**Ledger Feedback Payload**:
```json
{
  "epoch": 1699056000,
  "leader": "node-001",
  "peers": ["node-001", "node-002"],
  "status": "consensus-ok",
  "signature": "abcd1234...",
  "bridge": "SR-AIBRIDGE"
}
```

### 6. Runtime Configuration (`bridge.runtime.yaml`)

**New Configuration Section**:
```yaml
runtime:
  health:
    recovery: true
    chaos:
      enabled: false      # Disabled by default
      interval: 600       # 10 minutes
      probability: 0.15   # 15% chance
  ledger:
    forward:
      - federation/heartbeat
      - federation/consensus
      - recovery
```

## Testing

### Unit Tests

**Chaos Module Tests** (`brh/test_chaos_recovery.py`):
- ✓ Chaos disabled by default
- ✓ Chaos enables when configured
- ✓ Chaos interval configuration
- ✓ Chaos probability configuration
- ✓ Recovery enabled by default
- ✓ Recovery disabled when configured
- ✓ Recovery disabled without Docker

**API Endpoint Tests** (`brh/test_api_endpoints.py`):
- ✓ Event logging functionality
- ✓ Event timestamp generation
- ✓ Event log size limiting
- ✓ Federation state endpoint
- ✓ Peer structure validation
- ✓ Events endpoint
- ✓ Events limit to 50

**Integration Tests** (`brh/test_phase6_integration.py`):
- ✓ Module imports
- ✓ API endpoints availability
- ✓ Configuration options

### Running Tests

```bash
# Run all Phase 6 tests
pytest brh/test_chaos_recovery.py brh/test_api_endpoints.py -v

# Run integration test
python brh/test_phase6_integration.py

# Run specific test
pytest brh/test_chaos_recovery.py::TestChaosModule::test_chaos_enabled_starts_thread -v
```

## Deployment

### Prerequisites

1. Docker SDK for Python installed
2. FastAPI and Uvicorn installed
3. React frontend with Framer Motion

### Installation

All dependencies are already included in existing requirements:
```bash
pip install -r requirements.txt
pip install -r brh/requirements.txt
```

### Starting the System

The chaos and recovery modules are automatically started by `brh/run.py`:

```bash
python -m brh.run
```

This will:
1. Start heartbeat daemon
2. Start consensus coordinator
3. Start chaos injector (if enabled)
4. Start recovery watchtower (if enabled)
5. Deploy all services from `bridge.runtime.yaml`

### Enabling Chaos for Testing

```bash
export BRH_CHAOS_ENABLED=true
export BRH_CHAOS_INTERVAL=300  # 5 minutes for testing
python -m brh.run
```

## Security Considerations

1. **Chaos Injection**: Disabled by default to prevent accidental production disruption
2. **Event Logging**: Limited to 1000 events to prevent memory exhaustion
3. **API Endpoints**: CORS-protected with configurable origins
4. **Docker Operations**: Requires appropriate Docker socket permissions

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    BRH Runtime (run.py)                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Heartbeat   │  │  Consensus   │  │    Chaos     │ │
│  │   Daemon     │  │ Coordinator  │  │  Injector    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Recovery   │  │     API      │  │    Event     │ │
│  │  Watchtower  │  │   Server     │  │     Log      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Federation Console (React UI)              │
├─────────────────────────────────────────────────────────┤
│  • Live federation state                                │
│  • Peer status cards                                    │
│  • Event log feed                                       │
│  • Leader highlighting                                  │
└─────────────────────────────────────────────────────────┘
```

## Event Flow

```
1. Chaos Injector → Kills Random Container
   ↓
2. Event Logged → "CHAOS: killed container X"
   ↓
3. Recovery Watchtower Detects Failure
   ↓
4. Leader Restarts Container
   ↓
5. Event Logged → "RECOVERY: restarted container X"
   ↓
6. Consensus Updates → Ledger Feedback
   ↓
7. Event Logged → "CONSENSUS: elected leader=X"
   ↓
8. UI Updates → Real-time Display
```

## Troubleshooting

### Chaos not working
- Check `BRH_CHAOS_ENABLED=true` is set
- Verify Docker containers are running
- Check logs for chaos events

### Recovery not working
- Ensure Docker SDK is installed: `pip install docker`
- Verify Docker socket permissions
- Check if recovery is enabled (default: true)

### Events not appearing in UI
- Check API endpoint is accessible: `curl http://localhost:7878/events`
- Verify CORS settings in `brh/api.py`
- Check browser console for fetch errors

## Performance Impact

- **Chaos Injector**: Minimal (sleeps most of the time)
- **Recovery Watchtower**: Low (checks every 2 minutes)
- **Event Logging**: Minimal (in-memory, limited to 1000 events)
- **API Endpoints**: Low (simple JSON responses)

## Future Enhancements

1. **Persistent Event Storage**: Save events to database for long-term audit
2. **Chaos Strategies**: Implement different chaos patterns (network, CPU, memory)
3. **Recovery Metrics**: Track MTTR (Mean Time To Recovery)
4. **Alert Integration**: Send notifications on critical events
5. **Chaos Scheduling**: Allow scheduled chaos windows for testing

## References

- [Chaos Engineering Principles](https://principlesofchaos.org/)
- [Netflix Chaos Monkey](https://github.com/Netflix/chaosmonkey)
- [Kubernetes Chaos Engineering](https://kubernetes.io/blog/2021/12/22/kubernetes-1-23-release-announcement/)
