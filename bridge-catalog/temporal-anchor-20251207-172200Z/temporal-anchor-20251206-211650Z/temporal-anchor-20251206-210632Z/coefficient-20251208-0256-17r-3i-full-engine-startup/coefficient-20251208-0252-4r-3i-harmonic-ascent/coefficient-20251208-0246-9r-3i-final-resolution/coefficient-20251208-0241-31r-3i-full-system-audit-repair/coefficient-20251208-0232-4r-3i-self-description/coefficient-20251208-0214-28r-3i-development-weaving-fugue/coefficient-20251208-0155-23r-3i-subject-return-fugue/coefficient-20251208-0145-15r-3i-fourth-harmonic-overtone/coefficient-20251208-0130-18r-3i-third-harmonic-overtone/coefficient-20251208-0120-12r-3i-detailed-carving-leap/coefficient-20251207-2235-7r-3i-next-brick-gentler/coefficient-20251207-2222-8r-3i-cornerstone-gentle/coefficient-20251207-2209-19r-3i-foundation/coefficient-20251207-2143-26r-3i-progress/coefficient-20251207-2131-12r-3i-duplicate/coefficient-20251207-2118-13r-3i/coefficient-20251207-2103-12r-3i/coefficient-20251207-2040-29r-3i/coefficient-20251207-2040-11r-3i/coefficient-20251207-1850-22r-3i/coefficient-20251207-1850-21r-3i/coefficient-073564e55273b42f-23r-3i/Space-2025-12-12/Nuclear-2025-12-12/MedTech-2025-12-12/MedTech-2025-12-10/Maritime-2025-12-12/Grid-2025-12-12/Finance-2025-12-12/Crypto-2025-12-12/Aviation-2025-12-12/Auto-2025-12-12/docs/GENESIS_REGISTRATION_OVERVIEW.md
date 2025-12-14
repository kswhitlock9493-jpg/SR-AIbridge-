# Genesis Registration Overview

## 🌌 Node Registration & Federation Protocol

This document describes how the Embedded Autonomy Node (EAN) registers with the Genesis Bus and becomes part of the SR-AIbridge federation.

## Overview

Genesis Registration is the process by which autonomous engines and nodes announce their presence, capabilities, and status to the central Genesis Bus. This enables:

- **Discovery**: Other engines can find and interact with registered nodes
- **Coordination**: Genesis Orchestrator can route events appropriately
- **Monitoring**: Central visibility into all active components
- **Federation**: Nodes join the distributed intelligence network

## Registration Process

### 1. Node Initialization

When the Embedded Autonomy Node starts, it creates a registration payload:

```python
node = {
    "engine": "autonomy_node",
    "location": ".github/autonomy_node",
    "status": "active",
    "type": "micro_bridge",
    "certified": True,
    "version": "1.9.7n"
}
```

### 2. Genesis Bus Connection

The node attempts to connect to the Genesis Bus:

```python
from bridge_backend.genesis.bus import genesis_bus

if genesis_bus.is_enabled():
    # Proceed with registration
else:
    # Fall back to offline mode
```

### 3. Event Publication

Registration is published as a Genesis event:

```python
await genesis_bus.publish("genesis.node.register", node)
```

### 4. Confirmation

If successful, the node receives confirmation and is now part of the federation:

```
✅ Embedded Autonomy Node registered successfully.
```

## Registration Payload

### Standard Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `engine` | string | Unique engine identifier | `"autonomy_node"` |
| `location` | string | File system path | `".github/autonomy_node"` |
| `status` | string | Current operational status | `"active"` |
| `type` | string | Engine classification | `"micro_bridge"` |
| `certified` | boolean | Truth Engine certification | `true` |
| `version` | string | Engine version | `"1.9.7n"` |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `capabilities` | array | Supported operations |
| `dependencies` | array | Required other engines |
| `endpoints` | object | API endpoints (if applicable) |
| `health_check_url` | string | Health monitoring endpoint |
| `metadata` | object | Additional engine-specific data |

### Example Full Registration

```json
{
  "engine": "autonomy_node",
  "location": ".github/autonomy_node",
  "status": "active",
  "type": "micro_bridge",
  "certified": true,
  "version": "1.9.7n",
  "capabilities": [
    "repository_scanning",
    "safe_repair",
    "truth_verification",
    "cascade_sync"
  ],
  "dependencies": [
    "genesis_bus",
    "truth_engine",
    "cascade_engine"
  ],
  "metadata": {
    "platform": "github_actions",
    "interval_hours": 6,
    "self_heal_enabled": true
  }
}
```

## Registration States

### Active

Node is running and operational:

```json
{
  "status": "active",
  "last_heartbeat": "2025-10-13T12:00:00Z"
}
```

### Inactive

Node is registered but not currently running:

```json
{
  "status": "inactive",
  "reason": "scheduled_downtime"
}
```

### Degraded

Node is running with reduced functionality:

```json
{
  "status": "degraded",
  "reason": "genesis_bus_offline",
  "affected_capabilities": ["telemetry", "coordination"]
}
```

### Failed

Node encountered critical error:

```json
{
  "status": "failed",
  "reason": "configuration_error",
  "error": "Invalid node_config.json"
}
```

## Genesis Bus Topics

### Registration Topic

**Topic**: `genesis.node.register`

**Purpose**: Announce node presence and capabilities

**Payload**:
```json
{
  "engine": "autonomy_node",
  "location": ".github/autonomy_node",
  "status": "active",
  "type": "micro_bridge",
  "certified": true,
  "version": "1.9.7n"
}
```

**Subscribers**:
- Genesis Orchestrator
- Genesis Introspection
- Monitoring systems

### Report Topic

**Topic**: `genesis.autonomy_node.report`

**Purpose**: Publish audit reports and findings

**Payload**:
```json
{
  "timestamp": "2025-10-13T12:00:00Z",
  "findings_count": 5,
  "fixes_count": 5,
  "status": "complete",
  "report_path": ".github/autonomy_node/reports/summary_20251013.json"
}
```

### Status Topics

**Available Topics**:
- `autonomy_node.scan.complete` - Scan finished
- `autonomy_node.repair.applied` - Repairs completed
- `autonomy_node.truth.verified` - Truth certification done
- `autonomy_node.cascade.synced` - Cascade sync complete

## Federation Integration

### Discovery

Other engines can discover the node:

```python
from bridge_backend.genesis.introspection import GenesisIntrospection

introspection = GenesisIntrospection()
nodes = await introspection.list_registered_nodes()

# Find autonomy node
autonomy_node = next(
    n for n in nodes 
    if n["engine"] == "autonomy_node"
)
```

### Coordination

Genesis Orchestrator routes events to appropriate nodes:

```python
from bridge_backend.genesis.orchestration import GenesisOrchestrator

orchestrator = GenesisOrchestrator()

# Route repair request to autonomy node
await orchestrator.route_event(
    "repair.request",
    target="autonomy_node"
)
```

### Health Monitoring

Monitor node health through Genesis:

```python
# Check node status
status = await introspection.get_node_status("autonomy_node")

if status["status"] != "active":
    alert_admins(f"Autonomy node is {status['status']}")
```

## Registration Implementation

### Module Location

`bridge_backend/genesis/registration.py`

### Main Function

```python
def register_embedded_nodes() -> Dict[str, Any]:
    """
    Register the Embedded Autonomy Node with Genesis Bus
    
    Returns:
        Dictionary containing registration status and node information
    """
```

### Usage in Application

```python
# During application startup
from bridge_backend.genesis.registration import register_embedded_nodes

# Register node
result = register_embedded_nodes()

if result["registered"]:
    logger.info("✅ Node registered successfully")
else:
    logger.warning(f"⚠️ Registration failed: {result['reason']}")
```

### Usage in Workflow

The node self-registers when run via GitHub Actions:

```python
# In .github/autonomy_node/core.py
if config.get("genesis_registration"):
    from bridge_backend.genesis.registration import register_embedded_nodes
    register_embedded_nodes()
```

## Configuration

### Enable/Disable Registration

In `node_config.json`:

```json
{
  "genesis_registration": true
}
```

### Environment Variables

```bash
# Enable Genesis mode
export GENESIS_MODE="enabled"

# Enable strict policy
export GENESIS_STRICT_POLICY="true"
```

### Conditional Registration

```python
import os

# Only register in production
if os.getenv("ENVIRONMENT") == "production":
    register_embedded_nodes()
```

## Offline Mode

When Genesis Bus is unavailable:

```python
if not genesis_bus.is_enabled():
    logger.warning("⚠️ Genesis Bus not enabled, skipping node registration.")
    return {
        "registered": False,
        "reason": "genesis_disabled",
        "node": node,
        "offline_mode": True
    }
```

The node continues to operate but:
- No telemetry published
- No coordination with other engines
- Reports stored locally only
- Independent operation

## Security Considerations

### Authentication

Registration does not require authentication as it's:
- Internal to the repository
- Running in GitHub's secure sandbox
- Publishing to internal event bus only

### Authorization

Only certain operations trigger registration:
- Push to main branch (CI context)
- Scheduled workflow (CI context)
- Manual dispatch (authorized user)

### Validation

Genesis Bus validates registration payloads:

```python
# In GenesisEventBus.publish()
if topic not in self._valid_topics:
    raise ValueError(f"Invalid topic: {topic}")
```

### Encryption

Events on Genesis Bus are:
- Not encrypted (internal communication)
- Logged for audit
- Retained per policy

## Monitoring & Debugging

### Check Registration Status

```python
from bridge_backend.genesis.introspection import GenesisIntrospection

introspection = GenesisIntrospection()
nodes = await introspection.list_registered_nodes()

print(f"Registered nodes: {len(nodes)}")
for node in nodes:
    print(f"  - {node['engine']} ({node['status']})")
```

### View Registration Events

```python
from bridge_backend.genesis.bus import genesis_bus

# Get recent events
events = genesis_bus.get_event_history(limit=10)

# Filter registration events
registrations = [
    e for e in events 
    if e["topic"] == "genesis.node.register"
]
```

### Debug Registration Failures

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Attempt registration
result = register_embedded_nodes()

if not result["registered"]:
    print(f"Registration failed: {result['reason']}")
    print(f"Node info: {result['node']}")
```

## Best Practices

1. **Always Register**: Enable genesis_registration in production
2. **Handle Failures Gracefully**: Don't crash if registration fails
3. **Update Status**: Re-register on significant changes
4. **Monitor Health**: Check registration status regularly
5. **Clean Deregistration**: Announce when shutting down
6. **Version Tracking**: Include version in registration
7. **Metadata Rich**: Provide helpful metadata

## Troubleshooting

### Registration Not Appearing

**Check**:
1. Genesis Bus enabled: `GENESIS_MODE=enabled`
2. Topic in valid topics list
3. Node actually running
4. No exceptions in logs

### Duplicate Registrations

**Cause**: Node re-registering on each run

**Solution**: This is expected behavior; latest registration wins

### Registration Stale

**Cause**: Node not running but still registered

**Solution**: Implement heartbeat or TTL for registrations

### Cannot Find Registered Node

**Check**:
1. Correct engine name
2. Genesis Introspection initialized
3. Recent registration (check timestamp)
4. Event history retention

## Future Enhancements

- [ ] Heartbeat mechanism
- [ ] De-registration on shutdown
- [ ] Registration TTL
- [ ] Node capability negotiation
- [ ] Dynamic capability updates
- [ ] Registration clustering
- [ ] Cross-repository discovery
- [ ] Federation authentication

## See Also

- [Embedded Autonomy Node Documentation](EMBEDDED_AUTONOMY_NODE.md)
- [Genesis Bus Documentation](GENESIS_V2_GUIDE.md)
- [Genesis Orchestration](GENESIS_V2_QUICK_REF.md)
- [Total Autonomy Protocol](TOTAL_AUTONOMY_PROTOCOL.md)
