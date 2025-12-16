# ARIE Operations Guide

## Installation and Setup

### Prerequisites

ARIE is built into the SR-AIbridge system and requires no additional dependencies beyond the standard Python requirements.

### Enable ARIE

Add to your `.env` file:

```bash
ARIE_ENABLED=true
ARIE_POLICY=SAFE_EDIT
```

### Verify Installation

```bash
python3 -m bridge_backend.cli.ariectl scan --dry-run
```

## CLI Usage

### ariectl - ARIE Command Line Interface

#### Scan Repository

Run a read-only scan:

```bash
python3 -m bridge_backend.cli.ariectl scan --dry-run
```

Scan with verbose output:

```bash
python3 -m bridge_backend.cli.ariectl scan --dry-run --verbose
```

Scan specific paths:

```bash
python3 -m bridge_backend.cli.ariectl scan --paths bridge_backend/engines/ --dry-run
```

Get JSON output:

```bash
python3 -m bridge_backend.cli.ariectl scan --dry-run --json > scan_report.json
```

#### Apply Fixes

Apply SAFE_EDIT fixes:

```bash
python3 -m bridge_backend.cli.ariectl apply --policy SAFE_EDIT
```

Apply without confirmation (CI mode):

```bash
python3 -m bridge_backend.cli.ariectl apply --policy SAFE_EDIT --yes
```

Apply REFACTOR fixes (higher risk):

```bash
python3 -m bridge_backend.cli.ariectl apply --policy REFACTOR
```

#### Rollback Changes

Rollback a specific patch:

```bash
python3 -m bridge_backend.cli.ariectl rollback --patch patch_2025-10-11T20:30:00_abc123
```

Force rollback (skip safety checks):

```bash
python3 -m bridge_backend.cli.ariectl rollback --patch <patch_id> --force --yes
```

#### View Reports

Get last run report:

```bash
python3 -m bridge_backend.cli.ariectl report
```

Get report as JSON:

```bash
python3 -m bridge_backend.cli.ariectl report --json
```

## API Usage

### Run Scan

```bash
curl -X POST http://localhost:8000/api/arie/run \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "SAFE_EDIT",
    "dry_run": true,
    "apply": false
  }'
```

### Apply Fixes

```bash
curl -X POST http://localhost:8000/api/arie/run \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "SAFE_EDIT",
    "dry_run": false,
    "apply": true
  }'
```

### Get Last Report

```bash
curl http://localhost:8000/api/arie/report
```

### Rollback Patch

```bash
curl -X POST http://localhost:8000/api/arie/rollback \
  -H "Content-Type: application/json" \
  -d '{
    "patch_id": "patch_2025-10-11T20:30:00_abc123",
    "force": false
  }'
```

### Get Configuration

```bash
curl http://localhost:8000/api/arie/config
```

### Update Configuration

```bash
curl -X POST http://localhost:8000/api/arie/config \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "policy": "SAFE_EDIT",
    "auto_fix_on_deploy": false,
    "max_patch_backlog": 50,
    "strict_rollback": true
  }'
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/arie.yml`:

```yaml
name: ARIE Integrity Check

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  arie-check:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run ARIE scan (PR)
        if: github.event_name == 'pull_request'
        run: |
          python3 -m bridge_backend.cli.ariectl scan --dry-run --verbose
      
      - name: Run ARIE with fix (main)
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        env:
          ARIE_AUTO_FIX_ON_DEPLOY_SUCCESS: 'true'
        run: |
          bash scripts/arie_run_ci.sh
```

### Render Deploy Hook

Add to `render.yaml`:

```yaml
services:
  - type: web
    name: sr-aibridge
    env: python
    buildCommand: "pip install -r requirements.txt"
    preDeployCommand: "python3 -m bridge_backend.cli.ariectl scan --dry-run"
    # Optional: Auto-fix on deploy (requires admiral token)
    # postDeployCommand: "bash scripts/arie_run_ci.sh"
```

### Manual CI Script

```bash
# Read-only check
bash scripts/arie_run_ci.sh

# With auto-fix (set env vars first)
export ARIE_AUTO_FIX_ON_DEPLOY_SUCCESS=true
export ARIE_ADMIRAL_TOKEN=<your-token>
bash scripts/arie_run_ci.sh
```

## Rollback Procedures

### List Available Patches

```bash
ls -l bridge_backend/.arie/patchlog/
```

### Inspect Patch Details

```bash
cat bridge_backend/.arie/patchlog/patch_2025-10-11T20:30:00_abc123.json
```

### Rollback Steps

1. **Identify the patch to rollback**:
   ```bash
   python3 -m bridge_backend.cli.ariectl report
   ```

2. **Review patch details**:
   ```bash
   cat bridge_backend/.arie/patchlog/<patch_id>.json
   ```

3. **Perform rollback**:
   ```bash
   python3 -m bridge_backend.cli.ariectl rollback --patch <patch_id>
   ```

4. **Verify rollback**:
   ```bash
   git status
   git diff
   ```

5. **Test application**:
   ```bash
   python3 -m pytest bridge_backend/tests/
   ```

### Emergency Rollback

If ARIE rollback fails, use git:

```bash
# Revert specific files
git checkout HEAD~1 -- <file_path>

# Or revert entire commit
git revert <commit_hash>
```

## Policy Selection Guide

### When to use LINT_ONLY

- **CI/CD checks** - Validate code without changes
- **Auditing** - Assess technical debt
- **Discovery** - Find issues before planning fixes

### When to use SAFE_EDIT

- **Automated maintenance** - Safe, low-risk fixes
- **Deprecated API cleanup** - Replace old patterns
- **Comment cleanup** - Remove stubs and TODOs
- **Default policy** - Good for regular operation

### When to use REFACTOR

- **Import reorganization** - Fix broken imports
- **Route updates** - Update registration
- **Structural changes** - Requires review
- **Manual oversight recommended**

### When to use ARCHIVE

- **Cleanup operations** - Remove duplicates
- **Dead code removal** - Delete unused files
- **High risk** - Always review before applying
- **Backup recommended**

## Troubleshooting

### ARIE not finding issues

Check configuration:
```bash
python3 -m bridge_backend.cli.ariectl report
```

Verify enabled:
```bash
echo $ARIE_ENABLED
```

### Fixes not applying

Check permissions:
- Ensure you have `arie:fix` capability
- For API: Authenticate as admiral
- For CLI: No restrictions by default

Check if dry_run is enabled:
```bash
python3 -m bridge_backend.cli.ariectl apply --policy SAFE_EDIT
# Make sure to NOT use --dry-run flag
```

### Rollback failing

Check if patch exists:
```bash
ls bridge_backend/.arie/patchlog/<patch_id>.json
```

Try force rollback:
```bash
python3 -m bridge_backend.cli.ariectl rollback --patch <patch_id> --force
```

Use git fallback:
```bash
git checkout HEAD~1 -- <file_path>
```

### Permission denied

For API operations, ensure you have the right capability:
- `arie:scan` - captain+ 
- `arie:fix` - admiral only
- `arie:rollback` - admiral only
- `arie:configure` - admiral only

### Certification failures

If Truth Engine fails certification:
1. Check logs for specific errors
2. ARIE will auto-rollback
3. Review the failed patch details
4. Fix underlying issues manually
5. Re-run ARIE

## Monitoring and Observability

### Genesis Events

Subscribe to ARIE topics:

```python
from bridge_backend.genesis.bus import bus

bus.subscribe("arie.audit", lambda evt: print(f"Audit: {evt}"))
bus.subscribe("arie.fix.applied", lambda evt: print(f"Fix: {evt}"))
bus.subscribe("arie.alert", lambda evt: print(f"Alert: {evt}"))
```

### Patch Journal

```bash
# Count patches
ls bridge_backend/.arie/patchlog/ | wc -l

# Recent patches
ls -lt bridge_backend/.arie/patchlog/ | head -10

# Patch sizes
du -sh bridge_backend/.arie/patchlog/*
```

### Health Checks

```bash
# Run scan and check exit code
python3 -m bridge_backend.cli.ariectl scan --dry-run
echo $?  # Should be 0

# Check for critical issues
python3 -m bridge_backend.cli.ariectl scan --json | jq '.findings_by_severity.critical'
```

## Best Practices

1. **Regular scans** - Run weekly in LINT_ONLY mode
2. **Review before apply** - Always scan before applying fixes
3. **Test after fixes** - Run test suite after ARIE changes
4. **Monitor Genesis** - Watch for arie.alert events
5. **Backup before ARCHIVE** - Always backup before file operations
6. **Incremental fixes** - Apply fixes in small batches
7. **Review certifications** - Check Truth Engine results
8. **Document rollbacks** - Keep notes on why rollbacks occurred
9. **Update policies** - Adjust based on experience
10. **Integrate with CI** - Make ARIE part of your pipeline
