# BRH Consensus System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Forge (Netlify)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           forge-resolver.js (Serverless)                 │  │
│  │                                                           │  │
│  │  POST /federation/heartbeat  ← Heartbeat pulses          │  │
│  │  POST /federation/consensus  ← Election reports          │  │
│  │  GET  /federation/leader     ← Leader queries            │  │
│  │  GET  /manifest/resolve      ← Manifest requests         │  │
│  │                                                           │  │
│  │  State: currentLeader, consensusHistory[]                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▲  ▼
                    ┌─────────┼──┼─────────┐
                    │         │  │         │
        ┌───────────▼─────────┴──┴─────────▼───────────┐
        │                                               │
┌───────▼──────┐                            ┌──────────▼──────┐
│  BRH Node 1  │                            │   BRH Node 2    │
│  (Leader)    │                            │   (Witness)     │
├──────────────┤                            ├─────────────────┤
│ heartbeat.py │ → 60s pulse               │  heartbeat.py   │
│ consensus.py │ → 180s election            │  consensus.py   │
│ role.py      │    am_leader=True          │  role.py        │
│ handover.py  │                            │  handover.py    │
│ api.py       │ ✓ Accepts /deploy          │  api.py         │
│ run.py       │ ✓ Orchestrates             │  run.py         │
├──────────────┤                            ├─────────────────┤
│ Docker       │                            │  Docker         │
│ ┌──────────┐ │                            │  ┌────────────┐ │
│ │ api      │ │ brh.owner=node-1           │  │ (no owned) │ │
│ │ ws       │ │ brh.env=production         │  └────────────┘ │
│ └──────────┘ │                            │                 │
└──────────────┘                            └─────────────────┘
```

## Component Interactions

### 1. Heartbeat Flow (Every 60s)

```
BRH Node
  ├─ heartbeat_daemon.py
  │   ├─ Generate: epoch, sig, node_id, status
  │   └─ POST → /federation/heartbeat
  │
Forge
  └─ forge-resolver.js
      ├─ Validate signature
      ├─ Check age < 300s
      └─ Optional: Forward to Sovereign Ledger
```

### 2. Consensus Election Flow (Every 180s)

```
BRH Node (consensus.py)
  ├─ Collect active peers (last_seen < 300s)
  ├─ Elect leader (highest epoch)
  ├─ Generate signature
  └─ POST → /federation/consensus
      │
      ├─ payload: {epoch, leader, peers[], sig}
      │
Forge (forge-resolver.js)
  ├─ Update currentLeader
  ├─ Store in consensusHistory[]
  └─ Optional: Forward to Sovereign Ledger
```

### 3. Leader Polling Flow (Every 10s)

```
BRH Node (consensus.py)
  └─ GET → /federation/leader
      │
      ├─ Response: {leader: "node-1", lease: null}
      │
      └─ apply_leader_change()
          │
          ├─ Update role.set_leader()
          │
          ├─ IF promoted (witness → leader):
          │   ├─ Print: [CN] PROMOTE
          │   └─ handover.adopt_containers()
          │       └─ Add brh.owner label to orphaned containers
          │
          └─ IF demoted (leader → witness):
              ├─ Print: [CN] DEMOTE
              └─ handover.relinquish_ownership()
                  └─ Remove brh.owner label from containers
```

### 4. Deploy Hook Flow

```
External System
  └─ POST → /deploy {image: "myapp:latest"}
      │
BRH API (api.py)
  ├─ Check: role.am_leader()?
  │
  ├─ IF leader:
  │   ├─ Validate image name
  │   ├─ docker pull
  │   ├─ restart containers
  │   └─ Return: {status: "restarted"}
  │
  └─ IF witness:
      └─ Return: {status: "ignored", reason: "not-leader"}
```

## State Transitions

### Node Role States

```
┌─────────────┐
│  STARTING   │
└──────┬──────┘
       │
       ▼
┌─────────────┐     Consensus elects me     ┌─────────────┐
│   WITNESS   │ ────────────────────────────▶│   LEADER    │
│             │                               │             │
│ - Reject    │  Another node elected leader │ - Accept    │
│   deploys   │ ◀────────────────────────────│   deploys   │
│ - No        │                               │ - Orchestr- │
│   container │                               │   ate       │
│   owner     │                               │ - Own       │
└─────────────┘                               │   containers│
                                              └─────────────┘
```

### Container Ownership Transfer

```
BEFORE:
Node 1 (Leader)                   Node 2 (Witness)
├─ api [brh.owner=node-1]        (no containers)
└─ ws  [brh.owner=node-1]

DURING HANDOVER:
Node 1 dies or demotes
    └─ relinquish_ownership()
        └─ Remove brh.owner label

Node 2 promoted
    └─ adopt_containers()
        └─ Add brh.owner=node-2 label

AFTER:
Node 1 (Offline/Witness)         Node 2 (Leader)
(no containers)                  ├─ api [brh.owner=node-2]
                                 └─ ws  [brh.owner=node-2]
```

## Data Structures

### role.py State

```python
_state = {
    "leader_id": "node-1",         # Current leader
    "i_am_leader": True,           # Am I the leader?
    "lease_token": None,           # Optional lease
    "lock": RLock()                # Thread safety
}
```

### consensus.py Peers

```python
peers = {
    "node-1": {
        "epoch": 1730682217,
        "sig": "ab26e599...",
        "status": "alive",
        "last_seen": 1730682217.5
    },
    "node-2": {
        "epoch": 1730682218,
        "sig": "cd38f7aa...",
        "status": "alive",
        "last_seen": 1730682218.2
    }
}
```

### Container Labels

```yaml
labels:
  brh.service: api              # Service identifier
  brh.env: production           # Environment name
  brh.epoch: "1730682217"       # Creation epoch
  brh.owner: node-1             # Current owner (for handover)
```

## Failure Scenarios

### Scenario 1: Leader Node Fails

```
t=0:   Node 1 (Leader), Node 2 (Witness)
t=60:  Node 1 dies ☠️
t=120: Node 2 still witness (waiting for consensus cycle)
t=180: Consensus runs:
         - Node 1 not seen for 120s
         - Node 2 elected leader
         - Forge updates currentLeader=node-2
t=190: Node 2 polls /federation/leader
         - Detects promotion
         - Adopts containers (adds brh.owner=node-2)
t=191: Node 2 now accepts /deploy hooks
```

### Scenario 2: Network Partition

```
t=0:   Node 1 (Leader), Node 2 (Witness) - both healthy
t=60:  Network partition: Nodes can't reach Forge
t=120: Both continue heartbeats (fail silently)
t=180: Consensus broadcast fails
t=190: Leader poll fails
       - Nodes retain current roles
       - Node 1 remains leader
       - Node 2 remains witness
t=300: Network restored
t=310: Next consensus cycle succeeds
       - Leadership confirmed or reassigned
```

### Scenario 3: Split Brain Prevention

```
Both nodes think they're leader:
  ├─ Node 1: am_leader=True
  └─ Node 2: am_leader=True

Prevention Mechanism:
  └─ Forge maintains single source of truth
      ├─ Only one currentLeader in state
      ├─ All nodes poll same endpoint
      └─ Last consensus report wins
```

## Security Model

### Signature Generation

```python
def forge_sig(node_id, epoch):
    seal = os.getenv("DOMINION_SEAL")     # Shared secret
    msg = f"{node_id}|{epoch}".encode()
    return hmac.new(
        seal.encode(),
        msg,
        hashlib.sha256
    ).hexdigest()[:32]
```

### Validation Flow

```
1. BRH generates sig using DOMINION_SEAL
2. Includes sig in request
3. Forge validates (optional, if seal shared)
4. Stale messages (>300s) rejected
```

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Heartbeat Interval | 60s | Configurable via BRH_HEARTBEAT_INTERVAL |
| Consensus Interval | 180s | Configurable via BRH_CONSENSUS_INTERVAL |
| Leader Poll Interval | 10s | Hardcoded in consensus.py |
| Stale Threshold | 300s | Nodes not seen for 5min excluded |
| Handover Time | ~10-20s | Time to detect and apply promotion |
| Downtime | ~0s | Zero-downtime handover by default |

## Extension Points

### 1. Custom Election Algorithm

```python
# consensus.py - modify elect_leader()
def elect_leader():
    # Current: highest epoch
    # Alternative: weighted priority
    leader = max(active, key=lambda x: (
        x[1].get("priority", 0),  # Custom priority
        -x[1]["epoch"],            # Then epoch
        x[0]                       # Then alphabetical
    ))
```

### 2. Lease Token System

```javascript
// forge-resolver.js
async function handleLeaderQuery(event) {
    const lease = crypto.randomBytes(16).toString('hex');
    leaseRegistry[currentLeader] = {
        token: lease,
        expires: Date.now() + 300000  // 5 min
    };
    return { leader: currentLeader, lease };
}
```

### 3. Drain-and-Stop Policy

```python
# consensus.py - modify apply_leader_change()
if prev_was_leader and not now_leader:
    # Option 1: Zero-downtime (default)
    handover.relinquish_ownership(ENV)
    
    # Option 2: Graceful drain
    handover.drain_and_stop(ENV, timeout=30)
```

## Monitoring & Observability

### Key Metrics

```python
# Prometheus-style metrics (future enhancement)
brh_consensus_leader_changes_total
brh_consensus_election_duration_seconds
brh_consensus_active_peers
brh_handover_containers_adopted_total
brh_handover_containers_released_total
brh_role_is_leader{node_id="node-1"} 1
```

### Health Checks

```bash
# Check if consensus is running
curl http://localhost:8000/status | jq '.forge_root'

# Verify leader identity
curl https://forge/federation/leader | jq '.leader'

# List container ownership
docker ps --format '{{.Names}}\t{{.Label "brh.owner"}}'
```

## Deployment Topology

### Development (Single Node)
```
┌─────────┐
│ Forge   │
└────┬────┘
     │
┌────▼────┐
│ BRH-1   │ (always leader)
└─────────┘
```

### Production (Multi-Node)
```
       ┌─────────┐
       │ Forge   │
       └────┬────┘
            │
    ┌───────┼───────┐
    │       │       │
┌───▼───┐ ┌─▼─────┐ ┌─▼─────┐
│ BRH-1 │ │ BRH-2 │ │ BRH-3 │
│Leader │ │Witness│ │Witness│
└───────┘ └───────┘ └───────┘
```

### High Availability (Geographic)
```
          ┌─────────┐
          │ Forge   │
          │(Global) │
          └────┬────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌───▼───┐  ┌───▼───┐
│US-East│  │US-West│  │ EU    │
│ BRH-1 │  │ BRH-2 │  │ BRH-3 │
└───────┘  └───────┘  └───────┘
```

---

**Legend:**
- `▲▼` = Network communication
- `├─` = Component hierarchy
- `→` = Data flow direction
- `☠️` = Component failure
- `✓` = Enabled feature
- `✗` = Disabled feature
