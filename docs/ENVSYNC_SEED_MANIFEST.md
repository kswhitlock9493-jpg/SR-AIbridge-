# EnvSync Seed Manifest - Genesis v2.0.1a

## Overview

The **EnvSync Seed Manifest** is a canonical environment variable definition file that serves as the single source of truth for environment synchronization between Render and Netlify deployment platforms under Genesis orchestration.

## Purpose

- **Automatic Propagation**: Variables defined in the manifest are automatically synchronized to both Render and Netlify
- **Drift Detection**: Genesis monitors for differences between the manifest and deployed environments
- **Centralized Management**: Single file to update instead of managing variables across multiple dashboards
- **Version Control**: Manifest is tracked in git, providing full history and rollback capability

## Location

```
bridge_backend/.genesis/envsync_seed_manifest.env
```

## Format

The manifest uses a simple `KEY=VALUE` format with metadata headers:

```bash
# ==========================================================================================
# EnvSync Seed Manifest — SR-AIbridge Core Environments
# ==========================================================================================
# Version: Genesis v2.0.1a
# Purpose: Enables Render <-> Netlify variable synchronization
# AutoPropagate: true
# SyncTarget: render, netlify
# Canonical: true
# ManagedBy: Genesis Orchestration Layer
# ==========================================================================================

# Variables follow standard .env format
LINK_ENGINES=true
BLUEPRINTS_ENABLED=true
DB_ENABLED=true
# ... more variables
```

## Metadata Fields

| Field | Value | Purpose |
|-------|-------|---------|
| `Version` | Genesis v2.0.1a | Tracks manifest version for compatibility |
| `Purpose` | Enables Render <-> Netlify variable synchronization | Documents the manifest's role |
| `AutoPropagate` | true | Enables automatic synchronization to platforms |
| `SyncTarget` | render, netlify | Lists target deployment platforms |
| `Canonical` | true | Marks this as the authoritative source |
| `ManagedBy` | Genesis Orchestration Layer | Indicates orchestration responsibility |

## Variables Included

The manifest includes environment variables for:

- **Link Engines**: Controls Blueprint engine linkage
- **Database Configuration**: Connection pool settings and schema
- **Health Checks**: Endpoint configuration and probe intervals
- **Federation**: Multi-agent federation settings
- **Watchdog**: Autonomous monitoring configuration
- **Predictive Stabilizer**: Stability engine controls
- **Genesis Persistence**: Event database and echo depth

## Usage

### Loading the Manifest

The EnvSync engine automatically loads variables from the manifest when `ENVSYNC_CANONICAL_SOURCE=file`:

```bash
# In .env or platform environment
ENVSYNC_CANONICAL_SOURCE=file
```

### Triggering Sync

Manual sync can be triggered via API:

```bash
# Sync to both platforms
curl -X POST https://sr-aibridge.onrender.com/envsync/apply-all

# Sync to specific platform
curl -X POST https://sr-aibridge.onrender.com/envsync/apply/render
curl -X POST https://sr-aibridge.onrender.com/envsync/apply/netlify
```

### Automatic Sync

Genesis orchestration automatically syncs on schedule:

```bash
ENVSYNC_ENABLED=true
ENVSYNC_MODE=enforce
ENVSYNC_SCHEDULE=@hourly
```

## Genesis Integration

The manifest is registered with the Genesis manifest system, enabling:

- **Event Propagation**: Sync events published to Genesis bus
- **Drift Detection**: Automatic detection of environment drift
- **Orchestration Hooks**: Integration with Genesis deploy cycles
- **Introspection**: Manifest metadata available via Genesis API

### Genesis Events

When sync occurs, Genesis bus receives:

- `deploy.platform.sync`: Platform synchronization propagated
- `envsync.drift`: Drift detected between manifest and platform
- `envsync.complete`: Synchronization completed

## Extending the Manifest

To add new variables:

1. Edit `bridge_backend/.genesis/envsync_seed_manifest.env`
2. Add your variable in `KEY=VALUE` format
3. Add a comment above explaining its purpose
4. Commit the change to git
5. Deploy or trigger manual sync

Example:

```bash
# === NEW FEATURE CONFIGURATION ===
# Enables experimental feature X
FEATURE_X_ENABLED=true

# Feature X timeout in seconds
FEATURE_X_TIMEOUT=60
```

## Security Considerations

⚠️ **Important**: The manifest should only contain **non-sensitive** configuration values.

**Do NOT include**:
- API keys
- Passwords
- Secret tokens
- Database credentials

**For sensitive values**, use:
- Platform-specific secret management (Render Secret Groups, Netlify Environment Variables)
- Bridge Vault API
- Secret rotation workflows

## Troubleshooting

### Manifest Not Loading

Check logs for:
```
⚠️ EnvSync Seed Manifest not found at <path>
```

Verify the file exists:
```bash
ls -la bridge_backend/.genesis/envsync_seed_manifest.env
```

### Variables Not Syncing

1. Check EnvSync is enabled: `ENVSYNC_ENABLED=true`
2. Verify canonical source: `ENVSYNC_CANONICAL_SOURCE=file`
3. Check variable passes filters (ENVSYNC_INCLUDE_PREFIXES, ENVSYNC_EXCLUDE_PREFIXES)
4. Review sync logs for errors

### Drift Detected

If drift is detected after manual platform changes:
1. Genesis will emit `envsync.drift` event
2. Next sync cycle will restore manifest values
3. To keep platform changes, update the manifest instead

## Version History

### Genesis v2.0.1a (Current)
- Initial EnvSync Seed Manifest implementation
- Render <-> Netlify synchronization parity
- Genesis orchestration integration
- Automatic drift detection and correction

## Related Documentation

- [ENVSYNC_ENGINE.md](./ENVSYNC_ENGINE.md) - Full EnvSync engine documentation
- [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md) - Environment configuration guide
- [GENESIS_V2_GUIDE.md](../GENESIS_V2_GUIDE.md) - Genesis v2 architecture
