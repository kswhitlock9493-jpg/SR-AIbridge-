# 🜂 Forge Dominion v1.9.7s - Quick Reference

**Environment Sovereignty at a Glance**

---

## ⚡ Quick Start

### 1. Generate Root Key
```bash
export FORGE_DOMINION_ROOT=$(python - <<'PY'
import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip('='))
PY
)
```

### 2. Bootstrap
```bash
python -m bridge_backend.bridge_core.token_forge_dominion.bootstrap
```

### 3. Pre-Deploy
```bash
bash runtime/pre-deploy.dominion.sh
```

### 4. Scan Secrets
```bash
python -m bridge_backend.bridge_core.token_forge_dominion.scan_envs
```

---

## 🔑 Key Commands

| Command | Purpose |
|---------|---------|
| `bootstrap.py` | Validate/generate root key |
| `scan_envs.py` | Detect plaintext secrets |
| `pre-deploy.dominion.sh` | Mint provider tokens |
| `validate_or_renew.py <provider>` | Check/renew single token |

---

## 📊 Module Overview

```
token_forge_dominion/
├── quantum_authority.py         # Token minting (HMAC-SHA384)
├── sovereign_integration.py     # Bridge resonance integration
├── zero_trust_validator.py      # Policy enforcement
├── quantum_scanner.py           # Security scanning
├── enterprise_orchestrator.py   # Deployment automation + pulse
├── bootstrap.py                 # Root key validation
├── scan_envs.py                 # Secret detection
└── validate_or_renew.py         # Token lifecycle
```

---

## 🎯 Token Lifecycle

```
┌─────────────┐
│  Bootstrap  │ ──> Validate FORGE_DOMINION_ROOT
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Pre-Deploy │ ──> Mint tokens (TTL: resonance-aware)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Validate   │ ──> Auto-renew if expiring (<5min)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Expire     │ ──> Token invalid after TTL
└─────────────┘
```

---

## 🛡 Governance Pulse

| Metric | Threshold | Action |
|--------|-----------|--------|
| Mints/5min | >5 | 🔴 Governance lock |
| Renews/5min | >10 | 🔴 Governance lock |
| Inactive | >20min | 🟡 Manual review |
| Normal | - | 🟢 Healthy |

Check pulse:
```python
from bridge_backend.bridge_core.token_forge_dominion import EnterpriseOrchestrator
orchestrator = EnterpriseOrchestrator()
pulse = orchestrator.check_pulse()
print(pulse['pulse_strength'])  # gold/silver/red
```

---

## 🧪 Testing

Run all Forge Dominion tests:
```bash
pytest tests/test_forge_dominion_v197s.py -v
pytest tests/test_quantum_dominion.py -v
```

Run integration test:
```bash
export FORGE_DOMINION_ROOT="<your-key>"
bash runtime/pre-deploy.dominion.sh
```

---

## 🌐 Provider Configuration

### GitHub
```bash
python -m bridge_backend.bridge_core.token_forge_dominion.validate_or_renew github
```

### Netlify
```bash
python -m bridge_backend.bridge_core.token_forge_dominion.validate_or_renew netlify
```

### Render
```bash
python -m bridge_backend.bridge_core.token_forge_dominion.validate_or_renew render
```

---

## 📈 Visual Pulse Banner

Update banner:
```bash
node bridge_core/update_forge_banner_from_events.js
```

Watch mode (live updates):
```bash
node bridge_core/update_forge_banner_from_events.js --watch &
```

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FORGE_DOMINION_ROOT` | ✅ | - | Root key (32-byte base64) |
| `FORGE_DOMINION_MODE` | ❌ | `sovereign` | Operation mode |
| `FORGE_DOMINION_VERSION` | ❌ | `1.9.7s` | Version marker |
| `FORGE_ENVIRONMENT` | ❌ | `production` | Deployment environment |

---

## 🔍 Troubleshooting

### No FORGE_DOMINION_ROOT
```bash
# Generate and export
export FORGE_DOMINION_ROOT=$(python - <<'PY'
import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip('='))
PY
)
```

### Token validation fails
```bash
# Force renewal
python -m bridge_backend.bridge_core.token_forge_dominion.validate_or_renew <provider>
```

### Secrets detected
1. Remove plaintext from .env files
2. Add to .env.example as placeholders
3. Use Dominion tokens instead

---

## 📚 Full Documentation

See [FORGE_DOMINION_DEPLOYMENT_GUIDE.md](./FORGE_DOMINION_DEPLOYMENT_GUIDE.md) for complete deployment instructions.

---

**🜂 Status: SOVEREIGN • Resonance: 100.000 • Volatility: 0.032**
