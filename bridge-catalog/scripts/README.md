# Scripts Directory

This directory contains utility scripts for SR-AIbridge operations, validation, and maintenance.

## 🔍 Full System Scan

### `run_full_scan.py` - Comprehensive System Check ⭐

Runs a complete scan of all critical infrastructure components including:
- Quantum Dominion Security (pre-deployment orchestrator)
- API Triage (endpoint health checks)
- Preflight checks (Netlify guard, integrity)
- Umbra Triage (issue tracking and auto-healing)
- Build Triage (Netlify build validation)
- Endpoint API Sweep (route analysis)
- Environment Parity Guard (environment drift detection)
- Runtime Triage (Render health checks)

**Usage:**
```bash
# Run full scan with progress output
python3 scripts/run_full_scan.py

# Run quietly (just show pass/fail results)
python3 scripts/run_full_scan.py --quiet

# Output results as JSON
python3 scripts/run_full_scan.py --json

# Set custom timeout (default: 60s)
python3 scripts/run_full_scan.py --timeout 120
```

**Output:**
- Console summary of all checks
- Detailed JSON report saved to `bridge_backend/diagnostics/full_scan_report.json`

**Exit Codes:**
- `0` - All checks passed
- `1` - One or more checks failed

---

## 🔐 Validation & Security

### `validate_env_setup.py`
Validates environment variable configuration across all environment files.

### `validate_netlify.py`
Validates Netlify configuration and deployment settings.

### `validate_envsync_manifest.py`
Validates the EnvSync manifest for consistency and completeness.

### `integrity_audit.py`
Performs integrity audits on critical system components.

### `validate_copilot_env.py`
Validates GitHub Copilot environment configuration.

---

## 🌐 Netlify Operations

### `netlify_build.sh`
Builds the frontend for Netlify deployment.

### `netlify_rollback.py`
Rolls back Netlify deployment to a previous version.

### `repair_netlify_env.py`
Repairs Netlify environment configuration issues.

### `verify_netlify_build.py`
Verifies Netlify build artifacts and configuration.

### `synthesize_netlify_artifacts.py`
Synthesizes Netlify artifacts for testing.

---

## 🧹 Maintenance & Cleanup

### `comprehensive_repo_scan.py`
Scans repository for duplicates, dead files, and cleanup opportunities.

### `repo_cleanup.py`
Performs repository cleanup based on scan results.

### `prune_diagnostics.py`
Prunes old diagnostic reports and logs.

### `clean_stub_todos.py`
Cleans up stub TODO comments from code.

### `fix_deprecated_datetime.py`
Fixes deprecated datetime usage for Python 3.12+ compatibility.

---

## 🔄 Environment & Parity

### `check_env_parity.py`
Checks environment variable parity across deployment platforms.

### `scan_manual_env_vars.py`
Scans for environment variables requiring manual configuration.

---

## 🛡️ Security & Firewall

### `firewall_watchdog.py`
Monitors and manages firewall rules and network policies.

---

## 🧪 Verification Scripts

### `verify_autonomy_node.py`
Verifies autonomy node configuration and health.

### `verify_reflex_loop.py`
Verifies reflex loop integration and functionality.

### `verify_umbra_lattice.py`
Verifies Umbra lattice triage mesh.

---

## 📊 Reporting

### `report_bridge_event.py`
Reports events to the bridge diagnostics system.

---

## 🚀 Deployment & Build

### `arie_run_ci.sh`
Runs ARIE continuous integration checks.

### `migrate_workflows_to_forge.sh`
Migrates GitHub workflows to use Forge Dominion.

### `start.sh`
Generic start script for services.

---

## 🌱 Bootstrap & Seeding

### `seed_bootstrap.py`
Seeds initial bootstrap data for the system.

---

## 📝 EnvSync

### `view_envsync_manifest.py`
Views the current EnvSync manifest configuration.

---

## 📖 Usage Guidelines

### Running Scripts

Most scripts can be run directly:
```bash
python3 scripts/script_name.py [options]
```

Shell scripts:
```bash
./scripts/script_name.sh
```

### Common Patterns

**Validation scripts** typically exit with:
- `0` - Validation passed
- `1` - Validation failed

**Cleanup scripts** typically:
- Show what will be cleaned
- Require confirmation (unless `--force` flag)
- Generate reports of what was cleaned

**Verification scripts** typically:
- Run checks and report status
- Generate JSON reports in `bridge_backend/diagnostics/`
- Exit `0` on success, non-zero on failure

### Environment Variables

Some scripts require environment variables:
- `BRIDGE_API_URL` - Bridge backend API URL
- `NETLIFY_AUTH_TOKEN` - Netlify authentication
- `RENDER_API_TOKEN` - Render platform API access
- `GITHUB_TOKEN` - GitHub API access

Check individual script documentation for specific requirements.

---

## 🆘 Getting Help

Most Python scripts support `--help`:
```bash
python3 scripts/script_name.py --help
```

For shell scripts, check the header comments in the file.

---

## 📚 Related Documentation

- [COMPREHENSIVE_SCAN_REPORT.md](../COMPREHENSIVE_SCAN_REPORT.md) - Historical scan report
- [FULL_SCAN_REPORT_2025.md](../FULL_SCAN_REPORT_2025.md) - Latest full scan results
- [TOTAL_STACK_TRIAGE_VERIFICATION.md](../TOTAL_STACK_TRIAGE_VERIFICATION.md) - Triage verification
- [docs/TOTAL_STACK_TRIAGE.md](../docs/TOTAL_STACK_TRIAGE.md) - Triage operations guide

---

**Maintained by:** SR-AIbridge Development Team  
**Last Updated:** November 2025
