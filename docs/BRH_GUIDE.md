# 🧠 Bridge Runtime Handler (BRH) Guide

**Version:** 1.0.0-alpha  
**Status:** Phase 1 - Core Runtime Implementation  
**Sovereignty Level:** Full

---

## 🌟 Overview

The Bridge Runtime Handler (BRH) is a **repo-level backend supervisor** that transforms each Bridge repository into a self-contained, sovereign deployment node. It eliminates dependency on third-party platforms like Render or Vercel by managing its own runtime using ephemeral Forge Dominion tokens.

### Key Principles

1. **Sovereign Ownership** - 100% control over runtime and deployment
2. **Ephemeral Auth** - No static secrets, all tokens auto-expire
3. **Federation-Ready** - Multi-node sync via μ-harmonic lattice
4. **Self-Healing** - Auto-recovery from container failures
5. **Forge-Governed** - Cryptographic attestation for all operations

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  GitHub Repository                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  src/bridge.runtime.yaml (Manifest)                 │   │
│  │  src/forge-auth.go (Token Manager)                  │   │
│  │  src/manifest.json (Schema)                         │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           Sovereign Runtime Core (SRC)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  bridge_core/runtime_handler.py                      │  │
│  │  - Manifest Parser                                   │  │
│  │  - Forge Auth Integration                            │  │
│  │  - Container Lifecycle Management                    │  │
│  │  - Token Auto-Renewal                                │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Forge Dominion Layer                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FORGE_DOMINION_ROOT (Secret)                        │  │
│  │  ├─ Ephemeral Token Mint                             │  │
│  │  ├─ HMAC-SHA256 Signing                              │  │
│  │  ├─ Auto-Expiry (1hr default)                        │  │
│  │  └─ Auto-Renewal                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          Sovereign Deploy Protocol (SDP)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  .github/workflows/bridge_deploy.yml                 │  │
│  │  ├─ Forge Authentication                             │  │
│  │  ├─ Manifest Validation                              │  │
│  │  ├─ Container Deployment                             │  │
│  │  ├─ Node Registration                                │  │
│  │  └─ Health Verification                              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         Active Runtime Nodes (Federation Layer)              │
│  forge/runtime/active_nodes.json                             │
│  ├─ Node Registry                                            │
│  ├─ Health States                                            │
│  ├─ μ-Harmonic Sync                                          │
│  └─ Federation Heartbeats                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

1. **Forge Dominion Root Key** configured in GitHub Secrets:
   ```bash
   gh secret set FORGE_DOMINION_ROOT --body "$(python -c 'import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("="))')"
   ```

2. **Runtime Manifest** at `src/bridge.runtime.yaml`

3. **Python 3.12+** for runtime handler

### Step 1: Configure Runtime Manifest

Edit `src/bridge.runtime.yaml`:

```yaml
version: "1.0"
runtime:
  name: "my-bridge-runtime"
  type: "sovereign"
  
  auth:
    provider: "forge_dominion"
    token_mode: "ephemeral"
    token_ttl: 3600
    auto_renew: true
  
  containers:
    - name: "backend-api"
      image: "python:3.12-slim"
      command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
      ports:
        - "8000:8000"
      health_check:
        path: "/health"
        interval: 30
```

### Step 2: Initialize Runtime Locally

```bash
# Set Forge root key
export FORGE_DOMINION_ROOT="your_key_here"

# Run runtime handler
cd bridge_backend
python bridge_core/runtime_handler.py
```

### Step 3: Deploy via GitHub Actions

Push to main branch to trigger deployment:

```bash
git add .
git commit -m "feat: enable Bridge Runtime Handler"
git push origin main
```

The `bridge_deploy.yml` workflow will:
1. ✅ Authenticate with Forge Dominion
2. ✅ Validate runtime manifest
3. ✅ Generate ephemeral deployment token
4. ✅ Deploy containers
5. ✅ Register runtime node
6. ✅ Perform health checks

---

## 📋 Configuration Reference

### Runtime Manifest Schema

#### `runtime.auth`
- `provider`: Authentication provider (currently only `forge_dominion`)
- `token_mode`: `ephemeral` (recommended) or `static` (deprecated)
- `token_ttl`: Token lifetime in seconds (default: 3600)
- `auto_renew`: Automatically renew tokens before expiry (default: true)

#### `runtime.containers`
- `name`: Unique container identifier
- `image`: Container image (Docker format)
- `command`: Array of command and arguments
- `environment`: Array of env vars in `KEY=value` format
- `ports`: Array of port mappings (`"host:container"`)
- `health_check`: Health check configuration
  - `path`: HTTP path to check
  - `interval`: Check interval in seconds
  - `timeout`: Request timeout in seconds
  - `retries`: Max failed checks before unhealthy
- `resources`: Resource limits
  - `memory`: Memory limit (e.g., `"512Mi"`, `"1Gi"`)
  - `cpu`: CPU limit (e.g., `"0.5"`, `"2"`)

#### `runtime.federation`
- `enabled`: Enable federation with other BRH nodes
- `lattice_mode`: `"harmonic"`, `"mesh"`, or `"star"`
- `heartbeat_interval`: Heartbeat frequency in seconds
- `sync_protocol`: Protocol for state replication

#### `security.attestation`
- `enabled`: Enable cryptographic attestation
- `seal_algorithm`: `"HMAC-SHA256"` or `"HMAC-SHA512"`

---

## 🔐 Security

### Token Lifecycle

1. **Generation**: Tokens are generated on-demand with HMAC-SHA256 signatures
2. **Validation**: Each operation validates token signature and expiry
3. **Renewal**: Tokens auto-renew 5 minutes before expiry
4. **Expiry**: Expired tokens are immediately rejected

### Forge Dominion Integration

The BRH uses the existing Forge Dominion system:

```python
from bridge_core.token_forge_dominion import ForgeAuthority

auth = ForgeAuthority()
token = auth.generate_runtime_token(
    node_id="bridge-runtime-001",
    scope="runtime:execute",
    ttl_seconds=3600
)
```

### Attestation

All deployments are cryptographically signed:

```
Seal = HMAC-SHA256(FORGE_DOMINION_ROOT, "deploy:{commit_sha}:{timestamp}")
```

---

## 🌐 Federation

### μ-Harmonic Lattice Integration

BRH nodes can sync with each other using the existing lattice system:

```python
from bridge_core.lattice import heartbeat

# Register node in lattice
heartbeat.register_node(
    node_id=runtime.node_id,
    node_type="runtime_handler",
    metadata={
        "containers": len(runtime.running_containers),
        "health": runtime.health_status
    }
)
```

### Multi-Node Deployment

Enable federation in manifest:

```yaml
runtime:
  federation:
    enabled: true
    lattice_mode: "harmonic"
    heartbeat_interval: 10
    sync_protocol: "μ-state-replication"
```

---

## 📊 Monitoring

### Health Endpoint

Each BRH node exposes health status:

```bash
curl http://localhost:8000/bridge/runtime/health
```

Response:
```json
{
  "node_id": "bridge-runtime-abc123",
  "status": "healthy",
  "token_valid": true,
  "containers": {
    "backend-api": {
      "status": "running",
      "uptime": "2025-11-03T22:00:00Z"
    }
  }
}
```

### Logs

Runtime logs are stored in the Sovereign Ledger:

```
bridge_backend/vault/runtime/
├── deploy_20251103_220000.json
├── health_20251103_220100.json
└── token_renewal_20251103_220500.json
```

### Active Nodes Registry

View all active runtime nodes:

```bash
cat forge/runtime/active_nodes.json
```

---

## 🔧 Troubleshooting

### Token Validation Failures

**Problem**: `Token signature validation failed`

**Solution**:
1. Verify `FORGE_DOMINION_ROOT` is set correctly
2. Check token hasn't expired
3. Ensure no trailing whitespace in root key

### Container Won't Start

**Problem**: Container fails to start

**Solution**:
1. Check manifest syntax with `yaml-lint`
2. Verify image exists and is accessible
3. Check resource limits aren't too restrictive
4. Review container logs in vault

### Federation Sync Issues

**Problem**: Nodes not syncing

**Solution**:
1. Verify `federation.enabled: true` in manifest
2. Check heartbeat intervals match across nodes
3. Ensure lattice endpoints are accessible
4. Review federation logs

---

## 🛣️ Roadmap

### ✅ Phase 1: Core Runtime (Current)
- [x] Runtime manifest schema and parser
- [x] Forge authentication integration
- [x] Token generation and validation
- [x] Basic container lifecycle management
- [x] GitHub Actions integration

### 🚧 Phase 2: GitHub Integration (Next)
- [ ] Full container orchestration (Docker/Firecracker)
- [ ] Advanced health monitoring
- [ ] Log aggregation to Sovereign Ledger
- [ ] Metrics collection and visualization
- [ ] Auto-scaling based on load

### 📅 Phase 3: Federation Linking
- [ ] Multi-node state synchronization
- [ ] Distributed load balancing
- [ ] Cross-node failover
- [ ] Consensus-based configuration updates

### 🔮 Phase 4: UI Integration
- [ ] Command Deck BRH panel
- [ ] Real-time node visualization
- [ ] Log streaming interface
- [ ] Interactive deployment controls

---

## 📚 Additional Resources

- [Forge Dominion Guide](FORGE_DOMINION_DEPLOYMENT_GUIDE.md)
- [HXO Nexus Connectivity](HXO_NEXUS_CONNECTIVITY.md)
- [μ-Harmonic Lattice Documentation](docs/LATTICE_GUIDE.md)
- [GitHub Actions Integration](docs/GITHUB_ACTIONS.md)

---

## 🤝 Contributing

BRH is part of the SR-AIbridge ecosystem. Contributions welcome!

1. Fork the repository
2. Create feature branch: `git checkout -b feature/brh-enhancement`
3. Make changes and test thoroughly
4. Submit pull request with detailed description

---

## 📄 License

MIT License - See LICENSE file for details

---

**Built with sovereignty and precision by the Bridge Federation**

*"No vendor lock-in. No static secrets. Only sovereign runtime."*
