# ARIE Quick Reference

## What is ARIE?

**ARIE (Autonomous Repository Integrity Engine)** is a self-maintaining system that continuously scans, auto-fixes, audits, and manages code quality issues across the SR-AIbridge repository.

## Quick Start

### Run a scan

```bash
python3 -m bridge_backend.cli.ariectl scan --dry-run --verbose
```

### Apply fixes

```bash
python3 -m bridge_backend.cli.ariectl apply --policy SAFE_EDIT --yes
```

### View last report

```bash
python3 -m bridge_backend.cli.ariectl report
```

### Rollback changes

```bash
python3 -m bridge_backend.cli.ariectl rollback --patch <patch_id>
```

## Policy Types

| Policy | Risk | What it fixes |
|--------|------|---------------|
| `LINT_ONLY` | None | Reports only, no changes |
| `SAFE_EDIT` | Low | Deprecated calls, comments, config |
| `REFACTOR` | Medium | Imports, routes (needs review) |
| `ARCHIVE` | High | Deletes duplicates, dead files |

## Analyzers

ARIE includes 8 analyzers:

1. **DatetimeDeprecatedAnalyzer** - Finds `datetime.utcnow()`
2. **StubMarkerAnalyzer** - Finds "TODO stub" comments
3. **RouteRegistryAnalyzer** - Validates route registration
4. **ImportHealthAnalyzer** - Checks for broken imports
5. **ConfigSmellAnalyzer** - Finds ENV access without defaults
6. **DuplicateFileAnalyzer** - Detects identical files
7. **DeadFileAnalyzer** - Finds unused verification scripts
8. **UnusedFileAnalyzer** - Detects unused imports

## API Endpoints

- `POST /api/arie/run` - Run scan/apply fixes
- `GET /api/arie/report` - Get last report
- `POST /api/arie/rollback` - Rollback patch
- `GET /api/arie/config` - Get configuration
- `POST /api/arie/config` - Update configuration

## Configuration

Environment variables:

```bash
ARIE_ENABLED=true                          # Enable ARIE
ARIE_POLICY=SAFE_EDIT                     # Default policy
ARIE_AUTO_FIX_ON_DEPLOY_SUCCESS=false    # Auto-fix after deploy
ARIE_MAX_PATCH_BACKLOG=50                # Max patches to keep
ARIE_STRICT_ROLLBACK=true                # Strict rollback mode
```

## Genesis Integration

ARIE publishes to:
- `arie.audit` - Scan results
- `arie.fix.intent` - Planned fixes
- `arie.fix.applied` - Applied fixes
- `arie.fix.rollback` - Rollback events
- `arie.alert` - Critical issues

ARIE subscribes to:
- `deploy.platform.success` - Triggers post-deploy scan
- `genesis.heal` - Apply fixes on demand

## RBAC Permissions

- `arie:scan` - Run scans (captain+)
- `arie:fix` - Apply fixes (admiral only)
- `arie:rollback` - Rollback patches (admiral only)
- `arie:configure` - Change config (admiral only)

## Common Use Cases

### Weekly audit

```bash
python3 -m bridge_backend.cli.ariectl scan --dry-run --json > audit_$(date +%Y%m%d).json
```

### Apply safe fixes

```bash
python3 -m bridge_backend.cli.ariectl apply --policy SAFE_EDIT --yes
```

### Check for critical issues

```bash
python3 -m bridge_backend.cli.ariectl scan --dry-run --json | jq '.findings_by_severity.critical'
```

### CI integration

```bash
# In GitHub Actions or Render
bash scripts/arie_run_ci.sh
```

## Rollback

List patches:

```bash
ls -l bridge_backend/.arie/patchlog/
```

Rollback specific patch:

```bash
python3 -m bridge_backend.cli.ariectl rollback --patch patch_<id>
```

Emergency rollback via git:

```bash
git checkout HEAD~1 -- <file_path>
```

## Test Suite

Run all ARIE tests:

```bash
cd bridge_backend
python3 -m unittest discover -s tests -p "test_arie*.py" -v
```

33 tests total:
- 16 engine tests
- 10 route tests
- 7 integration tests

## Documentation

Full docs in `/docs/`:

- `ARIE_OVERVIEW.md` - Architecture and components
- `ARIE_OPERATIONS.md` - Detailed usage guide
- `ARIE_TOPICS.md` - Genesis event reference
- `ARIE_SECURITY.md` - Security model and RBAC

## Current Status

Latest scan results (production):
- **335 findings** across repository
- 23 MEDIUM (deprecated datetime)
- 312 LOW (unused imports, config smells, etc.)
- 1 duplicate file detected

## Troubleshooting

**ARIE not finding issues?**
```bash
# Check if enabled
echo $ARIE_ENABLED
```

**Fixes not applying?**
```bash
# Ensure you're not in dry-run mode
python3 -m bridge_backend.cli.ariectl apply --policy SAFE_EDIT
# (don't use --dry-run flag)
```

**Permission denied?**
- For CLI: No restrictions by default
- For API: Authenticate as admiral for fix/rollback

## Support

- Issues: File in GitHub
- Logs: Check `bridge_backend/logs/`
- Patches: `bridge_backend/.arie/patchlog/`
- Genesis events: Monitor `arie.*` topics

---

**Version**: v1.9.6m  
**Status**: Production Ready ✅  
**Tests**: 33/33 passing ✅
