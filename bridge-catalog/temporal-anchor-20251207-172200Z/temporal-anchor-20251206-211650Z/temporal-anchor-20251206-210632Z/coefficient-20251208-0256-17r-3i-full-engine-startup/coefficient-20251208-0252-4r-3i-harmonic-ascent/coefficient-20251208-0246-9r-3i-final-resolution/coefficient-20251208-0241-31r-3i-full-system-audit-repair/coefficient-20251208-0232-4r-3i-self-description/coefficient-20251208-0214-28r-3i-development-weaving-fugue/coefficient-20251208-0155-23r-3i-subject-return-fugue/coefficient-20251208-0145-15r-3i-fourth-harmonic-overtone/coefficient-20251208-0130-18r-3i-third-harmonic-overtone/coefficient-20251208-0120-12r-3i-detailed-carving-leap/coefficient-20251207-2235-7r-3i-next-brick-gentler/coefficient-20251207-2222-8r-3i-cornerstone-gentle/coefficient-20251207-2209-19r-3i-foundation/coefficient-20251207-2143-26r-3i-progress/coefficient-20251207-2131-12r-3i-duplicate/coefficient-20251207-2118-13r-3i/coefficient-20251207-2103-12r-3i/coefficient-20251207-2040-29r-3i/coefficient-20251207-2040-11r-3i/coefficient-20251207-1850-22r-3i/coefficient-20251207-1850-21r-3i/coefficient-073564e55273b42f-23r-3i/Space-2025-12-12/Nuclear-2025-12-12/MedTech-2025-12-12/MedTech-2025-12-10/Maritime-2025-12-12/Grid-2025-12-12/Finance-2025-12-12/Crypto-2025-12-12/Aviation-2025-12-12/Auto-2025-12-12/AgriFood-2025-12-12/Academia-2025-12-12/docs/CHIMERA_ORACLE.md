# Chimera Oracle

## Overview

The Chimera Oracle is a predictive deployment engine that orchestrates autonomous deployment with certification and fallback capabilities.

## Architecture

```
┌────────────────────────────┐
│         Genesis            │
│   (Event & Cert Bus)       │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│          Chimera           │
│  Predictive Deploy Engine  │
└────────────┬───────────────┘
             │
    ┌────────┼────────┐
    ▼        ▼        ▼
┌────────┐ ┌──────────┐ ┌────────┐
│Hydra   │ │Leviathan │ │ARIE    │
│(Guard) │ │(Simulate)│ │(Heal)  │
└────────┘ └──────────┘ └────────┘
```

## Features

### 1. Environment Audit
- Checks for environment drift
- Triggers healing intent when drift detected
- Applies local corrections in safe mode

### 2. Build Simulation (Leviathan)
- Dry-run build without actual deployment
- Route prediction and validation
- Estimated build time calculation

### 3. Configuration Synthesis (Hydra v2)
- Automatically generates Netlify headers
- Creates redirect rules
- Validates configuration files

### 4. Truth Certification
- Certifies deployment readiness
- Blocks deployments that fail certification
- Issues cryptographic signatures for approved deployments

### 5. Deploy Execution with Fallback
- Attempts Netlify deployment first
- Falls back to Render if Netlify fails
- Maintains parity between platforms

## Usage

### CLI

```bash
# Predictive deployment
python -m bridge_backend.cli.deployctl predictive --ref main
```

### API

```bash
# Execute predictive deployment
curl -X POST http://localhost:8000/api/chimera/deploy/predictive \
  -H "Content-Type: application/json" \
  -d '{"ref": "main"}'
```

### Python

```python
from bridge_backend.engines.chimera import ChimeraOracle

oracle = ChimeraOracle()
result = await oracle.run({"ref": "main"})
```

## Decision Matrix

The Chimera Oracle uses a decision matrix to determine the optimal deployment path:

| Condition | Target | Confidence |
|-----------|--------|------------|
| `can_build=true` AND `guard_ok=true` | Netlify | High |
| `can_build=false` OR `guard_ok=false` | Render | Low |

## Genesis Events

The Chimera Oracle publishes the following events to the Genesis bus:

- `env.heal.intent` - Environment healing intent
- `deploy.simulate` - Simulation results
- `deploy.guard.netlify` - Netlify guard synthesis results
- `arie.fix.applied` - ARIE fix application
- `deploy.certificate` - Truth certification results
- `deploy.plan` - Deployment plan
- `deploy.fallback.render` - Render fallback activation
- `deploy.outcome.success` - Successful deployment
- `deploy.outcome.failure` - Failed deployment

## RBAC

All deployment operations require **Admiral** role.

## Configuration

Environment variables:

- `RBAC_ENFORCED` - Enable RBAC enforcement (default: false)
- `TRUTH_CERTIFICATION` - Enable Truth certification (default: false)
- `GENESIS_MODE` - Genesis bus mode (default: enabled)
