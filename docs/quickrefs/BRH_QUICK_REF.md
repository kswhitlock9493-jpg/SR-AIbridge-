# 🚀 Bridge Runtime Handler (BRH) - Quick Reference

## ⚡ Quick Setup

```bash
# 1. Generate FORGE_DOMINION_ROOT
./brh/examples/generate_forge_root.sh dev your-seal

# 2. Set environment variables (from output above)
export FORGE_DOMINION_ROOT="dominion://sovereign.bridge?env=dev&epoch=XXXXX&sig=XXXXX"
export DOMINION_SEAL="your-seal"

# 3. Install dependencies
pip install -r brh/requirements.txt

# 4. Run BRH runtime
python -m brh.run

# 5. (Optional) Run API server in another terminal
uvicorn brh.api:app --host 0.0.0.0 --port 7878
```

## 📝 Key Files

| File | Purpose |
|------|---------|
| `bridge.runtime.yaml` | Service definitions and health checks |
| `brh/forge_auth.py` | HMAC-SHA256 authentication |
| `brh/run.py` | Container orchestration engine |
| `brh/api.py` | Remote control API (FastAPI) |
| `brh/examples/generate_forge_root.sh` | Helper to generate Forge root |
| `brh/examples/test_forge_auth.py` | Test authentication flow |

## 🔑 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FORGE_DOMINION_ROOT` | ✅ Yes | - | Full dominion URL with HMAC signature |
| `DOMINION_SEAL` | ✅ Yes* | - | HMAC secret key (*except with allow_unsigned) |
| `BRH_ALLOW_UNSIGNED` | No | `false` | Allow unsigned mode (dev only) |
| `BRH_ALLOWED_ORIGINS` | No | `*` | CORS origins for API (comma-separated) |

## 📋 Runtime Manifest (bridge.runtime.yaml)

```yaml
version: "1.0"
dominion:
  root_env_var: FORGE_DOMINION_ROOT
  service_ttl_minutes: 180
  allow_unsigned: false

provider:
  kind: docker
  network: brh_net
  autostart: true

services:
  api:
    context: ./bridge_backend
    dockerfile: Dockerfile
    image: ghcr.io/org/app:latest
    replicas: 1
    ports: ["8000:8000"]
    env: ["ENVIRONMENT=production"]
    health:
      http: "http://localhost:8000/health/live"
      interval: 10s
      timeout: 2s
      retries: 12
    volumes: []
```

## 🎯 Common Commands

```bash
# Generate Forge root with custom seal
./brh/examples/generate_forge_root.sh prod my-secret-seal

# Test authentication flow
python brh/examples/test_forge_auth.py

# Run BRH runtime (starts containers)
python -m brh.run

# Run API server for remote control
uvicorn brh.api:app --host 0.0.0.0 --port 7878

# Check API status
curl http://localhost:7878/status | jq

# Trigger deployment
curl -X POST http://localhost:7878/deploy \
  -H "Content-Type: application/json" \
  -d '{"image": "ghcr.io/org/app:latest", "branch": "main"}'

# Restart a container
curl -X POST http://localhost:7878/restart/brh_api

# Drain (stop and remove) a container
curl -X POST http://localhost:7878/drain/brh_api
```

## 🔒 Security Features

1. **HMAC-SHA256 Signature** - All operations verify HMAC signature
2. **Time Skew Protection** - Rejects requests ±15 minutes from epoch
3. **Ephemeral Tokens** - Deterministic, time-limited service tokens
4. **Image Name Validation** - Prevents command injection attacks
5. **CORS Configuration** - Restrict origins in production

## 🏃 Deployment Flow

```
Push to main
    ↓
GitHub Actions builds image
    ↓
Publishes to GHCR
    ↓
Netlify build completes
    ↓
Calls bridge-deploy function
    ↓
BRH node pulls new image
    ↓
Restarts containers
    ↓
Health checks pass
    ↓
Service online
```

## 🔍 Troubleshooting

### "FORGE_DOMINION_ROOT missing"
```bash
# Check if set
echo $FORGE_DOMINION_ROOT

# Generate new one
./brh/examples/generate_forge_root.sh dev test-seal
```

### "Forge signature invalid"
- Verify `DOMINION_SEAL` matches signature generation
- Check system time (must be within ±15 minutes)
- Regenerate with current timestamp

### "Forge epoch skew too large"
- System clock > 15 minutes off
- Sync time: `sudo ntpdate -s time.nist.gov`
- Regenerate FORGE_DOMINION_ROOT

### "Health check failed"
```bash
# Check container logs
docker logs brh_api

# Increase retries in bridge.runtime.yaml
# Verify health endpoint URL is correct
```

### Docker build errors
```bash
# Ensure context is repository root
docker build -f bridge_backend/Dockerfile .

# Check Dockerfile exists
ls bridge_backend/Dockerfile
```

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/deploy` | Pull image and restart (validates image name) |
| GET | `/status` | Get container status and metadata |
| POST | `/restart/{name}` | Restart specific container |
| POST | `/drain/{name}` | Stop and remove container |

## 🚀 Production Deployment

### Systemd Service

```bash
# Copy service file
sudo cp infra/systemd/brh@.service /etc/systemd/system/

# Create environment file
sudo mkdir -p /etc/brh
echo "DOMINION_SEAL=your-production-seal" | sudo tee /etc/brh/dominion.env
sudo chmod 600 /etc/brh/dominion.env

# Generate production Forge root
./brh/examples/generate_forge_root.sh prod $(cat /etc/brh/dominion.env | cut -d'=' -f2)

# Enable and start (use generated FORGE_DOMINION_ROOT)
sudo systemctl enable brh@"dominion://sovereign.bridge?env=prod&epoch=XXX&sig=XXX"
sudo systemctl start brh@"dominion://..."

# Check status
sudo systemctl status brh@"dominion://..."
```

### GitHub Actions

- Workflow: `.github/workflows/bridge-runtime-local.yml`
- Triggers: Push to `main`, changes to `bridge_backend/**`
- Output: Image published to GHCR at `ghcr.io/org/sr-aibridge-backend:latest`

## 🎨 Frontend Integration

```jsx
import BridgeRuntimePanel from "@/components/BridgeRuntimePanel";

// With default localhost:7878
<BridgeRuntimePanel />

// With custom URL
<BridgeRuntimePanel apiUrl="https://brh.yourdomain.com" />

// Configure default via env
// .env: VITE_BRH_API_URL=https://brh.yourdomain.com
```

## 🔗 Integration Points

| System | Integration | Status |
|--------|-------------|--------|
| FORGE_DOMINION_ROOT | HMAC authentication | ✅ Active |
| GitHub Actions | Image builds | ✅ Active |
| Netlify Functions | Deploy webhooks | ✅ Active |
| Docker | Container runtime | ✅ Active |
| FastAPI | Control API | ✅ Active |
| React Dashboard | UI control | ✅ Active |

## 📚 Related Documentation

- [Full Deployment Guide](BRH_DEPLOYMENT_GUIDE.md)
- [Implementation Summary](BRH_IMPLEMENTATION_SUMMARY.md)
- [Forge Dominion Guide](FORGE_DOMINION_DEPLOYMENT_GUIDE.md)
- [Example Scripts](brh/examples/README.md)

## ⚙️ Next Steps

- [ ] Set up production BRH node with systemd
- [ ] Configure GitHub Actions secrets (GITHUB_TOKEN automatic)
- [ ] Add `FORGE_DOMINION_ROOT` to Netlify environment
- [ ] Test deployment flow end-to-end
- [ ] Add BridgeRuntimePanel to Command Deck
- [ ] Remove Render dependency

---

**Version**: 1.0.0-Phase1  
**Last Updated**: 2025-11-03  
**Status**: Ready for deployment
