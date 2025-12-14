# BRH Consensus & Leader Election - Quick Reference

## 🚀 Quick Start

### Single Node Setup
```bash
export BRH_NODE_ID=brh-primary
export BRH_ENV=production
export FORGE_DOMINION_ROOT=dominion://sovereign.bridge
export DOMINION_SEAL=your-secret-seal

python3 -m brh.run
```

### Multi-Node Setup
**Node 1:**
```bash
export BRH_NODE_ID=brh-node-01
export BRH_ENV=production
python3 -m brh.run
```

**Node 2:**
```bash
export BRH_NODE_ID=brh-node-02
export BRH_ENV=production
python3 -m brh.run
```

## 📋 New Modules

| Module | Purpose |
|--------|---------|
| `brh/consensus.py` | Peer discovery, leader election, consensus broadcast |
| `brh/role.py` | Track leader/witness role state |
| `brh/handover.py` | Container ownership transfer during transitions |

## 🎯 Key Features

### Leader Election
- **Algorithm**: Highest epoch wins (most recent node)
- **Interval**: Every 180 seconds (configurable via `BRH_CONSENSUS_INTERVAL`)
- **Stale Filter**: Nodes not seen for >300s are ignored

### Container Ownership
```yaml
labels:
  brh.owner: brh-node-01  # Current owner node
  brh.env: production      # Environment filter
  brh.service: api         # Service name
```

### Zero-Downtime Handover
1. **Old Leader**: Removes `brh.owner` label
2. **New Leader**: Adds `brh.owner` label
3. **Result**: Container keeps running, ownership transfers

## 🔌 Forge Endpoints

### POST /federation/consensus
Receives election reports from BRH nodes.

**Request:**
```json
{
  "epoch": 1234567890,
  "forge_root": "dominion://sovereign.bridge",
  "leader": "brh-node-02",
  "peers": ["brh-node-01", "brh-node-02"],
  "sig": "ab26e599..."
}
```

**Response:**
```json
{
  "ok": true,
  "leader": "brh-node-02",
  "peers_count": 2
}
```

### GET /federation/leader
Returns current leader information.

**Response:**
```json
{
  "leader": "brh-node-02",
  "lease": null,
  "epoch": 1234567890
}
```

## 🛡️ API Gating

### Deploy Endpoint
```bash
# Leader node - accepts deploy
curl -X POST http://leader:8000/deploy \
  -H "Content-Type: application/json" \
  -d '{"image": "myapp:latest", "branch": "main"}'

# Response: {"status": "restarted", "image": "myapp:latest"}

# Witness node - rejects deploy
curl -X POST http://witness:8000/deploy \
  -H "Content-Type: application/json" \
  -d '{"image": "myapp:latest", "branch": "main"}'

# Response: {"status": "ignored", "reason": "not-leader"}
```

## 🔧 Testing

### Run Unit Tests
```bash
cd /home/runner/work/SR-AIbridge-/SR-AIbridge-
PYTHONPATH=. python3 brh/test_consensus_role.py
```

### Run Integration Tests
```bash
PYTHONPATH=. python3 brh/test_integration.py
```

## 📊 Logging

### Heartbeat Logs
```
[HB] brh-node-01 pulse → 200
```

### Consensus Logs
```
[CN] Elected leader=brh-node-02 | peers=2 | → 200
```

### Role Transition Logs
```
[CN] PROMOTE → I am leader (brh-node-01)
[PROMOTE] Adopted brh_api
[PROMOTE] Adopted brh_ws

[CN] DEMOTE → I am witness (leader=brh-node-02)
[DEMOTE] Released brh_api
[DEMOTE] Released brh_ws
```

## ⚙️ Configuration Files

### bridge.runtime.yaml
```yaml
runtime:
  federation:
    consensus:
      enabled: true
      interval: 180
      election_method: highest_epoch
      ledger_forward: true
```

### Environment Variables
```bash
BRH_NODE_ID=brh-node-01              # Unique node identifier
BRH_ENV=production                    # Environment name
BRH_CONSENSUS_ENABLED=true            # Enable consensus (default: true)
BRH_CONSENSUS_INTERVAL=180            # Consensus interval in seconds
FORGE_DOMINION_ROOT=dominion://...   # Forge endpoint
DOMINION_SEAL=secret-seal             # HMAC signing key
```

## 🔍 Troubleshooting

### Check Current Leader
```bash
curl http://your-forge.netlify.app/.netlify/functions/forge-resolver/federation/leader
```

### Check Node Role
```python
from brh import role
print(f"Am I leader? {role.am_leader()}")
print(f"Current leader: {role.leader_id()}")
```

### Verify Consensus Working
```bash
# Watch logs for consensus broadcasts
tail -f logs/*.log | grep "\[CN\]"
```

### Container Ownership Check
```bash
# List containers with ownership labels
docker ps -a --format '{{.Names}}\t{{.Label "brh.owner"}}'
```

## 📚 Full Documentation
See [BRH_CONSENSUS_GUIDE.md](./BRH_CONSENSUS_GUIDE.md) for complete details.
