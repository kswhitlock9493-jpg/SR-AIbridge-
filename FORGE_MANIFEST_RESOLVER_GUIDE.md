# Forge Dominion Manifest Resolver & Federation Heartbeat

## Overview

This implementation adds two major features to the SR-AIbridge infrastructure:

1. **Forge Dominion Manifest Resolver** - Dynamic credential provisioning system
2. **Federation Heartbeat Extension** - Real-time health monitoring and consensus

---

## Forge Dominion Manifest Resolver

### Purpose

Handles runtime handshake requests and dynamically returns ephemeral connection data to bridge agents (Netlify, GitHub Actions, etc.).

### Endpoint

```
GET /manifest/resolve?target={ledger|bridge|default}
```

### Supported Targets

- **ledger** - Returns sovereign ledger connection credentials
- **bridge** - Returns bridge deployment sync credentials  
- **default** - Returns basic forge status

### Response Format

```json
{
  "forge_root": "dominion://sovereign.bridge",
  "epoch": 1699056000,
  "target": "ledger",
  "ledger_url": "https://sovereign.bridge/api/log",
  "ledger_signature": "abc123...",
  "ledger_identity": "SR-AIBRIDGE::FORGE::EPOCH-1699056000"
}
```

### Environment Variables

- `FORGE_DOMINION_ROOT` - The forge dominion root URL
- `DOMINION_SEAL` - Secret key for HMAC signature generation

### Security

- All signatures are HMAC-SHA256 hashed using `DOMINION_SEAL`
- Signatures are ephemeral and expire based on epoch
- No static secrets are stored or transmitted

---

## Federation Heartbeat Extension

### Purpose

Establishes Bridge-to-Bridge health checks so nodes can detect failures and the Dominion can promote secondary nodes automatically.

### Endpoint

```
POST /federation/heartbeat
```

### Request Format

```json
{
  "epoch": 1699056000,
  "forge_root": "dominion://sovereign.bridge",
  "sig": "abc123...",
  "node": "brh-node-1",
  "status": "alive"
}
```

### Heartbeat Daemon

The BRH Heartbeat Daemon (`brh/heartbeat_daemon.py`) automatically:

- Broadcasts heartbeat pulses every 60 seconds (configurable)
- Generates cryptographically signed payloads
- Runs as a background daemon thread

### Environment Variables

- `BRH_HEARTBEAT_ENABLED` - Enable/disable heartbeat (default: `true`)
- `BRH_HEARTBEAT_INTERVAL` - Heartbeat interval in seconds (default: `60`)
- `BRH_NODE_ID` - Unique identifier for this node
- `FORGE_HEARTBEAT_LEDGER_FORWARD` - Forward heartbeats to ledger (default: `false`)

### Integration

The heartbeat daemon is automatically started when BRH boots up:

```python
from brh import heartbeat_daemon

# In brh/run.py main():
heartbeat_daemon.start()
```

---

## Configuration

All configuration is defined in `bridge.runtime.yaml`:

```yaml
# Forge configuration schema
forge:
  dominion: sovereign.bridge
  resolver: forge://resolve
  schema:
    - target: ledger
      purpose: runtime logging
      return:
        - ledger_url
        - ledger_signature
        - ledger_identity
    - target: bridge
      purpose: deployment bridge sync
      return:
        - bridge_url
        - bridge_signature
        - bridge_identity

# Federation heartbeat configuration
runtime:
  federation:
    heartbeat:
      enabled: true
      interval: 60
      endpoint: forge://federation/heartbeat
      ledger_forward: true
      ttl: 300
```

---

## Testing

Run the test suite:

```bash
pytest tests/test_forge_manifest_resolver.py -v
```

Tests cover:
- Signature generation and validation
- Manifest target resolution
- Heartbeat payload structure
- Daemon lifecycle management
- Configuration validation

---

## Architecture

### Flow: Manifest Resolution

1. **Runtime Call** → Bridge module calls `GET ${FORGE_DOMINION_ROOT}/manifest/resolve?target=ledger`
2. **Forge Resolver** → Generates time-based HMAC signature
3. **Response** → Returns ephemeral tokens, URLs, and IDs (valid for minutes)
4. **Consumer Action** → Bridge Runtime uses ephemeral values for API calls

### Flow: Federation Heartbeat

1. **BRH Node** → Emits signed pulse every 60 seconds
2. **Forge Resolver** → Verifies signature + epoch (±5 min tolerance)
3. **Ledger (optional)** → Records pulse for uptime analytics
4. **Consensus (future)** → Promotes highest-uptime node if primary drops

---

## Benefits

✅ **Self-Serving Credentials** - Forge provisions credentials on-demand  
✅ **Dynamic Rotation** - All credentials rotate automatically  
✅ **Bridge-Native** - No dependency on external services like Render  
✅ **Real-Time Health** - Live federation health monitoring  
✅ **Cryptographic Trust** - All communication is signed and verified  
✅ **Audit Trail** - Sovereign Ledger records all activity  

---

## Next Steps

Future enhancements could include:

- Automatic failover and node promotion
- Multi-region federation support
- Advanced consensus algorithms
- Real-time dashboard for federation health
- Automated security incident response
