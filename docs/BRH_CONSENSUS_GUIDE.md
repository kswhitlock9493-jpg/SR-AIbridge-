# BRH Consensus and Leader Election Guide

## Overview

The Bridge Runtime Handler (BRH) now includes a **Sovereign Consensus Election Layer** that enables multiple BRH nodes to form a self-governing federation. This system automatically elects a leader node and manages graceful handover during leadership transitions.

## Architecture

### Components

1. **`brh/consensus.py`** - Consensus Coordinator Module
   - Tracks peer nodes via heartbeat listeners
   - Elects leader based on highest epoch (most recent)
   - Broadcasts consensus decisions to Forge
   - Polls Forge for current leader status

2. **`brh/role.py`** - Role State Management
   - Tracks whether this node is leader or witness
   - Maintains leader ID and optional lease token
   - Thread-safe state management

3. **`brh/handover.py`** - Leader Promotion/Demotion
   - Adopts orphaned containers on promotion
   - Relinquishes ownership on demotion
   - Supports zero-downtime handover

4. **Forge Endpoints** (`netlify/functions/forge-resolver.js`)
   - `POST /federation/consensus` - Receives election reports
   - `GET /federation/leader` - Returns current leader

## Configuration

### Environment Variables

```bash
# Node identity (must be unique per BRH instance)
BRH_NODE_ID=brh-node-01

# Environment name (for container filtering)
BRH_ENV=production

# Forge root endpoint
FORGE_DOMINION_ROOT=dominion://sovereign.bridge

# Consensus settings
BRH_CONSENSUS_ENABLED=true
BRH_CONSENSUS_INTERVAL=180  # seconds (default: 3 minutes)

# Heartbeat settings
BRH_HEARTBEAT_ENABLED=true
BRH_HEARTBEAT_INTERVAL=60   # seconds (default: 1 minute)

# Security seal
DOMINION_SEAL=your-secret-seal-here
```

### Runtime Manifest (`bridge.runtime.yaml`)

```yaml
runtime:
  federation:
    heartbeat:
      enabled: true
      interval: 60
      endpoint: forge://federation/heartbeat
      ledger_forward: true
      ttl: 300
    consensus:
      enabled: true
      interval: 180
      election_method: highest_epoch
      ledger_forward: true
```

## How It Works

### 1. Heartbeat Phase
Each BRH node continuously sends signed heartbeats to the Forge:

```
BRH Node A → [heartbeat] → Forge ← [heartbeat] → BRH Node B
```

### 2. Consensus Election
Every 3 minutes (configurable), the consensus module:
1. Collects all active peer heartbeats
2. Filters out stale nodes (>300s since last heartbeat)
3. Elects leader using highest epoch
4. Broadcasts election result to Forge

```python
# Election algorithm
def elect_leader():
    active_peers = filter_active(peers)  # last_seen < 300s
    leader = max(active_peers, key=lambda p: p.epoch)
    return leader
```

### 3. Leader Polling
Nodes poll Forge every 10 seconds for current leader:

```
BRH Node → GET /federation/leader → Forge
         ← {"leader": "node-02", "lease": null}
```

### 4. Role Transitions

#### Promotion (Witness → Leader)
```
1. Detect: I am now the leader
2. Print: [CN] PROMOTE → I am leader
3. Adopt: Take ownership of orphaned containers
   - Update container labels: brh.owner=<my-node-id>
4. Enable: Accept deploy hooks and orchestration
```

#### Demotion (Leader → Witness)
```
1. Detect: Another node is now leader
2. Print: [CN] DEMOTE → I am witness
3. Release: Drop ownership from my containers
   - Remove brh.owner label
4. Disable: Reject deploy hooks
```

### 5. Container Ownership

Containers are labeled with:
```yaml
labels:
  brh.service: api
  brh.env: production
  brh.owner: brh-node-01  # Current owner
```

During handover:
- **Zero-downtime mode** (default): Old leader removes `brh.owner`, new leader adds it
- **Drain mode** (optional): Old leader stops containers before releasing

## API Behavior

### `/deploy` Endpoint

**Leader Node:**
```bash
curl -X POST http://leader:8000/deploy -d '{"image": "myapp:latest"}'
# Response: {"status": "restarted", "image": "myapp:latest"}
```

**Witness Node:**
```bash
curl -X POST http://witness:8000/deploy -d '{"image": "myapp:latest"}'
# Response: {"status": "ignored", "reason": "not-leader"}
```

## Testing

### Unit Tests
```bash
cd /home/runner/work/SR-AIbridge-/SR-AIbridge-
PYTHONPATH=. python3 brh/test_consensus_role.py
```

### Integration Tests
```bash
PYTHONPATH=. python3 brh/test_integration.py
```

### Manual Testing (Two Node Setup)

1. **Start Node 1:**
```bash
export BRH_NODE_ID=node-alpha
export BRH_ENV=test
python3 -m brh.run
```

2. **Start Node 2:**
```bash
export BRH_NODE_ID=node-beta
export BRH_ENV=test
python3 -m brh.run
```

3. **Kill Node 1** (simulating failure)
   - Node 2 should automatically become leader within one consensus cycle (3 min)

4. **Check logs:**
```
[CN] PROMOTE → I am leader (node-beta)
[PROMOTE] Adopted brh_api
```

## Security Considerations

1. **Signature Verification**: All consensus messages are HMAC-signed
2. **Lease Tokens** (optional): Forge can issue cryptographic leases
3. **Stale Node Filtering**: Nodes not seen for >5 minutes are excluded
4. **Command Injection Protection**: Image names are validated before execution

## Troubleshooting

### No Leader Elected
**Symptom:** `elect_leader()` returns `None`

**Causes:**
- No active peers (all nodes seen >300s ago)
- Heartbeat daemon not running
- Network connectivity issues

**Solution:**
```bash
# Check heartbeat status
journalctl -u brh -f | grep HB

# Verify peers
curl http://forge/federation/leader
```

### Containers Not Adopted
**Symptom:** Promotion occurs but containers not labeled

**Causes:**
- Docker SDK not installed (`pip install docker`)
- Docker daemon not accessible
- Wrong environment name in filter

**Solution:**
```bash
# Install Docker SDK
pip install docker

# Check Docker access
python3 -c "import docker; print(docker.from_env().ping())"
```

### Deploy Hook Rejected
**Symptom:** `/deploy` returns `{"status": "ignored", "reason": "not-leader"}`

**Cause:** Node is not currently the leader

**Solution:**
```bash
# Check role status
curl http://forge/federation/leader

# Wait for next consensus cycle or promote manually
```

## Advanced: Custom Demotion Policy

By default, demotion uses zero-downtime handover. To enable drain-and-stop:

**Edit `brh/consensus.py`:**
```python
def apply_leader_change(new_leader: str, lease_token: str | None = None):
    # ... existing code ...
    
    if prev_was_leader and not now_leader:
        print(f"[CN] DEMOTE → I am witness (leader={new_leader})")
        # Option 1: Zero-downtime (default)
        # handover.relinquish_ownership(ENV)
        
        # Option 2: Stop workloads on demotion
        handover.drain_and_stop(ENV, timeout=30)
```

## Future Enhancements

1. **Forge Lease System**: Cryptographic lease tokens for enhanced security
2. **Priority Weights**: Allow nodes to have different election priorities
3. **Split-Brain Detection**: Handle network partitions gracefully
4. **Metrics Export**: Prometheus metrics for consensus health
5. **Web Dashboard**: Real-time visualization of federation state

## References

- [BRH Deployment Guide](./BRH_DEPLOYMENT_GUIDE.md)
- [Forge Dominion Guide](./FORGE_DOMINION_DEPLOYMENT_GUIDE.md)
- [Bridge Runtime YAML Spec](./bridge.runtime.yaml)
