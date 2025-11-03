# Bridge Runtime Handler (BRH) - Deployment Guide

The Bridge Runtime Handler (BRH) is a self-hosted, sovereign runtime manager that replaces Render with Docker-based container orchestration. It uses the FORGE_DOMINION_ROOT variable for authentication and enables true sovereign control over your backend infrastructure.

## Architecture Overview

- **Phase 1**: Local Docker orchestration with HMAC authentication
- **Phase 2**: SDTF integration for token minting (future)
- **Phase 3**: μ-harmonic lattice telemetry (future)

## Components

1. **bridge.runtime.yaml** - Runtime manifest defining services
2. **brh/forge_auth.py** - HMAC authentication and token minting
3. **brh/run.py** - Runtime launcher and container orchestration
4. **brh/api.py** - FastAPI server for remote control
5. **netlify/functions/bridge-deploy.js** - Deployment webhook
6. **BridgeRuntimePanel.jsx** - Frontend control dashboard

## Quick Start

### 1. Install Dependencies

```bash
pip install -r brh/requirements.txt
```

### 2. Set Environment Variables

```bash
# Generate a secure seal
export DOMINION_SEAL="your-secret-seal-here"

# Compute HMAC signature
export EPOCH=$(date +%s)
export SIG=$(echo -n "dominion://sovereign.bridge|dev|$EPOCH" | openssl dgst -sha256 -hmac "$DOMINION_SEAL" | cut -d' ' -f2)

# Set the Forge Dominion Root
export FORGE_DOMINION_ROOT="dominion://sovereign.bridge?env=dev&epoch=$EPOCH&sig=$SIG"
```

### 3. Run BRH

```bash
python -m brh.run
```

This will:
- Parse and verify the FORGE_DOMINION_ROOT
- Mint an ephemeral token
- Create Docker network (brh_net)
- Build/pull container images
- Start services with health checks
- Report when all services are healthy

### 4. Run BRH API Server (Optional)

For remote control capabilities:

```bash
# Install additional dependencies
pip install fastapi uvicorn docker

# Run the API server
uvicorn brh.api:app --host 0.0.0.0 --port 7878
```

## Configuration

### bridge.runtime.yaml

The runtime manifest defines:

- **dominion**: Authentication and token settings
- **provider**: Runtime provider (docker for Phase-1)
- **services**: Container definitions with:
  - `context`: Build directory (if building from source)
  - `image`: Container image name
  - `ports`: Port mappings
  - `env`: Environment variables
  - `health`: Health check configuration
  - `volumes`: Volume mounts

Example service:

```yaml
services:
  api:
    context: ./bridge_backend
    dockerfile: Dockerfile
    image: ghcr.io/your-org/sr-aibridge-backend:latest
    replicas: 1
    ports:
      - "8000:8000"
    env:
      - "ENVIRONMENT=production"
    health:
      http: "http://localhost:8000/health/live"
      interval: 10s
      timeout: 2s
      retries: 12
```

## Security

### HMAC Signature Verification

BRH uses HMAC-SHA256 to verify the FORGE_DOMINION_ROOT:

1. Message: `<root>|<env>|<epoch>`
2. Key: `DOMINION_SEAL`
3. Signature must match within ±15 minutes time skew

### Token Minting

Ephemeral tokens are deterministically generated for service authentication:
- Based on Forge context (root, env, epoch)
- Signed with DOMINION_SEAL
- Default TTL: 180 minutes

### Allow Unsigned Mode

For development only:

```bash
export BRH_ALLOW_UNSIGNED=true
```

⚠️ Never use in production!

## GitHub Actions Integration

The workflow `.github/workflows/bridge-runtime-local.yml` automatically:

1. Builds backend Docker image on push to main
2. Publishes to GitHub Container Registry (GHCR)
3. BRH nodes can pull and deploy updates

### Setup GHCR

1. Enable GHCR in your repository settings
2. Workflow uses `GITHUB_TOKEN` automatically
3. Pull images with: `docker pull ghcr.io/your-org/sr-aibridge-backend:latest`

## Netlify Integration

### Deploy Webhook

The `netlify/functions/bridge-deploy.js` function:

1. Receives build completion webhooks
2. Authenticates with FORGE_DOMINION_ROOT
3. Triggers BRH node to pull and restart

Configure in Netlify:
- Add `FORGE_DOMINION_ROOT` to environment variables
- Set up build hook to call the function

## Frontend Control Dashboard

The `BridgeRuntimePanel.jsx` component provides:

- Live container status
- Restart/drain controls
- Auto-refresh every 10 seconds
- Forge authentication status

Add to your CommandDeck:

```jsx
import BridgeRuntimePanel from "@/components/BridgeRuntimePanel";

export default function CommandDeck() {
  return (
    <main className="space-y-6 p-8">
      <h1 className="text-3xl font-bold">SR-AIbridge Command Deck</h1>
      <BridgeRuntimePanel />
    </main>
  );
}
```

## Systemd Service (Production)

For persistent BRH node operation:

1. Copy service template:
   ```bash
   sudo cp infra/systemd/brh@.service /etc/systemd/system/
   ```

2. Create seal file:
   ```bash
   sudo mkdir -p /etc/brh
   echo "your-dominion-seal" | sudo tee /etc/brh/dominion.seal
   sudo chmod 600 /etc/brh/dominion.seal
   ```

3. Enable and start:
   ```bash
   sudo systemctl enable brh@"dominion://sovereign.bridge?env=prod&epoch=$(date +%s)&sig=<sig>"
   sudo systemctl start brh@"dominion://..."
   ```

## API Endpoints

When running `brh/api.py`:

- `POST /deploy` - Trigger deployment (pull image + restart)
- `GET /status` - Get container status
- `POST /restart/{name}` - Restart container
- `POST /drain/{name}` - Stop and remove container

## Troubleshooting

### Container won't start

Check logs:
```bash
docker logs brh_api
```

### Health check failing

- Verify the endpoint is correct in `bridge.runtime.yaml`
- Check container logs for startup errors
- Increase `retries` or `interval` if service is slow to start

### Signature verification failed

- Ensure `DOMINION_SEAL` matches between sign and verify
- Check system clock (epoch time must be within ±15 minutes)
- Verify FORGE_DOMINION_ROOT format is correct

### Docker network errors

Reset network:
```bash
docker network rm brh_net
python -m brh.run
```

## Migration from Render

1. Set up BRH on your server with Docker
2. Configure FORGE_DOMINION_ROOT in Netlify
3. Test deployment with bridge-deploy function
4. Update netlify.toml to proxy to BRH node instead of Render
5. Remove render.yaml once validated

## Next Steps (Phase 2)

- [ ] Replace HMAC token minting with SDTF calls
- [ ] Server-side signature verification
- [ ] JWT-based service authentication
- [ ] Multi-node orchestration
- [ ] μ-harmonic lattice integration

## Support

For issues or questions:
1. Check container logs: `docker logs <container>`
2. Verify environment variables are set correctly
3. Review BRH output for error messages
4. Check GitHub Actions logs for build failures
