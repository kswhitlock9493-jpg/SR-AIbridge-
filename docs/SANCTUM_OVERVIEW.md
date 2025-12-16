# Sanctum Overview

## 🧭 Sanctum - Predictive Deployment Simulation Layer

Sanctum is the Bridge's predictive deployment engine that catches configuration issues **before** they reach production.

### Purpose

- **Predict** build failures before deployment
- **Detect** Netlify/Render/GitHub configuration errors
- **Trigger** automated healing through Forge and Cascade
- **Prevent** deployment downtime

### Architecture

```
┌─────────────────────────────┐
│   Sanctum Engine            │
│                             │
│  ┌─────────────────────┐   │
│  │ Virtual Netlify     │   │
│  │ Simulation          │   │
│  └─────────────────────┘   │
│           ↓                 │
│  ┌─────────────────────┐   │
│  │ Config Validation   │   │
│  └─────────────────────┘   │
│           ↓                 │
│  ┌─────────────────────┐   │
│  │ Route Integrity     │   │
│  └─────────────────────┘   │
│           ↓                 │
│  ┌─────────────────────┐   │
│  │ Build Health Check  │   │
│  └─────────────────────┘   │
└─────────────────────────────┘
         ↓
   ┌─────────────┐
   │ Report      │
   └─────────────┘
```

### Features

#### 1. Configuration Validation

Sanctum checks for:
- Missing `_headers`, `_redirects`, `netlify.toml`
- Empty or malformed configuration files
- Invalid redirect rules
- Missing security headers

#### 2. Build Health Assessment

Validates:
- Frontend `package.json` exists
- Backend `requirements.txt` exists
- Build commands are configured
- Publish directory exists

#### 3. Route Integrity

Ensures:
- API routes are properly configured
- Serverless function routing is correct
- SPA fallback routes exist

### Integration Points

#### Genesis Bus Events

Sanctum publishes two key events:

```python
# Success
await genesis_bus.publish("sanctum.predeploy.success", {
    "can_build": True,
    "routes_ok": True,
    "config_ok": True,
    "timestamp": "..."
})

# Failure
await genesis_bus.publish("sanctum.predeploy.failure", {
    "can_build": False,
    "errors": ["Missing _headers", ...],
    "timestamp": "..."
})
```

#### Truth Certification

On successful simulation, Sanctum requests Truth Engine certification:

```python
cert_result = await truth.certify(sim_report, {"ok": True})
```

#### Forge Auto-Repair

On failure, Sanctum automatically triggers Forge:

```python
if sim_report.has_errors():
    from bridge_backend.engines.forge.core import run_full_repair
    run_full_repair(scan_only=False)
```

### Usage

#### Programmatic

```python
from bridge_backend.engines.sanctum.core import SanctumEngine

engine = SanctumEngine()
report = await engine.run_predeploy_check()

if report.has_errors():
    print("Issues detected:", report.errors)
else:
    print("✅ Simulation passed!")
```

#### CLI

```bash
cd bridge_backend/engines/sanctum
python3 core.py
```

#### GitHub Actions

Sanctum runs automatically in the Total Autonomy workflow:

```yaml
- name: Run Sanctum Predictive Simulation
  run: |
    cd bridge_backend/engines/sanctum
    python3 core.py
```

### Configuration

Environment variables:

```bash
# Enable/disable Sanctum
SANCTUM_ENABLED=true

# Genesis bus integration
GENESIS_MODE=enabled
GENESIS_STRICT_POLICY=true
```

### Output Example

```
🧭 Sanctum: Running predictive deployment simulation...
⚠️ Sanctum: Detected 2 issue(s)
  - Missing required file: _headers
  - Missing API route in _redirects
⚠️ Sanctum detected issues — triggering Forge repair.
```

### Error Detection

Sanctum detects:

| Category | Examples |
|----------|----------|
| **Config** | Missing `_headers`, empty `netlify.toml` |
| **Build** | No `package.json`, missing `requirements.txt` |
| **Routes** | Missing API redirect, broken SPA fallback |
| **Security** | Missing security headers |

### Best Practices

1. **Run before every deploy** - Sanctum should be the first step
2. **Trust the simulation** - If Sanctum fails, don't deploy
3. **Review errors** - Check what Sanctum detected before auto-repair
4. **Monitor Genesis events** - Track `sanctum.predeploy.*` events

### Troubleshooting

**Sanctum reports false positives?**
- Check file paths match your repository structure
- Verify `SANCTUM_ENABLED=true`
- Review Genesis Bus event history

**Auto-repair not triggering?**
- Ensure Forge engine is available
- Check `FORGE_ENABLED=true`
- Verify Genesis Bus is active

### Related

- [Forge Auto-Repair Guide](FORGE_AUTOREPAIR_GUIDE.md)
- [ARIE Sanctum Loop](ARIE_SANCTUM_LOOP.md)
- [Total Autonomy Protocol](TOTAL_AUTONOMY_PROTOCOL.md)
