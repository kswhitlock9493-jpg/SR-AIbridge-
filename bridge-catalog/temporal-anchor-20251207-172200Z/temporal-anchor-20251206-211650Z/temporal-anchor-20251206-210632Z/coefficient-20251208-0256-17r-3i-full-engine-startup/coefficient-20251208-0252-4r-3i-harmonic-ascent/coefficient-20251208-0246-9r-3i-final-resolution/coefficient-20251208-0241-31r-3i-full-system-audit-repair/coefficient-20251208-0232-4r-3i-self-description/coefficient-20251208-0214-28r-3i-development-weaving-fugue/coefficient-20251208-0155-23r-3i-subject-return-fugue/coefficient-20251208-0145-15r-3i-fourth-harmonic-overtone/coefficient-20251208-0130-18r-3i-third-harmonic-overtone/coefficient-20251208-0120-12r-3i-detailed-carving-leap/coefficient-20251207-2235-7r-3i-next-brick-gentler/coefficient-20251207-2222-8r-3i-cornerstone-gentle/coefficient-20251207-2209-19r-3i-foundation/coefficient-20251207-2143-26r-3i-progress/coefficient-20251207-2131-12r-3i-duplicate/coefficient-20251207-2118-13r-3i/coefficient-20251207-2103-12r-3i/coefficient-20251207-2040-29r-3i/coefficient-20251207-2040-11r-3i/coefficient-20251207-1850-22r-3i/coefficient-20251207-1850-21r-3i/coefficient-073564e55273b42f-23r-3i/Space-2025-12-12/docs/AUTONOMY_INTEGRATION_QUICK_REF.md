# Autonomy Integration Quick Reference

## 🎯 What Was Done

The Autonomy Engine is now linked to **every** triage, federation, and parity feature in the SR-AIbridge system.

## 🔗 Integration Points

### Triage → Autonomy
- **API Triage** publishes to `triage.api`
- **Endpoint Triage** publishes to `triage.endpoint`
- **Diagnostics Federation** publishes to `triage.diagnostics`
- Autonomy responds with auto-healing via `genesis.heal`

### Federation → Autonomy
- **Federation Client** publishes to `federation.events` and `federation.heartbeat`
- Autonomy coordinates distributed operations via `genesis.intent`

### Parity → Autonomy
- **Parity Engine** publishes to `parity.check`
- **Parity Autofix** publishes to `parity.autofix`
- **Deploy Parity** publishes to `parity.check`
- Autonomy fixes issues via `genesis.heal`

## 🚀 Quick Start

### Enable Integration
```bash
export GENESIS_MODE=enabled
export GENESIS_STRICT_POLICY=true
```

### Test Triage Integration
```bash
cd bridge_backend/tools/triage
python3 api_triage.py          # Triggers autonomy via triage.api
python3 endpoint_triage.py     # Triggers autonomy via triage.endpoint
python3 diagnostics_federate.py # Triggers autonomy via triage.diagnostics
```

### Test Parity Integration
```bash
python3 bridge_backend/tools/parity_engine.py   # Triggers autonomy via parity.check
python3 bridge_backend/tools/parity_autofix.py  # Triggers autonomy via parity.autofix
```

### Test Federation Integration
```python
from bridge_backend.bridge_core.heritage.federation.federation_client import FederationClient

client = FederationClient()
await client.send_heartbeat()  # Triggers autonomy via federation.heartbeat
```

## 📊 Event Flow

```
Triage/Federation/Parity → Genesis Bus → Autonomy Engine → Auto-Actions
```

## 🔍 Verify Integration

```bash
python3 bridge_backend/tests/test_autonomy_integration.py
```

## 📚 Full Documentation

- [Autonomy Integration Guide](AUTONOMY_INTEGRATION.md)
- [System Diagram](AUTONOMY_INTEGRATION_DIAGRAM.md)

## ✅ Files Modified

**Core:**
- `bridge_backend/bridge_core/engines/adapters/genesis_link.py` - Autonomy subscriptions
- `bridge_backend/genesis/bus.py` - New event topics

**Triage:**
- `bridge_backend/tools/triage/api_triage.py`
- `bridge_backend/tools/triage/endpoint_triage.py`
- `bridge_backend/tools/triage/diagnostics_federate.py`

**Federation:**
- `bridge_backend/bridge_core/heritage/federation/federation_client.py`

**Parity:**
- `bridge_backend/tools/parity_engine.py`
- `bridge_backend/tools/parity_autofix.py`
- `bridge_backend/runtime/deploy_parity.py`

## 🧪 Tests Added

- `bridge_backend/tests/test_autonomy_integration.py`

## 📖 Docs Added

- `docs/AUTONOMY_INTEGRATION.md`
- `docs/AUTONOMY_INTEGRATION_DIAGRAM.md`
- `docs/AUTONOMY_INTEGRATION_QUICK_REF.md` (this file)

---

**Created:** 2025-10-11  
**Version:** 1.0.0  
**Status:** ✅ Complete
