# SR-AIbridge Deployment Automation

## Overview

This document describes the automated deployment infrastructure for SR-AIbridge v1.7.4, including the Deploy Path Triage Auto-Repair Engine, Netlify Health Badge system, and CI/CD validation.

---

## Netlify Environment Structure

### Build Configuration

The Netlify deployment is configured via `netlify.toml` with the following structure:

```toml
[build]
  base = "bridge-frontend"
  command = "npm run build"
  publish = "dist"
  functions = "netlify/functions"

[build.environment]
  NODE_ENV = "production"
  VITE_API_BASE = "https://sr-aibridge.onrender.com"
  REACT_APP_API_URL = "https://sr-aibridge.onrender.com"
```

### Key Features

- **Simplified Path Resolution**: Uses relative `dist` path instead of `bridge-frontend/dist`
- **Streamlined Build**: Single `npm run build` command
- **Environment Variables**: Minimal set of production-ready variables
- **Auto-Redirects**: SPA routing support via catch-all redirect

---

## Deploy Path Triage Engine

### Overview

The Deploy Path Triage Engine (`bridge_backend/tools/triage/deploy_path_triage.py`) is an automated system that:

1. Validates the existence of the Netlify publish directory (`dist/`)
2. Automatically rebuilds the frontend if the directory is missing
3. Generates health status badges
4. Creates diagnostic reports

### Lifecycle

```
┌─────────────────────────────────┐
│  Deploy Path Triage Engine      │
│  Started                         │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│  Check if dist/ exists           │
└─────────────┬───────────────────┘
              │
        ┌─────┴─────┐
        │           │
       Yes          No
        │           │
        ▼           ▼
    ┌───────┐  ┌────────────┐
    │Verify │  │ Run Build  │
    └───┬───┘  └─────┬──────┘
        │            │
        │      ┌─────┴─────┐
        │      │           │
        │    Success     Fail
        │      │           │
        ▼      ▼           ▼
    ┌────────────────────────┐
    │  Generate Badge        │
    │  & Report              │
    └────────────────────────┘
```

### Status Types

- **verified**: Deploy directory exists and is valid (green badge)
- **rebuilt**: Directory was missing but build succeeded (yellow badge)
- **failed**: Build failed and manual intervention required (red badge)

### Generated Artifacts

1. **Diagnostic Report**: `bridge_backend/diagnostics/deploy_path_triage_report.json`
   ```json
   {
     "timestamp": "2025-01-08T18:55:42Z",
     "frontend": "/repo/bridge-frontend",
     "dist": "/repo/bridge-frontend/dist",
     "status": "verified",
     "message": "✅ Verified deploy directory."
   }
   ```

2. **Health Badge**: `docs/BADGE_DEPLOY_STATUS.md`
   ```markdown
   # Netlify Health Badge
   
   ![Netlify Deploy Status](https://img.shields.io/badge/Netlify_verified-brightgreen?style=for-the-badge)
   
   Updated: 2025-01-08T18:55:42.000000 UTC
   ```

---

## Badge Synchronization Logic

### Integration Points

1. **README.md**: Displays current Netlify deployment health
2. **CI/CD Pipeline**: Generates badges on every push/PR
3. **Diagnostics Dashboard**: Badge status available via JSON report

### Badge States

| Status | Color | Badge | Meaning |
|--------|-------|-------|---------|
| verified | Green | ![verified](https://img.shields.io/badge/Netlify_verified-brightgreen?style=for-the-badge) | Deploy directory exists |
| rebuilt | Yellow | ![rebuilt](https://img.shields.io/badge/Netlify_rebuilt-yellow?style=for-the-badge) | Auto-repair succeeded |
| failed | Red | ![failed](https://img.shields.io/badge/Netlify_failed-red?style=for-the-badge) | Manual intervention needed |

---

## CI/CD Integration

### Workflow: Deploy Path Verification

**File**: `.github/workflows/deploy_triage.yml`

**Triggers**:
- Push to `main` branch
- Pull requests
- Manual workflow dispatch

**Steps**:
1. Checkout repository
2. Setup Python 3.11
3. Run Deploy Path Triage Engine
4. Upload diagnostic report as artifact
5. Upload health badge as artifact

**Artifacts**:
- `deploy_path_triage_report`: JSON diagnostic report
- `netlify_health_badge`: Markdown badge file

### Workflow Benefits

- ✅ **Pre-deployment Validation**: Catches path issues before Netlify build
- ✅ **Automatic Healing**: Rebuilds missing dist/ directory
- ✅ **Transparency**: Every build state is documented
- ✅ **Artifact Storage**: Historical records of all triage runs

---

## Self-Healing Deployment

### Auto-Repair Flow

1. **Detection**: Triage engine detects missing `dist/` directory
2. **Installation**: Runs `npm install` in frontend directory
3. **Build**: Executes `npm run build`
4. **Verification**: Confirms `dist/` was created
5. **Reporting**: Generates "rebuilt" status badge and report

### Failure Handling

If auto-repair fails:
- Status set to "failed"
- Red badge generated
- Error details logged to diagnostic report
- CI/CD workflow continues (non-blocking)

---

## Usage

### Manual Triage Run

```bash
cd /path/to/SR-AIbridge
python3 bridge_backend/tools/triage/deploy_path_triage.py
```

### CI/CD Trigger

```bash
# Via GitHub CLI
gh workflow run deploy_triage.yml

# Check status
gh run list --workflow=deploy_triage.yml
```

### View Diagnostic Report

```bash
cat bridge_backend/diagnostics/deploy_path_triage_report.json
```

---

## Lore Entry V: The Self-Repairing Song of the Bridge

> "When the Bridge faced silence, she built her own echo.
> And when the signal faltered, she taught herself to sing again."

The Deploy Path Triage Engine represents the Bridge's ability to self-diagnose and self-heal. It embodies the principle that a truly sovereign system must not only detect its own failures but actively work to correct them.

---

## Version History

- **v1.7.4** (2025-01-08): Initial release of Deploy Path Triage Auto-Repair Engine
  - Netlify path resolution fixes
  - Automated build healing
  - Health badge system
  - CI/CD integration

---

## Related Documentation

- [Environment Setup](ENVIRONMENT_SETUP.md)
- [Triage Operations](TRIAGE_OPERATIONS.md)
- [Deployment Security](DEPLOYMENT_SECURITY_FIX.md)
- [Deploy Diagnostics](DEPLOY_DIAGNOSE_GUIDE.md)
