# v1.9.7f Cascade Synchrony - Quick Reference

## 🚀 Quick Start

Enable the full Cascade Synchrony protocol by adding these environment variables:

```bash
# Forge Core
FORGE_MODE=enabled
FORGE_SELF_HEAL=true

# Cascade Synchrony Protocol
CASCADE_SYNC=true
ARIE_PROPAGATION=true
UMBRA_MEMORY_SYNC=true
```

## 📡 API Endpoints

When `FORGE_MODE=enabled`, access these endpoints:

### Status & Configuration
- `GET /api/forge/status` - Get Forge and Synchrony status
- `GET /api/forge/registry` - Get engine registry mappings  
- `GET /api/forge/topology` - Get topology visualization

### Actions
- `POST /api/forge/integrate` - Manually trigger engine integration
- `POST /api/forge/heal/{subsystem}` - Trigger healing for a subsystem
- `POST /api/forge/recover/{platform}` - Trigger platform recovery

## 🧬 Architecture

### Healing Flow
```
Cascade (detects error) → ARIE (generates fix) → Truth (certifies) 
    → Forge (commits) → Umbra (learns)
```

### Platform Support
- **Render**: Cascade restores engine state
- **Netlify**: Umbra replays successful deploys
- **GitHub**: ARIE applies Forge-level patches
- **Bridge**: Genesis orchestrates cross-platform healing

## 📁 Key Files

### Configuration
- `.github/bridge_forge.json` - Engine path registry
- `.github/forge_topology.json` - Topology visualization map

### Core Modules
- `bridge_backend/forge/forge_core.py` - Engine introspection & integration
- `bridge_backend/forge/synchrony.py` - Cross-system healing protocol
- `bridge_backend/forge/routes.py` - API endpoints

## 🧪 Testing

Run integration tests:
```bash
pytest tests/test_forge_cascade_synchrony.py -v
```

All 19 tests should pass ✅

## 🔒 Security

- **RBAC**: Admiral-exclusive Forge control
- **Truth Certification**: All operations certified
- **Immutable Writes**: Only Truth-certified changes allowed

## 🌐 Integration Matrix

| Platform | Engines | Purpose |
|----------|---------|---------|
| Render | Cascade, ARIE, Truth | Error detection & repair |
| Netlify | Umbrella, Chimera, Steward | Deploy memory & replay |
| GitHub | Forge, EnvScribe, EnvRecon, Truth | Repository integration |
| Bridge | Genesis, Federation, Autonomy | Orchestration core |

## 📊 Status Check

Check system status:
```bash
curl http://localhost:8000/api/forge/status
```

Expected response:
```json
{
  "forge": {
    "forge_mode": "enabled",
    "forge_self_heal": "true",
    "cascade_sync": "true",
    "arie_propagation": "true",
    "umbra_memory_sync": "true",
    "truth_certification": "true",
    "registry_exists": true
  },
  "synchrony": {
    "enabled": true,
    "arie_propagation": true,
    "umbra_memory_sync": true,
    "cascade_sync": "true",
    "protocol": "cascade_synchrony",
    "version": "v1.9.7f"
  },
  "version": "v1.9.7f",
  "protocol": "cascade_synchrony"
}
```

## 🎯 Usage Examples

### Trigger Healing
```bash
curl -X POST http://localhost:8000/api/forge/heal/cascade \
  -H "Content-Type: application/json" \
  -d '{"message": "Service timeout", "severity": "high"}'
```

### Trigger Recovery
```bash
curl -X POST http://localhost:8000/api/forge/recover/render \
  -H "Content-Type: application/json" \
  -d '{"message": "Deployment failed", "code": 503}'
```

### Manual Integration
```bash
curl -X POST http://localhost:8000/api/forge/integrate
```

## 📈 Version Info

- **Version**: v1.9.7f
- **Codename**: Cascade Synchrony
- **Protocol**: Universal Healing Protocol
- **Autonomy Level**: Full
- **Engines**: 31+ integrated

## 🧭 Admiral Directive

> "The Forge remembers, the Bridge learns, the Truth certifies.
> No engine sleeps, no system fails unseen." ⚙️✨

---

For complete documentation, see: `V197F_CASCADE_SYNCHRONY.md`
