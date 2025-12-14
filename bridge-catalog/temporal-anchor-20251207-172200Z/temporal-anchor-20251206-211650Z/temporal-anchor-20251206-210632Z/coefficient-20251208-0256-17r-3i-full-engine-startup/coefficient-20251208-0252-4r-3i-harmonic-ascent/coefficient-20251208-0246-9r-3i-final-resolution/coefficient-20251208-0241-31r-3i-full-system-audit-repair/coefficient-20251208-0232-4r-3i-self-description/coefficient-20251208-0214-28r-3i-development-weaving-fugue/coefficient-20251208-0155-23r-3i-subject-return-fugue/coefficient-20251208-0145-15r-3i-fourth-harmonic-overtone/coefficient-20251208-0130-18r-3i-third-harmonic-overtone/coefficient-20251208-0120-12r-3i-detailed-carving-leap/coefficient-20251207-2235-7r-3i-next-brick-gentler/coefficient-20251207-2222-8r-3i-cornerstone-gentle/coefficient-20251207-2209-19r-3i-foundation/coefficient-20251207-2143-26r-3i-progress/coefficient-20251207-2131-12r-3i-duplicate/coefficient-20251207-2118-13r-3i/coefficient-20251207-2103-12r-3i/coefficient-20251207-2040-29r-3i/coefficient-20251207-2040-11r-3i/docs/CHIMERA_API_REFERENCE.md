# Chimera API Reference

Complete API reference for the Chimera Deployment Engine.

---

## CLI Commands

### `chimeractl`

Main command-line interface for Chimera Deployment Engine.

#### Global Options

```bash
chimeractl [command] [options]
```

---

### Commands

#### `simulate`

Run deployment simulation without actually deploying.

**Usage:**
```bash
chimeractl simulate --platform <platform> [options]
```

**Options:**
- `--platform` (required): Target platform (`netlify`, `render`, `github_pages`)
- `--path`: Project path (default: current directory)
- `--auto-heal`: Show auto-heal recommendations
- `--json`: Output results as JSON

**Examples:**
```bash
# Simulate Netlify deployment
chimeractl simulate --platform netlify

# Simulate with JSON output
chimeractl simulate --platform render --json

# Simulate specific path
chimeractl simulate --platform netlify --path /path/to/project
```

**Returns:**
- Exit code 0: Success (no critical issues)
- Exit code 1: Issues detected

---

#### `deploy`

Execute autonomous deployment with full pipeline.

**Usage:**
```bash
chimeractl deploy --platform <platform> [options]
```

**Options:**
- `--platform` (required): Target platform (`netlify`, `render`, `github_pages`)
- `--path`: Project path (default: current directory)
- `--no-heal`: Disable automatic healing
- `--certify`: Require Truth Engine certification (default: true)
- `--json`: Output results as JSON

**Examples:**
```bash
# Deploy to Netlify with certification
chimeractl deploy --platform netlify --certify

# Deploy to Render without healing
chimeractl deploy --platform render --no-heal

# Deploy with JSON output
chimeractl deploy --platform netlify --json
```

**Returns:**
- Exit code 0: Deployment successful
- Exit code 1: Deployment failed or rejected

---

#### `monitor`

Monitor Chimera deployment status and history.

**Usage:**
```bash
chimeractl monitor [options]
```

**Options:**
- `--json`: Output as JSON

**Examples:**
```bash
# Monitor status
chimeractl monitor

# Get JSON output
chimeractl monitor --json
```

---

#### `verify`

Verify deployment with Truth Engine certification.

**Usage:**
```bash
chimeractl verify --platform <platform> [options]
```

**Options:**
- `--platform` (required): Target platform
- `--path`: Project path (default: current directory)
- `--json`: Output as JSON

**Examples:**
```bash
# Verify Netlify deployment
chimeractl verify --platform netlify

# Verify with JSON output
chimeractl verify --platform render --json
```

**Returns:**
- Exit code 0: Certification passed
- Exit code 1: Certification failed

---

## REST API Endpoints

Base URL: `http://localhost:8000/api/chimera`

### GET `/status`

Get Chimera engine status.

**Response:**
```json
{
  "enabled": true,
  "config": {
    "engine": "CHIMERA_DEPLOYMENT_ENGINE",
    "codename": "HXO-Echelon-03",
    "autonomy_level": "TOTAL",
    ...
  },
  "deployments_count": 10,
  "certifications_count": 8,
  "recent_deployments": [...],
  "timestamp": "2025-10-12T00:00:00.000Z"
}
```

---

### GET `/config`

Get Chimera configuration.

**Response:**
```json
{
  "engine": "CHIMERA_DEPLOYMENT_ENGINE",
  "codename": "HXO-Echelon-03",
  "core_protocol": "Predictive_Autonomous_Deployment",
  "connected_systems": [
    "HXO_CORE",
    "LEVIATHAN_ENGINE",
    ...
  ],
  "policies": {
    "simulate_before_deploy": true,
    "heal_on_detected_drift": true,
    ...
  }
}
```

---

### POST `/simulate`

Run deployment simulation.

**Request:**
```json
{
  "platform": "netlify",
  "project_path": "/path/to/project"  // optional
}
```

**Response:**
```json
{
  "status": "passed",
  "timestamp": "2025-10-12T00:00:00.000Z",
  "duration_seconds": 2.3,
  "issues": [],
  "warnings": [],
  "issues_count": 0,
  "warnings_count": 0,
  "simulation_accuracy": "99.8%"
}
```

---

### POST `/deploy`

Execute autonomous deployment.

**Request:**
```json
{
  "platform": "netlify",
  "project_path": "/path/to/project",  // optional
  "auto_heal": true,
  "certify": true
}
```

**Response:**
```json
{
  "status": "success",
  "platform": "netlify",
  "timestamp": "2025-10-12T00:00:00.000Z",
  "duration_seconds": 228.5,
  "simulation": {...},
  "healing": {...},
  "certification": {
    "certified": true,
    "signature": "abc123...",
    ...
  },
  "deployment": {...},
  "verification": {...}
}
```

---

### GET `/deployments`

Get deployment history.

**Response:**
```json
{
  "deployments": [
    {
      "status": "success",
      "platform": "netlify",
      "timestamp": "2025-10-12T00:00:00.000Z",
      ...
    }
  ],
  "count": 10
}
```

---

### GET `/certifications`

Get certification history.

**Response:**
```json
{
  "certifications": [
    {
      "certified": true,
      "timestamp": "2025-10-12T00:00:00.000Z",
      "protocol": "TRUTH_CERT_V3",
      "signature": "abc123...",
      ...
    }
  ],
  "count": 8
}
```

---

## Genesis Bus Events

### Published Events

#### `deploy.initiated`

Published when deployment starts.

**Payload:**
```json
{
  "platform": "netlify",
  "timestamp": "2025-10-12T00:00:00.000Z",
  "auto_heal": true,
  "certify": true
}
```

---

#### `deploy.heal.intent`

Published when healing is needed.

**Payload:**
```json
{
  "platform": "netlify",
  "issues_count": 3,
  "timestamp": "2025-10-12T00:00:00.000Z"
}
```

---

#### `deploy.heal.complete`

Published when healing finishes.

**Payload:**
```json
{
  "platform": "netlify",
  "fixes_applied": 2,
  "timestamp": "2025-10-12T00:00:00.000Z"
}
```

---

#### `deploy.certified`

Published when certification completes.

**Payload:**
```json
{
  "platform": "netlify",
  "certified": true,
  "signature": "abc123...",
  "timestamp": "2025-10-12T00:00:00.000Z"
}
```

---

#### `chimera.simulate.start`

Published when simulation starts.

---

#### `chimera.simulate.complete`

Published when simulation completes.

---

#### `chimera.deploy.start`

Published when deployment execution starts.

---

#### `chimera.deploy.complete`

Published when deployment execution completes.

---

#### `chimera.rollback.triggered`

Published when rollback is initiated.

**Payload:**
```json
{
  "platform": "netlify",
  "reason": "certification_failed",
  "timestamp": "2025-10-12T00:00:00.000Z"
}
```

---

## Python API

### ChimeraDeploymentEngine

Main engine class.

```python
from bridge_backend.bridge_core.engines.chimera import ChimeraDeploymentEngine, ChimeraConfig

# Initialize
config = ChimeraConfig()
chimera = ChimeraDeploymentEngine(config)

# Or use singleton
from bridge_backend.bridge_core.engines.chimera import get_chimera_instance
chimera = get_chimera_instance()
```

#### Methods

##### `deploy(platform, project_path=None, auto_heal=True, certify=True)`

Execute autonomous deployment.

**Parameters:**
- `platform` (str): Target platform
- `project_path` (Path, optional): Project root path
- `auto_heal` (bool): Enable automatic healing
- `certify` (bool): Require certification

**Returns:** Dict with deployment results

---

##### `simulate(platform, project_path=None)`

Run simulation only.

**Returns:** Dict with simulation results

---

##### `monitor()`

Get current status.

**Returns:** Dict with status information

---

### ChimeraConfig

Configuration dataclass.

```python
from bridge_backend.bridge_core.engines.chimera import ChimeraConfig

config = ChimeraConfig(
    enabled=True,
    simulation_timeout=300,
    healing_max_attempts=3
)

# Export as JSON
json_str = config.to_json()

# Export as dict
config_dict = config.to_dict()
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CHIMERA_ENABLED` | `true` | Enable/disable Chimera engine |
| `CHIMERA_SIM_TIMEOUT` | `300` | Simulation timeout (seconds) |
| `CHIMERA_HEAL_MAX_ATTEMPTS` | `3` | Maximum healing attempts |

---

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 0 | Success | Operation completed successfully |
| 1 | Failure | Operation failed or rejected |
| 500 | Server Error | Internal server error |

---

## Rate Limits

No rate limits currently enforced for CLI or API usage.

---

## Examples

### Full Deployment Pipeline

```python
import asyncio
from pathlib import Path
from bridge_backend.bridge_core.engines.chimera import get_chimera_instance

async def deploy_to_netlify():
    chimera = get_chimera_instance()
    
    result = await chimera.deploy(
        platform="netlify",
        project_path=Path.cwd(),
        auto_heal=True,
        certify=True
    )
    
    if result["status"] == "success":
        print(f"✅ Deployed: {result['certification']['signature']}")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")

asyncio.run(deploy_to_netlify())
```

### Simulation Only

```bash
curl -X POST http://localhost:8000/api/chimera/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "netlify"
  }'
```

### Monitor Status

```bash
watch -n 5 'chimeractl monitor'
```
