# BCSE v2 - Sovereign Autocorrect Engine

## Overview

BCSE v2 (Bridge Code Super-Engine v2) is an advanced sovereign autocorrect engine that provides:

- **Controlled Patch Pipeline**: Generate patches, review them, and apply them manually
- **Production Readiness Verification**: Comprehensive pre-deployment checks
- **Placeholder Detection**: Automatically detect unsafe placeholder code
- **Localhost Rewriter**: Convert localhost references to Forge Dominion endpoints
- **Safe Defaults**: All potentially destructive operations require explicit opt-in

## Architecture

```
BCSE Detects → Generates Patch → Writes Patch to /bcse_autofixes → Human Approves → BCSE Applies → Runtime Certifies → Commit / Deploy
```

### Core Principles

1. **No guessing** - All changes are deterministic and based on rules
2. **No rewrites** - Only surgical patches, never full file replacements
3. **No unsafe hallucination patches** - Human review required for all changes
4. **Controlled, Reversible, Auditable** - Every change is tracked and signed
5. **Sovereign** - All configuration flows from Forge Dominion

## Commands

### Basic Quality Commands

```bash
# Show available commands
make help

# Run comprehensive quality analysis
make analyze

# Auto-fix style issues (black, ruff)
make fix

# Run tests with coverage
make test

# Show all quality gates
make gates
```

### BCSE v2 Commands

#### `make improve`

Apply safe AST transforms to code. **Disabled by default** to prevent unwanted changes.

```bash
make improve
```

**Output**:
```
⚠️  BCSE improve command is available but disabled by default.
    AST transforms can make unwanted changes.
    For style fixes, use: make fix
    For targeted improvements, review and edit code manually.
```

#### `make rewrite`

Scan for localhost references and show what would be rewritten to Forge Dominion endpoints.

**Dry-run mode** (default):
```bash
FORGE_DOMINION_ROOT=https://your-forge.example.com make rewrite
```

**Output**:
```
🔍 Scanning for localhost references (dry run mode)...
    Target: https://your-forge.example.com
📝 Would rewrite: bridge_backend/main.py
📝 Would rewrite: bridge_backend/config.py
...
✅ Found 15 file(s) with localhost references.
    To apply changes, set environment variable BCSE_REWRITE_APPLY=true
```

**Apply mode** (actually modifies files):
```bash
FORGE_DOMINION_ROOT=https://your-forge.example.com BCSE_REWRITE_APPLY=true make rewrite
```

#### `make prove`

Run full production readiness proof including:

1. Frontend build
2. Environment variable validation
3. Placeholder/stub detection
4. Backend health check (if not in CI)
5. CORS configuration validation

```bash
ENVIRONMENT=production \
CORS_ALLOW_ALL=false \
DEBUG=false \
ALLOWED_ORIGINS=https://sr-aibridge.netlify.app \
FORGE_DOMINION_ROOT=https://your-forge.example.com \
make prove
```

**Success Output**:
```
============================================================
🜂 BCSE Production Proof
============================================================

▶ Building frontend...
✅ Frontend build succeeded

▶ Running production checks...
✅ No placeholder patterns detected

▶ Checking CORS configuration...

============================================================
✅ Production proof passed
============================================================
```

#### `make review-patches`

List all pending patches in the review queue.

```bash
make review-patches
```

#### `make apply-patches`

Apply all approved patches from the `bcse_autofixes/` directory.

```bash
make apply-patches
```

## Modules

### Placeholder Detection (`bridge_tools/bcse/placeholders.py`)

Detects unsafe patterns in code:

- `TODO`, `FIXME`, `TBD` comments
- `NotImplementedError` exceptions
- Mock/stub code
- Dummy credentials
- Localhost URLs
- Safe mode flags

**Usage**:
```python
from bridge_tools.bcse.placeholders import scan

hits = scan(".")
for file, line, snippet in hits:
    print(f"{file}:{line} :: {snippet}")
```

### Production Check (`bridge_tools/bcse/prodcheck.py`)

Validates production environment:

- ✅ `DEBUG=false`
- ✅ `CORS_ALLOW_ALL=false`
- ✅ `ALLOWED_ORIGINS` contains HTTPS URLs
- ✅ `FORGE_DOMINION_ROOT` is set
- ✅ No placeholder patterns detected
- ✅ Backend health endpoint responds

### Localhost Rewriter (`bridge_tools/bcse/rewriters.py`)

Converts localhost references to Forge endpoints:

```python
from bridge_tools.bcse.rewriters import rewrite_localhost_to_forge

# Dry run (default)
changed = rewrite_localhost_to_forge(["bridge_backend"], dry_run=True)

# Apply changes
changed = rewrite_localhost_to_forge(["bridge_backend"], dry_run=False)
```

### Patch Generation (`bridge_tools/bcse/autofix/`)

Generate, review, and apply patches:

```python
from bridge_tools.bcse.autofix import generate_patch, apply_patch

# Generate patch
old_content = "x = 1"
new_content = "x = 2"
patch = generate_patch(old_content, new_content, "test.py")

# Apply patch
apply_patch("test.patch", dry_run=True)  # Check if can apply
apply_patch("test.patch", dry_run=False)  # Actually apply
```

## CI/CD Integration

### GitHub Actions Workflow

The `bridge-proof.yml` workflow runs on every push/PR to main:

```yaml
name: ✅ Bridge Production Proof
on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  prove:
    runs-on: ubuntu-latest
    env:
      FORGE_DOMINION_ROOT: ${{ secrets.FORGE_DOMINION_ROOT }}
      DEBUG: "false"
      CORS_ALLOW_ALL: "false"
      ALLOWED_ORIGINS: "https://sr-aibridge.netlify.app"
    steps:
      - uses: actions/checkout@v4
      - name: Production Proof
        run: python -m bridge_tools.bcse.cli prove
```

### Required Secrets

- `FORGE_DOMINION_ROOT` - Your Forge Dominion endpoint
- `DOMINION_SEAL` - Optional signature for patches

## Environment Variables

### Production Proof Variables

- `ENVIRONMENT` - Set to `production` for production checks
- `DEBUG` - Must be `false` for production
- `CORS_ALLOW_ALL` - Must be `false` for production
- `ALLOWED_ORIGINS` - Comma-separated HTTPS origins
- `FORGE_DOMINION_ROOT` - Forge Dominion endpoint URL

### BCSE Control Variables

- `BCSE_REWRITE_APPLY` - Set to `true` to actually apply localhost rewrites
- `DOMINION_SEAL` - Signature added to generated patches (defaults to `Σ–DEV–UNSIGNED`)

## Safety Features

### 1. Dry-Run by Default

The `rewrite` command runs in dry-run mode unless explicitly enabled:

```bash
# Safe - only shows what would change
make rewrite

# Dangerous - actually modifies files
BCSE_REWRITE_APPLY=true make rewrite
```

### 2. Improve Command Disabled

The `improve` command is disabled by default to prevent unwanted AST transforms:

```bash
# Shows warning, makes no changes
make improve
```

### 3. Human-in-the-Loop

All patches must be reviewed and explicitly approved before application:

1. Generate patch → `bcse_autofixes/`
2. Review with `make review-patches`
3. Approve and apply with `make apply-patches`

### 4. Signature Tracking

All patches include a Dominion signature for traceability:

```patch
--- a/test.py
+++ b/test.py
@@ -1,1 +1,1 @@
-old line
+new line
# Dominion-Signature: Σ–DEV–UNSIGNED
```

## Testing

Run the BCSE v2 test suite:

```bash
pytest tests/test_bcse_v2.py -v
```

**Test Coverage**:
- ✅ Placeholder detection
- ✅ Refactor module
- ✅ Production checks
- ✅ Localhost rewriter
- ✅ Patch generation
- ✅ Patch review
- ✅ CORS validation

## Comparison with Copilot

| Feature | Copilot | BCSE v2 |
|---------|---------|---------|
| Rewrite code | ✅ Yes (full rewrites) | ✅ Yes (surgical patches) |
| Improve quality | ⚠️ Unverified | ✅ Objectively measurable |
| Escape placeholder mode | ❌ No | ✅ Yes (certified runtime) |
| Prevent AI chaos | ❌ No | ✅ Yes (patch-based + review) |
| Sovereign architecture | ❌ No | ✅ Yes (Forge Dominion) |

## Production Deployment Checklist

Before deploying to production, ensure:

- [ ] `make prove` passes locally
- [ ] `bridge-proof.yml` CI passes
- [ ] No placeholder patterns detected
- [ ] All environment variables set correctly
- [ ] Frontend builds successfully
- [ ] Backend health check responds
- [ ] CORS configured with HTTPS origins only
- [ ] No localhost references in code

## Troubleshooting

### `make prove` fails with "FORGE_DOMINION_ROOT must be set"

**Solution**: Set the environment variable:
```bash
export FORGE_DOMINION_ROOT=https://your-forge.example.com
make prove
```

### `make rewrite` finds no files

**Solution**: Ensure `FORGE_DOMINION_ROOT` is set:
```bash
FORGE_DOMINION_ROOT=https://your-forge.example.com make rewrite
```

### Backend health check fails

**Solution**: Check that FastAPI can start:
```bash
cd bridge_backend
python main.py
```

### Placeholder patterns detected

**Solution**: Review and fix the identified issues:
```bash
python -m bridge_tools.bcse.cli gates
# Review the output and fix flagged patterns
```

## Best Practices

1. **Always run `make prove` before deployment**
2. **Review patches before applying** - Use `make review-patches`
3. **Use dry-run mode first** - Test commands safely
4. **Keep FORGE_DOMINION_ROOT secure** - Use secrets management
5. **Run tests frequently** - `pytest tests/test_bcse_v2.py`
6. **Check CI status** - Ensure `bridge-proof.yml` passes

## License

This is part of the SR-AIbridge project and follows the project's license.
