# Status Badges

Add these badges to your README to show the health of SR-AIbridge:

## Health Status

```markdown
![Bridge Health](https://img.shields.io/badge/Bridge_Health-Stable-brightgreen)
![Build Triage](https://img.shields.io/badge/Build-PASS-brightgreen)
![Runtime Triage](https://img.shields.io/badge/Runtime-PASS-brightgreen)
![Env Parity](https://img.shields.io/badge/Env-Parity-blue)
```

### Rendered:

![Bridge Health](https://img.shields.io/badge/Bridge_Health-Stable-brightgreen)
![Build Triage](https://img.shields.io/badge/Build-PASS-brightgreen)
![Runtime Triage](https://img.shields.io/badge/Runtime-PASS-brightgreen)
![Env Parity](https://img.shields.io/badge/Env-Parity-blue)

## Workflow Status

```markdown
![Build Triage](https://github.com/kswhitlock9493-jpg/SR-AIbridge-/actions/workflows/build_triage_netlify.yml/badge.svg)
![Runtime Triage](https://github.com/kswhitlock9493-jpg/SR-AIbridge-/actions/workflows/runtime_triage_render.yml/badge.svg)
![Deploy Gate](https://github.com/kswhitlock9493-jpg/SR-AIbridge-/actions/workflows/deploy_gate.yml/badge.svg)
![Endpoint Sweep](https://github.com/kswhitlock9493-jpg/SR-AIbridge-/actions/workflows/endpoint_api_sweep.yml/badge.svg)
![Env Parity](https://github.com/kswhitlock9493-jpg/SR-AIbridge-/actions/workflows/environment_parity_guard.yml/badge.svg)
```

## Component Status

```markdown
![Federation](https://img.shields.io/badge/Federation-Online-brightgreen)
![Database](https://img.shields.io/badge/Database-Connected-brightgreen)
![Build System](https://img.shields.io/badge/Build-Passing-brightgreen)
![Deployments](https://img.shields.io/badge/Deployments-Green-brightgreen)
```

### Rendered:

![Federation](https://img.shields.io/badge/Federation-Online-brightgreen)
![Database](https://img.shields.io/badge/Database-Connected-brightgreen)
![Build System](https://img.shields.io/badge/Build-Passing-brightgreen)
![Deployments](https://img.shields.io/badge/Deployments-Green-brightgreen)

## Security & Compliance

```markdown
![Security Scan](https://img.shields.io/badge/Security-Passing-brightgreen)
![Code Quality](https://img.shields.io/badge/Code_Quality-A-brightgreen)
![Uptime](https://img.shields.io/badge/Uptime-99.9%25-brightgreen)
```

### Rendered:

![Security Scan](https://img.shields.io/badge/Security-Passing-brightgreen)
![Code Quality](https://img.shields.io/badge/Code_Quality-A-brightgreen)
![Uptime](https://img.shields.io/badge/Uptime-99.9%25-brightgreen)

## Status Colors

- 🟢 **Green (brightgreen)** - Passing, healthy, stable
- 🔵 **Blue** - Informational, parity, synchronized  
- 🟡 **Yellow** - Warning, degraded, attention needed
- 🔴 **Red** - Failed, critical, action required

## Custom Badge Examples

### Build Status with Size

```markdown
![Build](https://img.shields.io/badge/Build-PASS-brightgreen)
![Size](https://img.shields.io/badge/Size-2.3MB-blue)
```

### Runtime with Response Time

```markdown
![Runtime](https://img.shields.io/badge/Runtime-Healthy-brightgreen)
![Response](https://img.shields.io/badge/Response-120ms-blue)
```

### Environment with Version

```markdown
![Environment](https://img.shields.io/badge/Env-Synced-blue)
![Version](https://img.shields.io/badge/Version-v1.8.2-blue)
```

## Dynamic Badges

For dynamic badges that update based on actual workflow status:

```markdown
[![Build Triage](https://github.com/{owner}/{repo}/actions/workflows/build_triage_netlify.yml/badge.svg)](https://github.com/{owner}/{repo}/actions/workflows/build_triage_netlify.yml)
```

Replace `{owner}` and `{repo}` with your GitHub username and repository name.

## Badge Templates

### Success Template
```markdown
![{Component}](https://img.shields.io/badge/{Component}-PASS-brightgreen)
```

### Info Template
```markdown
![{Component}](https://img.shields.io/badge/{Component}-{Value}-blue)
```

### Warning Template
```markdown
![{Component}](https://img.shields.io/badge/{Component}-WARNING-yellow)
```

### Error Template
```markdown
![{Component}](https://img.shields.io/badge/{Component}-FAIL-red)
```

## Shield.io Documentation

For more badge customization options, visit: https://shields.io/

## Suggested README Section

```markdown
## 🏥 System Health

![Bridge Health](https://img.shields.io/badge/Bridge_Health-Stable-brightgreen)
![Build Triage](https://img.shields.io/badge/Build-PASS-brightgreen)
![Runtime Triage](https://img.shields.io/badge/Runtime-PASS-brightgreen)
![Env Parity](https://img.shields.io/badge/Env-Parity-blue)

SR-AIbridge uses automated triage and health monitoring across the entire stack:

- ✅ Build validation and artifact verification
- ✅ Runtime health checks and database connectivity
- ✅ Federation schema version alignment
- ✅ Endpoint and API sweep for route validation
- ✅ Environment parity and drift detection

For details, see [Total-Stack Triage documentation](docs/TOTAL_STACK_TRIAGE.md).
```
