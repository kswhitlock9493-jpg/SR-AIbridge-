# ARIE Overview - Autonomous Repository Integrity Engine

## Introduction

ARIE (Autonomous Repository Integrity Engine) is a self-maintaining system that continuously scans, auto-fixes, audits, and manages code quality and compliance issues across the entire SR-AIbridge repository.

## Architecture

### Core Pipeline

ARIE operates through a sequential pipeline:

```
discover → analyze → plan → fix → verify → report
```

1. **Discover**: Identify files to scan based on patterns and exclusions
2. **Analyze**: Run multiple analyzers to detect issues
3. **Plan**: Create execution plans based on policy
4. **Fix**: Apply automated fixes
5. **Verify**: Validate changes through Truth Engine
6. **Report**: Generate comprehensive reports

### Components

#### 1. Core Engine (`bridge_backend/engines/arie/core.py`)

**ARIEEngine** - Main orchestrator class

**Analyzers**:
- `DatetimeDeprecatedAnalyzer` - Detects deprecated `datetime.utcnow()` calls
- `StubMarkerAnalyzer` - Finds "TODO stub" comments in generated clients
- `RouteRegistryAnalyzer` - Validates route imports and registrations
- `ImportHealthAnalyzer` - Checks for broken or overly-nested imports
- `ConfigSmellAnalyzer` - Detects ENV access without defaults
- `DuplicateFileAnalyzer` - Finds duplicate files (Parcel engine integration)
- `DeadFileAnalyzer` - Identifies unused verification scripts
- `UnusedFileAnalyzer` - Detects unused imports

**Fixers**:
- `DatetimeFixer` - Replaces `datetime.utcnow()` with `datetime.now(UTC)`
- `StubCommentFixer` - Removes stub markers
- `ImportAliasFixer` - Fixes import issues

#### 2. Models (`bridge_backend/engines/arie/models.py`)

Pydantic models for data structures:
- `Finding` - Individual integrity issue
- `Plan` - Execution plan for fixes
- `Patch` - Applied fix record
- `Rollback` - Rollback operation record
- `Summary` - Run summary report
- `PolicyType` - Fix policy enum (LINT_ONLY, SAFE_EDIT, REFACTOR, ARCHIVE)

#### 3. Routes (`bridge_backend/engines/arie/routes.py`)

FastAPI endpoints:
- `POST /api/arie/run` - Run scan/apply fixes
- `GET /api/arie/report` - Get last run report
- `POST /api/arie/rollback` - Rollback a patch
- `GET /api/arie/config` - Get configuration
- `POST /api/arie/config` - Update configuration

#### 4. Genesis Integration

**ARIEGenesisLink** (`bridge_backend/bridge_core/engines/adapters/arie_genesis_link.py`)

Subscribes to:
- `deploy.platform.success` - Triggers post-deploy scan
- `genesis.heal` (category: repo_integrity) - Apply planned fixes

Publishes:
- `arie.audit` - Scan results
- `arie.fix.intent` - Planned fixes
- `arie.fix.applied` - Applied fixes
- `arie.fix.rollback` - Rollback events
- `arie.alert` - Critical issues

#### 5. Permission Integration

**ARIEPermissionLink** (`bridge_backend/bridge_core/engines/adapters/arie_permission_link.py`)

RBAC capabilities:
- `arie:scan` - Run scans (captain+)
- `arie:fix` - Apply fixes (admiral only)
- `arie:rollback` - Rollback patches (admiral only)
- `arie:configure` - Change configuration (admiral only)

#### 6. Truth Engine Integration

**ARIETruthLink** (`bridge_backend/bridge_core/engines/adapters/arie_truth_link.py`)

Post-fix certification:
- Verifies module hashes
- Runs test matrix
- Auto-rollback on failed certification

#### 7. Cascade Integration

**ARIECascadeLink** (`bridge_backend/bridge_core/engines/adapters/arie_cascade_link.py`)

Post-fix flows:
- Re-run unit tests
- Warm caches
- Check deploy parity
- Notify EnvRecon

#### 8. Blueprint Integration

**ARIEBlueprintLink** (`bridge_backend/bridge_core/engines/adapters/arie_blueprint_link.py`)

Records structural edits:
- Route map changes
- Module ownership updates
- Engine manifest updates

## Policy Types

### LINT_ONLY
- **Description**: Report issues only, no changes
- **Use Case**: CI checks, auditing
- **Risk Level**: None

### SAFE_EDIT
- **Description**: Safe automated fixes (comments, deprecated calls)
- **Categories**: deprecated, stub, config_smell
- **Use Case**: Automated maintenance
- **Risk Level**: Low

### REFACTOR
- **Description**: Structural changes (imports, routes)
- **Categories**: deprecated, stub, import_health, route_integrity
- **Use Case**: Guided refactoring
- **Risk Level**: Medium

### ARCHIVE
- **Description**: File operations (move, delete)
- **Categories**: duplicate, dead_file
- **Use Case**: Cleanup operations
- **Risk Level**: High

## Data Flow

```
┌─────────────┐
│   Deploy    │
│  Success    │
└──────┬──────┘
       │
       v
┌─────────────┐
│    ARIE     │
│    Scan     │
└──────┬──────┘
       │
       v
┌─────────────┐     ┌──────────────┐
│  Findings   │────>│  Permission  │
└──────┬──────┘     │    Check     │
       │            └──────┬───────┘
       v                   │
┌─────────────┐           │
│    Plan     │<──────────┘
└──────┬──────┘
       │
       v
┌─────────────┐
│  Apply Fix  │
└──────┬──────┘
       │
       v
┌─────────────┐     ┌──────────────┐
│    Patch    │────>│    Truth     │
└──────┬──────┘     │ Certification│
       │            └──────┬───────┘
       v                   │
┌─────────────┐           │
│   Cascade   │<──────────┘
│    Flows    │
└─────────────┘
```

## Rollback Journal

All patches are recorded in `bridge_backend/.arie/patchlog/`:
- Each patch has a unique ID
- Stores diff, files modified, timestamp
- Enables point-in-time rollback
- Maintains certification status

## Configuration

Environment variables:

```bash
ARIE_ENABLED=true                          # Enable ARIE
ARIE_POLICY=SAFE_EDIT                     # Default policy
ARIE_AUTO_FIX_ON_DEPLOY_SUCCESS=false    # Auto-fix after deploy
ARIE_MAX_PATCH_BACKLOG=50                # Max patches to keep
ARIE_STRICT_ROLLBACK=true                # Strict rollback mode
```

## Integration Points

### With Parcel Engine
ARIE's `DuplicateFileAnalyzer` and `DeadFileAnalyzer` integrate with the repository scanner logic to detect and handle:
- Duplicate files (same content hash)
- Dead verification scripts
- Unused files

### With Genesis
Full event-driven integration for orchestration across all engines

### With Truth Engine
Certification of all fixes before marking as "final"

### With Permission Engine
RBAC enforcement for all operations

### With Cascade
Post-fix validation and cache warming

### With Blueprint
Structural change tracking and registry updates

## Best Practices

1. **Start with LINT_ONLY** - Understand issues before fixing
2. **Use SAFE_EDIT for automation** - Low-risk, high-value
3. **Review REFACTOR plans** - Structural changes need human oversight
4. **Test rollback procedures** - Ensure you can undo changes
5. **Monitor certification** - Failed certs indicate problems
6. **Check Genesis events** - Full observability of ARIE actions

## Monitoring

Watch these Genesis topics:
- `arie.audit` - Scan results
- `arie.fix.applied` - Successful fixes
- `arie.alert` - Issues requiring attention

Check patch journal:
```bash
ls -l bridge_backend/.arie/patchlog/
```

View last report:
```bash
python3 -m bridge_backend.cli.ariectl report
```
