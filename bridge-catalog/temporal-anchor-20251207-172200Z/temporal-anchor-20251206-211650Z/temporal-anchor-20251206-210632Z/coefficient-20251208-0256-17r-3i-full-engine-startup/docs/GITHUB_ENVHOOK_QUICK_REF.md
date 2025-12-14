# GitHub Environment Hook - Quick Reference

**Component:** Autonomous Environment Lattice  
**Version:** v1.9.6x  
**File:** `.github/scripts/github_envhook.py`

---

## 🚀 Commands

```bash
# Watch for changes (continuous monitoring)
python3 .github/scripts/github_envhook.py --watch

# Manual trigger (one-time sync)
python3 .github/scripts/github_envhook.py --trigger

# Help
python3 .github/scripts/github_envhook.py --help
```

---

## 📡 Genesis Events Published

| Event | Topic | Purpose |
|-------|-------|---------|
| **EnvMirror Sync** | `envmirror.sync.start` | Triggers GitHub ↔ Render ↔ Netlify sync |
| **EnvDuo Audit** | `envduo.audit` | Triggers ARIE + EnvRecon integrity check |

---

## 📂 Files

| File | Purpose | Committed |
|------|---------|-----------|
| `.github/scripts/github_envhook.py` | Main watcher script | ✅ Yes |
| `logs/github_envhook_state.json` | State persistence | ❌ No (auto-gen) |
| `logs/github_envhook_triggers.log` | Audit trail | ❌ No (auto-gen) |

---

## 🔍 Monitoring

```bash
# View trigger logs
tail -f logs/github_envhook_triggers.log | jq .

# View current state
cat logs/github_envhook_state.json | jq .

# Check Genesis events
curl http://localhost:8000/api/genesis/events?topic=envmirror.sync.start
```

---

## 🧪 Testing

```bash
# Run tests
cd bridge_backend
python3 -m unittest tests.test_github_envhook -v

# Test manual trigger
python3 .github/scripts/github_envhook.py --trigger

# Simulate file change
jq '.version = "test"' .github/environment.json > /tmp/env.json
mv /tmp/env.json .github/environment.json
```

---

## 🔌 Integration

### Subscribe to Events (Python)

```python
from genesis.bus import genesis_bus

def on_sync(event):
    print(f"Sync triggered: {event['source']}")

genesis_bus.subscribe("envmirror.sync.start", on_sync)
genesis_bus.subscribe("envduo.audit", on_sync)
```

### GitHub Actions Workflow

See: `.github/workflows/env-sync-trigger.yml.example`

---

## 🎯 Use Cases

| Scenario | Command | Triggers |
|----------|---------|----------|
| Edit environment.json via PR | Auto (webhook) | Both events |
| Manual sync after deploy | `--trigger` | Both events |
| Development testing | `--watch` | On file change |
| CI/CD integration | GitHub Actions | On push to main |

---

## 🔒 Security

- ✅ `.github/environment.json` is Admiral-only writable
- ✅ All events Truth-certified via Genesis
- ✅ Audit logs immutable once written
- ✅ Genesis Guardians policy enforcement

---

## 📚 Documentation

- **Main Docs:** `docs/GITHUB_ENVHOOK.md`
- **Integration Guide:** `docs/GITHUB_ENVHOOK_INTEGRATION.md`
- **Genesis Events:** `docs/GENESIS_EVENT_FLOW.md`

---

## 🛠️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GENESIS_MODE` | `enabled` | Enable/disable Genesis bus |
| `GENESIS_STRICT_POLICY` | `true` | Enforce strict topic validation |
| `GENESIS_TRACE_LEVEL` | `2` | Logging verbosity (0-3) |

---

## 🎯 Result

✅ Zero-config autonomous environment sync  
✅ Instant cross-platform propagation  
✅ Continuous audit & self-healing  
✅ Complete Genesis visibility

> "When .github/environment.json changes, the Bridge awakens."

---

**Last Updated:** 2025-10-12  
**Status:** ✅ Production Ready
