# Bridge Runtime Handler (BRH)

**Self-hosted, sovereign backend runtime manager using Docker + HMAC authentication**

## What is BRH?

The Bridge Runtime Handler is a lightweight, secure runtime orchestrator that replaces cloud platforms like Render with self-hosted Docker infrastructure. It uses FORGE_DOMINION_ROOT (one variable to rule them all) for authentication and provides complete control over your backend deployment.

## Quick Start

```bash
# 1. Generate authentication
./examples/generate_forge_root.sh dev my-seal

# 2. Set environment (copy from output above)
export FORGE_DOMINION_ROOT="dominion://sovereign.bridge?env=dev&epoch=XXX&sig=XXX"
export DOMINION_SEAL="my-seal"

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run BRH
cd ..
python -m brh.run
```

## Components

- **forge_auth.py** - HMAC-SHA256 authentication and token minting
- **run.py** - Container orchestration with health checks
- **api.py** - FastAPI server for remote control
- **examples/** - Helper scripts and tests

## Key Features

- ✅ HMAC-SHA256 signature verification
- ✅ Docker container lifecycle management  
- ✅ HTTP/TCP health checking
- ✅ Remote control API
- ✅ Image name validation (prevents injection)
- ✅ Configurable CORS origins
- ✅ Systemd service support

## Documentation

- [Deployment Guide](../BRH_DEPLOYMENT_GUIDE.md) - Full setup instructions
- [Quick Reference](../BRH_QUICK_REF.md) - Command cheat sheet
- [Implementation Summary](../BRH_IMPLEMENTATION_COMPLETE.md) - What was built
- [Examples README](examples/README.md) - Helper scripts

## Security

BRH implements defense-in-depth security:

1. **Authentication**: HMAC-SHA256 signature with time skew protection
2. **Validation**: Image names validated to prevent command injection
3. **Isolation**: Docker network isolation between services
4. **Access Control**: Configurable CORS for API endpoints
5. **Secrets**: No hardcoded credentials, environment-based

## Architecture

```
FORGE_DOMINION_ROOT
      │
      ├─→ forge_auth.py (verify)
      ├─→ run.py (orchestrate)
      └─→ api.py (control)
            │
            └─→ Docker
                  └─→ Containers
```

## Requirements

- Python 3.11+
- Docker
- `pyyaml`, `requests`, `docker` (see requirements.txt)
- Optional: `fastapi`, `uvicorn` (for API server)

## License

Part of the SR-AIbridge project.
