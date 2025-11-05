# v1.9.6r Quick Reference - Chimera Preflight + Autonomous Deploy Healing

## Overview

Version 1.9.6r introduces **Chimera Preflight Engine** and **Autonomous Deploy Healing** to eliminate Netlify preview failures through pre-validation and self-healing.

## What's New

### 1. Chimera Preflight Engine

Located in `bridge_backend/engines/chimera/`, this lightweight engine generates and validates Netlify deploy artifacts:

- `_headers` - Security headers configuration
- `_redirects` - URL rewrite rules  
- `netlify.toml` - Build configuration

**Key Features:**
- Auto-detects publish directory
- Validates syntax locally before deploy
- Publishes Genesis events for observability
- Integrates with ARIE for auto-repair

### 2. GitHub Actions Deploy Preview Workflow

New workflow: `.github/workflows/deploy_preview.yml`

**Flow:**
1. PR opened/updated → Chimera preflight runs
2. Deploy artifacts generated and validated
3. If changed, artifacts committed to PR
4. Netlify preview consumes validated config
5. If Netlify still fails → ARIE auto-heals

### 3. Engine Defaults (All ON)

The following engines are now **enabled by default** via environment flags:

```bash
ARIE_ENABLED=true
ENVRECON_ENABLED=true  
STEWARD_ENABLED=true
CHIMERA_ENABLED=true
HXO_ENABLED=true
```

Override by setting environment variables to `false`.

## Usage

### Manual Preflight

```bash
# Run preflight validation
python -m bridge_backend.cli.chimeractl preflight

# With JSON output
python -m bridge_backend.cli.chimeractl preflight --json

# Specify path
python -m bridge_backend.cli.chimeractl preflight --path /path/to/project
```

### API Endpoint

```bash
POST /api/chimera/preflight
```

Returns:
```json
{
  "publish": "bridge-frontend/dist",
  "status": "ok"
}
```

### Python API

```python
from pathlib import Path
from bridge_backend.engines.chimera.core import ChimeraEngine
import asyncio

async def run_preflight():
    engine = ChimeraEngine(Path("."))
    result = await engine.preflight()
    print(f"Publish dir: {result['publish']}")

asyncio.run(run_preflight())
```

## Genesis Events

Chimera publishes these events to the Genesis bus:

- `chimera.preflight.start` - Preflight validation started
- `chimera.preflight.ok` - Validation succeeded
- `chimera.preflight.fail` - Validation failed
- `chimera.deploy.heal.intent` - Healing triggered
- `chimera.deploy.heal.applied` - Healing completed
- `deploy.preview.requested` - Preview deploy requested
- `deploy.preview.failed` - Preview deploy failed

## Auto-Healing

When a Netlify preview fails:

1. Genesis bus emits `deploy.preview.failed` event
2. ARIE handler `on_preview_failed()` triggers
3. Chimera regenerates deploy artifacts with safe defaults
4. Git commits and pushes fixes (if git is available)
5. Preview redeploys with fixed configuration

## Configuration

### Environment Variables

```bash
# Enable/disable Chimera (default: true)
CHIMERA_ENABLED=true

# Netlify credentials (optional, for direct API integration)
NETLIFY_AUTH_TOKEN=<token>
NETLIFY_SITE_ID=<site-id>
```

### Publish Directory Detection

Chimera auto-detects the publish directory in this order:

1. `frontend/dist`
2. `frontend/build`
3. `apps/web/out`
4. `dist`
5. `build`
6. `bridge-frontend/dist`

Defaults to `frontend/build` if none exist.

## Testing

Run Chimera tests:

```bash
python -m pytest bridge_backend/tests/test_chimera_preflight.py -v
```

All 7 tests should pass:
- ✅ test_chimera_preflight_generates_files
- ✅ test_chimera_headers_format
- ✅ test_chimera_redirects_format
- ✅ test_chimera_netlify_toml_format
- ✅ test_chimera_detect_publish_dir
- ✅ test_chimera_heal_after_failure
- ✅ test_chimera_models

## Files Added

```
bridge_backend/engines/chimera/
├── __init__.py
├── core.py
├── models.py
├── routes.py
└── preflight/
    ├── __init__.py
    └── netlify_config.py

bridge_backend/bridge_core/engines/adapters/
└── chimera_genesis_link.py

bridge_backend/tests/
└── test_chimera_preflight.py

.github/workflows/
└── deploy_preview.yml
```

## Modified Files

- `bridge_backend/config.py` - Added engine enable flags
- `bridge_backend/genesis/bus.py` - Added Chimera topics
- `bridge_backend/bridge_core/engines/adapters/genesis_link.py` - Registered Chimera
- `bridge_backend/cli/chimeractl.py` - Added preflight command
- `bridge_backend/engines/arie/core.py` - Added preview failure handler
- `bridge_backend/engines/steward/core.py` - Added publish dir detection

## Integration Points

### With ARIE
ARIE receives `deploy.preview.failed` events and triggers Chimera to regenerate artifacts.

### With Genesis Bus
All Chimera operations publish events for observability and coordination.

### With Steward  
Steward can use `detect_publish_dir()` for deploy path verification.

### With EnvRecon
EnvRecon ensures environment variables stay in sync across platforms.

## Troubleshooting

### Preflight fails with missing publish dir
Check that at least one of the expected directories exists, or the workflow will default to `frontend/build`.

### GitHub Actions workflow doesn't commit
Ensure the workflow has `contents: write` permission and the bot has access to push to the branch.

### Genesis events show as invalid
Make sure Genesis bus topics are registered. Run the application normally to initialize Genesis.

## Breaking Changes

**None.** All additions are additive and gated behind environment flags that default to `true`.

## Next Steps

1. Verify the workflow runs on your next PR
2. Check Genesis events in introspection logs
3. Monitor auto-healing behavior in failed previews
4. Customize security headers in `preflight/netlify_config.py` if needed

---

**Version:** 1.9.6r  
**Codename:** Chimera Pre-flight + Autonomous Deploy Healing  
**Status:** ✅ Ready for deployment
