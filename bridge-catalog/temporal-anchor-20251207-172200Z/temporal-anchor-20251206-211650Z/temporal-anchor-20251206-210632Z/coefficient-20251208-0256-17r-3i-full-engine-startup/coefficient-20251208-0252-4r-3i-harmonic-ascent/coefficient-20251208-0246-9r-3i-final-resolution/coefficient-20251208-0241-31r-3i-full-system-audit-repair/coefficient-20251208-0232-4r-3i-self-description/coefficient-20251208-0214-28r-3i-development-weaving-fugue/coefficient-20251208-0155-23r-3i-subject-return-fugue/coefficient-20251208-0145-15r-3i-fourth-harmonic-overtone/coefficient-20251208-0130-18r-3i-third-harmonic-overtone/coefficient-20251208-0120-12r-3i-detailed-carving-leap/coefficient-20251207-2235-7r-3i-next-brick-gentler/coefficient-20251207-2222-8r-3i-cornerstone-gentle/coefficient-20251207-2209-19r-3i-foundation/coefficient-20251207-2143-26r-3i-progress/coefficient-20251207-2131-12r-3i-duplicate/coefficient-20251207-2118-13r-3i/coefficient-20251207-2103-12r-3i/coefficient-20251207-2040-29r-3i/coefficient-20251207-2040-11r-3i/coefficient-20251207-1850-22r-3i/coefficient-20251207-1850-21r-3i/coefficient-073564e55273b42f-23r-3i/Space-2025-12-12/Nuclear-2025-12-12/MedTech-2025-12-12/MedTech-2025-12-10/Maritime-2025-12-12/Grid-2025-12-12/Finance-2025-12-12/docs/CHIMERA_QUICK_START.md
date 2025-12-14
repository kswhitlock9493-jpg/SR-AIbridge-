# Chimera Deployment Quick Start

## Quick Integration Guide for v1.9.7c

---

## Prerequisites

- Python 3.11+
- Access to Bridge repository
- Admiral-level permissions (for production deployments)

---

## Local Testing

### 1. Simulate Deployment

```bash
# Test Netlify deployment
python3 -m bridge_backend.cli.chimeractl simulate --platform netlify

# Test Render deployment
python3 -m bridge_backend.cli.chimeractl simulate --platform render
```

### 2. Monitor Status

```bash
python3 -m bridge_backend.cli.chimeractl monitor
```

### 3. Verify Configuration

```bash
python3 -m bridge_backend.cli.chimeractl verify --platform netlify
```

---

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/chimera_deploy.yml`:

```yaml
name: Chimera Autonomous Deployment

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Dependencies
        run: pip install -r requirements.txt
      
      - name: Chimera Simulation
        run: |
          python3 -m bridge_backend.cli.chimeractl simulate \
            --platform netlify \
            --auto-heal
      
      - name: Chimera Deploy
        if: success()
        run: |
          python3 -m bridge_backend.cli.chimeractl deploy \
            --platform netlify \
            --certify
        env:
          CHIMERA_ENABLED: true
```

---

## Render Integration

Already configured in `render.yaml`:

```yaml
preDeployCommand: "python3 -m bridge_backend.cli.chimeractl simulate --platform render --auto-heal || true"
```

Environment variables set:
- `CHIMERA_ENABLED=true`
- `CHIMERA_SIM_TIMEOUT=300`
- `CHIMERA_HEAL_MAX_ATTEMPTS=3`

---

## Netlify Integration

### Build Settings

No changes needed to `netlify.toml` - Chimera validates configuration during build.

### Optional: Pre-build Validation

Add to your build script in `package.json`:

```json
{
  "scripts": {
    "prebuild": "python3 -m bridge_backend.cli.chimeractl simulate --platform netlify || true",
    "build": "vite build"
  }
}
```

---

## API Usage

### Start the Backend

```bash
uvicorn bridge_backend.main:app --host 0.0.0.0 --port 8000
```

### Test Endpoints

```bash
# Get status
curl http://localhost:8000/api/chimera/status

# Simulate deployment
curl -X POST http://localhost:8000/api/chimera/simulate \
  -H "Content-Type: application/json" \
  -d '{"platform": "netlify"}'

# Deploy with certification
curl -X POST http://localhost:8000/api/chimera/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "netlify",
    "auto_heal": true,
    "certify": true
  }'
```

---

## Configuration

### Environment Variables

```bash
# Enable/disable Chimera
export CHIMERA_ENABLED=true

# Simulation timeout (seconds)
export CHIMERA_SIM_TIMEOUT=300

# Max healing attempts
export CHIMERA_HEAL_MAX_ATTEMPTS=3

# Genesis mode (required for event publishing)
export GENESIS_MODE=enabled
```

---

## Monitoring

### Real-time Status

```bash
# Watch deployment status
watch -n 5 'python3 -m bridge_backend.cli.chimeractl monitor'
```

### Check Logs

```bash
# View simulation logs
tail -f /var/log/bridge/chimera.log

# View Genesis events
tail -f /var/log/bridge/genesis.log
```

---

## Troubleshooting

### Simulation Fails

**Problem:** Simulation times out or fails

**Solution:**
```bash
# Increase timeout
export CHIMERA_SIM_TIMEOUT=600

# Run with verbose output
python3 -m bridge_backend.cli.chimeractl simulate --platform netlify --json
```

---

### Certification Fails

**Problem:** Build rejected by Truth Engine

**Solution:**
```bash
# Check certification details
python3 -m bridge_backend.cli.chimeractl verify --platform netlify --json

# Deploy without certification (emergency only)
python3 -m bridge_backend.cli.chimeractl deploy --platform netlify --no-certify
```

---

### Healing Loop

**Problem:** Healing keeps retrying same issues

**Solution:**
```bash
# Deploy without healing
python3 -m bridge_backend.cli.chimeractl deploy --platform netlify --no-heal
```

---

## Security Notes

- ✅ Chimera requires `admiral` role for production deployments
- ✅ All deployments logged in Genesis Ledger (immutable audit trail)
- ✅ Certification uses SHA3-256 cryptographic signatures
- ✅ Rollback protection via Cascade Engine (1.2s guarantee)

---

## Next Steps

1. ✅ Test simulation locally
2. ✅ Verify configuration
3. ✅ Run first deployment with certification
4. ✅ Monitor post-deployment health
5. ✅ Review Genesis Ledger for audit trail

---

## Support

- 📖 Full Documentation: [CHIMERA_README.md](../CHIMERA_README.md)
- 🏗️ Architecture: [docs/CHIMERA_ARCHITECTURE.md](./CHIMERA_ARCHITECTURE.md)
- 🔍 API Reference: [docs/CHIMERA_API_REFERENCE.md](./CHIMERA_API_REFERENCE.md)
- 🛡️ Failsafe Protocol: [docs/CHIMERA_FAILSAFE_PROTOCOL.md](./CHIMERA_FAILSAFE_PROTOCOL.md)

---

## Version

**v1.9.7c** — Project Chimera: Autonomous Deployment Sovereignty
