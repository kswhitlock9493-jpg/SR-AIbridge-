# Build Triage & Auto-Repair Engine (v1.7.9)

## What it does
- Enforces Node 20 (Netlify + local)
- Ensures devDependencies are always installed
- Calms secret-scan noise (log-level only)
- Scans for inline-looking secrets (warns)
- Auto-retries npm install with scoped mirrors

## Run locally
```bash
cd bridge-frontend
python3 scripts/build_triage.py
npm run build
```

## CI

`.github/workflows/build_preflight.yml` runs triage on PRs and pushes.

## Diagnostics

Output: `bridge_backend/diagnostics/build_triage_report.json`

Forwarded to Healer-Net by your existing diagnostics pipeline.

## Components

### 1. `.nvmrc`
Locks Node version to 20 for local development and CI environments that respect this file.

### 2. `package.json` Updates
- **engines**: Enforces Node 20 (`>=20 <21`) and npm 10+
- **prebuild**: Runs `build_triage.py` before every build
- **postbuild**: Confirms successful build completion
- **ci:install**: Custom install command that forces devDependencies installation even in production mode

### 3. `netlify.toml` Enhancements
- **Monorepo-safe paths**: Explicit `base`, `publish`, and `functions` directories
- **NODE_VERSION**: Set to "20" for Netlify build environment
- **NPM_CONFIG_PRODUCTION**: Set to "false" to ensure devDependencies install
- **SECRETS_SCAN_LOG_LEVEL**: Set to "error" to reduce noise while keeping scanner active
- **Healer-Net integration**: AUTO_REPAIR_MODE, BRIDGE_HEALTH_REPORT, DIAGNOSTIC_KEY, CONFIDENCE_MODE
- **Build image hint**: Ensures Node 20 image is used

### 4. Build Triage Sentinel (`scripts/build_triage.py`)

Pre-flight checks before every build:

**Node Version Enforcement**
- Sets `NODE_VERSION=20` environment variable
- Creates/validates `.nvmrc` file
- Prevents accidental Node 22+ usage

**DevDependencies Guarantee**
- Forces `NPM_CONFIG_PRODUCTION=false`
- Ensures Vite and build tools are available

**Registry Resilience**
- First attempts: `npm ci --no-audit --prefer-offline`
- On registry errors (E404, ENOTFOUND, ECONNRESET): Falls back to mirror configuration
- Second attempt: Retry with enhanced registry settings

**Secret Leak Detection**
- Scans `.js`, `.map`, `.html` files in source and dist
- Detects patterns like `api_key=`, `secret=`, `token=`
- Warns but doesn't fail build (Netlify scanner still active)

**Diagnostic Reporting**
- Writes JSON report to `bridge_backend/diagnostics/build_triage_report.json`
- Includes: node enforcement status, install attempts, detected leaks

### 5. Registry Repair Script (`scripts/repair_npm_registry.sh`)

Configures npm for resilient installs:
- Disables audit and fund messages
- Sets explicit registries for scoped packages (@netlify, @vitejs, @rollup)
- Configures retry behavior (4 attempts, exponential backoff)
- Increases timeout thresholds

### 6. Functions Sanity Check (`netlify/functions/hello.ts`)

Minimal serverless function that:
- Confirms functions directory exists and is bundled
- Provides testable endpoint at `/.netlify/functions/hello`
- Returns `{ ok: true, msg: "hello from functions" }`

### 7. CI Preflight Workflow (`.github/workflows/build_preflight.yml`)

Automated validation on every PR and push:
- Sets up Node 20 and Python 3.11
- Runs build triage script
- Uploads diagnostic report as artifact
- Catches issues before Netlify deployment

## Report Format

```json
{
  "node_enforced_20": true,
  "devDependencies_forced": true,
  "install": {
    "attempts": 1,
    "mirror": false,
    "status": "ok"
  },
  "inline_secret_leaks_detected": 0,
  "leak_paths": []
}
```

## What This Fixes

### Node Engine Mismatch
**Before**: Netlify might pick Node 22, project expects Node 20
**After**: Triple enforcement via `.nvmrc`, `engines`, and `NODE_VERSION`

### Missing DevDependencies
**Before**: `NODE_ENV=production` causes Netlify to skip devDependencies
**After**: `NPM_CONFIG_PRODUCTION=false` forces full install

### npm Registry Failures
**Before**: E404, ENOTFOUND errors cause build failures
**After**: Auto-retry with enhanced registry configuration

### Secret Scan False Positives
**Before**: Build fails on benign patterns in vendor files
**After**: Scanner active but at error level; our sentinel pre-warns

### Monorepo Path Drift
**Before**: Inconsistent base/publish/functions paths
**After**: Explicit paths prevent Netlify confusion

## Integration with Healer-Net

The Build Triage Engine integrates with the existing Healer-Net diagnostic network:

1. Triage report written to `bridge_backend/diagnostics/build_triage_report.json`
2. Healer-Net probe aggregates this with other subsystem reports
3. Unified health status displayed in Bridge UI
4. Auto-repair events logged to diagnostic timeline

## Troubleshooting

### Triage Script Fails with Python Error
Ensure Python 3.7+ is available:
```bash
python3 --version
```

### npm ci Still Fails After Mirror Fallback
Check registry connectivity:
```bash
npm config get registry
npm ping
```

### Functions Not Deploying
Verify functions path in `netlify.toml`:
```toml
functions = "bridge-frontend/netlify/functions"
```

### Secret Leaks Detected in Report
Review `leak_paths` in report. Common false positives:
- Vendor/library files with example code
- Test fixtures with dummy credentials
- Add legitimate files to suppression list if needed

## Local Testing

```bash
# Test triage script
cd bridge-frontend
python3 scripts/build_triage.py

# Check report
cat ../bridge_backend/diagnostics/build_triage_report.json

# Test registry repair
bash scripts/repair_npm_registry.sh
npm config list

# Test build
npm run build

# Test functions locally
netlify dev
curl http://localhost:8888/.netlify/functions/hello
```

## Deployment Checklist

Before merging v1.7.9:
- [x] `.nvmrc` created with "20"
- [x] `package.json` engines updated to `>=20 <21`
- [x] `package.json` scripts include prebuild, postbuild, ci:install
- [x] `cross-env` added to devDependencies
- [x] `netlify.toml` updated with monorepo paths
- [x] `netlify.toml` includes Healer-Net environment variables
- [x] Build triage script created and executable
- [x] Registry repair script created and executable
- [x] Hello function created in correct path
- [x] Build preflight workflow created
- [x] Documentation complete

## Future Enhancements

Planned for v1.8.x:
- [ ] Automated npm package audit and security patching
- [ ] Build performance metrics tracking
- [ ] Dependency version drift detection
- [ ] Automatic rollback on failed health checks
- [ ] Integration with alerting systems (Slack, Discord)
- [ ] Historical build triage analytics

## Related Documentation

- [HEALER_NET.md](HEALER_NET.md) - Healer-Net Diagnostic Network
- [TRIAGE_OPERATIONS.md](TRIAGE_OPERATIONS.md) - Triage Operations Handbook
- [DEPLOYMENT_AUTOMATION.md](DEPLOYMENT_AUTOMATION.md) - Deploy Path Triage
- [TRIAGE_FEDERATION.md](TRIAGE_FEDERATION.md) - Triage Federation v1.7.5

## Lore Entry: The Self-Correcting Bridge

> "Before the Bridge could build itself anew,  
> it learned to examine its own foundation.  
> And in that examination, it found the power  
> to heal what had not yet broken."

The Build Triage & Auto-Repair Engine represents the Bridge's ability to detect and correct issues before they manifest as failures. It embodies the principle of proactive resilience—not waiting for problems to occur, but preventing them through continuous self-examination and automatic correction.

---

**Version**: 1.7.9  
**Last Updated**: 2024  
**Maintainer**: SR-AIbridge Team
