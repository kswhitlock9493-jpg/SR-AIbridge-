# SR-AIbridge Vault

## Purpose

The Vault serves as a centralized repository for archival materials, reference scripts, and historical artifacts that support the SR-AIbridge but are not required for daily operations.

## Structure

```
vault/
├── archived_scripts/    # Test, validation, and study scripts
├── reference_sql/       # SQL patches, migrations, and maintenance scripts
├── old_configs/         # Archived configuration files and examples
├── documentation/       # Historical or reference documentation
└── README.md           # This file
```

## What Goes in the Vault?

### ✅ Include
- **Test & Validation Scripts**: Scripts used for testing, validation, and verification that are run periodically but not part of core operations
- **SQL Reference**: Database patches, migrations, and maintenance scripts
- **Configuration Archives**: Old environment configurations, deprecated settings, template variants
- **Study & Analysis**: Repository analysis scripts, diagnostics, and study tools
- **Historical Documentation**: Archived docs, summaries, and reference materials

### ❌ Exclude (Keep at Root)
- **Active Runtime Files**: Files required for application startup and operation
- **Current Configuration**: Active .env files, package files, primary configs
- **Core Documentation**: README.md, START_HERE.md, and primary guides
- **Build Tools**: Current build scripts, deployment configs

## Vault vs Backend Vault

This root-level **vault/** is for repository-wide archival and reference materials.

The **bridge_backend/vault/** contains runtime vault functionality and protocols used by the application.

They serve different purposes:
- **Root vault/**: Repository organization and archival
- **Backend vault/**: Application runtime vault features

## Usage Guidelines

### Adding to Vault
When adding files to the vault:
1. Choose the appropriate subdirectory
2. Preserve original filenames for traceability
3. Add a note to this README if the file is historically significant
4. Update .gitignore if needed (vault contents are typically tracked)

### Retrieving from Vault
Files in the vault are tracked in git and available at any time:
- Reference scripts can be run from within the vault directory
- SQL scripts can be executed as needed
- Configurations can be referenced or restored

## Integration with Bridge UI

The Bridge UI includes a **Vault Logs** tab (`/vault-logs`) which displays vault-related logs and activities from the backend vault system. This is separate from the root-level vault organization.

## Sovereign Git Mode

In Sovereign Git mode, the vault helps maintain a clean, organized repository structure while preserving all historical and reference materials. Nothing is deleted - it's simply organized for better navigation.

## Current Vault Contents

### Archived Scripts (`archived_scripts/`)
- `smoke_test_engines.py` - Smoke test for all engines
- `smoke_test_engines.sh` - Shell version of smoke tests
- `test_endpoints_full.py` - Comprehensive endpoint testing
- `validate_genesis_unified.py` - Genesis validation script
- `verify_hxo_nexus.py` - HXO Nexus verification
- `study_repo_with_engines.py` - Repository study using engines
- `run_repo_study.sh` - Shell script for repo study
- `count_loc.py` - Line of code counter
- `get_env_drift.py` - Environment configuration drift detector

### Reference SQL (`reference_sql/`)
- `init.sql` - Database initialization
- `maintenance.sql` - Database maintenance scripts
- `blueprint_partition_patch.sql` - Blueprint partition patch

### Old Configurations (`old_configs/`)
- `.env.template` - Environment template (archived)
- `.env.deploy` - Deployment environment (archived)
- `.env.envsync.example` - EnvSync example configuration
- `.env.v197f.example` - Version 1.9.7f example
- `.env.v197q.example` - Version 1.9.7q example

### Documentation (`documentation/`)
- `REPO_STUDY_REPORT.json` - Historical repository study report

---

**Vault Status:** ✅ Active  
**Organization Level:** Root Repository  
**Access:** Full read/write via git  
**Bridge UI Vault Tab:** Available at `/vault-logs`  
**Files Organized:** 19 files moved from root to vault
