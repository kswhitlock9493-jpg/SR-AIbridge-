# 🔍 Sovereign Audit & Repair System

## Overview

The Sovereign Audit & Repair System is a comprehensive tool for auditing and automatically repairing Git, Netlify, and repository configurations in the SR-AIbridge project. It ensures sovereign compliance across all infrastructure components.

## Features

### 🔐 Git Sovereign Audit
- ✅ Git configuration validation (user.name, user.email)
- ✅ Git Sovereign Agent installation verification
- ✅ Git hooks inspection
- ✅ .gitignore completeness check
- ✅ Git LFS configuration validation
- ✅ Branch status and working tree checks
- ✅ Submodules validation

### 🌐 Netlify Sovereign Audit
- ✅ netlify.toml configuration validation
- ✅ Security headers verification
- ✅ Environment files audit (.env.netlify, .env.netlify.example)
- ✅ Netlify Functions presence check
- ✅ Redirects configuration validation
- ✅ Headers file verification
- ✅ Build scripts validation

### 📦 Repository Sovereign Audit
- ✅ Repository structure validation
- ✅ Dependencies files verification (requirements.txt, pyproject.toml, package.json)
- ✅ Configuration files completeness
- ✅ Documentation presence check
- ✅ Security files validation
- ✅ CI/CD workflows verification

### 🔧 Auto-Repair Capabilities
- 🔧 Automatic .gitignore pattern addition
- 🔧 Missing security headers detection
- 🔧 Configuration file validation
- 🔧 (More auto-repair features coming soon)

## Installation

The audit tool is already included in the repository. No additional installation required.

```bash
# Make sure you're in the repository root
cd /path/to/SR-AIbridge-

# The tool is located at:
scripts/sovereign_audit_orchestrator.py
```

## Usage

### Basic Usage

Run a full audit with auto-repair:

```bash
python3 scripts/sovereign_audit_orchestrator.py
```

### Advanced Usage

Run audit without auto-repair:

```bash
python3 scripts/sovereign_audit_orchestrator.py --no-repair
```

Run audit in a specific directory:

```bash
python3 scripts/sovereign_audit_orchestrator.py --repo-root /path/to/repo
```

### Command-Line Options

```
--repo-root PATH    Repository root directory (default: current directory)
--no-repair         Disable auto-repair functionality
```

## Output

### Console Output

The tool provides real-time feedback during execution:

```
================================================================================
👑 SOVEREIGN AUDIT & REPAIR ORCHESTRATOR
================================================================================
Repository: SR-AIbridge-
Branch: main
Commit: abc123de
Timestamp: 2025-11-05T18:08:05.578548+00:00
================================================================================

🚀 EXECUTING FULL SOVEREIGN AUDIT

================================================================================
🔍 GIT SOVEREIGN AUDIT
================================================================================
...
📊 GIT SOVEREIGN Results:
  ✅ PASS: 7
  ⚠️  WARNING: 2
  ❌ FAIL: 0
  🔧 REPAIRED: 0
...
```

### JSON Reports

Audit reports are saved to:
- `bridge_backend/diagnostics/sovereign_audit_latest.json` - Latest audit
- `bridge_backend/diagnostics/sovereign_audit_YYYYMMDD_HHMMSS.json` - Timestamped audit

### Report Structure

```json
{
  "timestamp": "2025-11-05T18:08:05.578548+00:00",
  "repository": "SR-AIbridge-",
  "branch": "main",
  "commit_hash": "abc123de",
  "audits_performed": [
    "git_sovereign",
    "netlify_sovereign",
    "repository_sovereign"
  ],
  "results": [...],
  "summary": {
    "total_checks": 27,
    "passed": 25,
    "warnings": 2,
    "failed": 0,
    "repaired": 0,
    "score": 92.59,
    "status": "HEALTHY"
  },
  "repair_actions": [...]
}
```

## Exit Codes

- `0` - HEALTHY: All checks passed or warnings only
- `1` - WARNING: Some warnings present
- `2` - NEEDS_ATTENTION: Critical issues detected

## Audit Categories

### Git Categories
- `git_config` - Git configuration settings
- `git_sovereign` - Git Sovereign Agent installation
- `git_hooks` - Git hooks configuration
- `git_ignore` - .gitignore completeness
- `git_lfs` - Git LFS configuration
- `git_branch` - Branch and working tree status
- `git_submodules` - Submodules configuration

### Netlify Categories
- `netlify_config` - netlify.toml configuration
- `netlify_security` - Security headers
- `netlify_env` - Environment files
- `netlify_functions` - Netlify Functions
- `netlify_redirects` - Redirects configuration
- `netlify_headers` - Headers file
- `netlify_build` - Build scripts

### Repository Categories
- `repo_structure` - Directory structure
- `dependencies` - Dependency files
- `config_files` - Configuration files
- `documentation` - Documentation files
- `security` - Security documentation
- `ci_cd` - CI/CD workflows

## Severity Levels

- `CRITICAL` - Immediate attention required
- `HIGH` - Important issue that should be addressed
- `MEDIUM` - Should be addressed soon
- `LOW` - Minor issue
- `INFO` - Informational

## Status Values

- `PASS` - Check passed successfully
- `WARNING` - Issue detected, may need attention
- `FAIL` - Check failed
- `REPAIRED` - Issue was automatically repaired

## Integration with CI/CD

### GitHub Actions

You can integrate the audit tool into GitHub Actions workflows:

```yaml
name: Sovereign Audit

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  audit:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Run Sovereign Audit
      run: |
        python3 scripts/sovereign_audit_orchestrator.py
    
    - name: Upload Audit Report
      uses: actions/upload-artifact@v4
      with:
        name: sovereign-audit-report
        path: bridge_backend/diagnostics/sovereign_audit_latest.json
        retention-days: 30
```

## Testing

Run the test suite:

```bash
python3 -m pytest tests/test_sovereign_audit.py -v
```

Expected output:
```
29 passed in 0.27s
```

## Development

### Adding New Checks

To add a new check to any auditor:

1. Add a new method to the appropriate auditor class (e.g., `_check_new_feature`)
2. Call the method from the `audit()` method
3. Append results to `self.results`
4. Add tests in `tests/test_sovereign_audit.py`

Example:

```python
def _check_new_feature(self):
    """Check for new feature"""
    feature_file = self.repo_root / "feature.txt"
    
    if feature_file.exists():
        self.results.append(AuditResult(
            category="new_category",
            check_name="new_feature",
            status="PASS",
            message="Feature configured correctly",
            severity="INFO"
        ))
    else:
        self.results.append(AuditResult(
            category="new_category",
            check_name="new_feature",
            status="FAIL",
            message="Feature not configured",
            severity="HIGH",
            auto_repair_available=True
        ))
```

### Adding Auto-Repair

Implement repair logic in the `_perform_repairs()` method:

```python
def _perform_repairs(self):
    """Perform auto-repairs for failed checks"""
    for result in self.results:
        if result.auto_repair_available and result.status in ["FAIL", "WARNING"]:
            if result.check_name == "new_feature":
                self._repair_new_feature(result)

def _repair_new_feature(self, result: AuditResult):
    """Repair new feature"""
    try:
        # Perform repair
        feature_file = self.repo_root / "feature.txt"
        feature_file.write_text("feature config\n")
        
        # Update result
        result.status = "REPAIRED"
        result.repaired = True
        result.message = "Feature configured automatically"
        
        print(f"  ✅ Repaired: {result.check_name}")
    except Exception as e:
        print(f"  ❌ Failed to repair {result.check_name}: {e}")
```

## Architecture

### Class Hierarchy

```
SovereignAuditOrchestrator
├── SovereignGitAuditor
├── SovereignNetlifyAuditor
└── SovereignRepositoryAuditor
```

### Data Models

- `AuditResult` - Individual check result
- `AuditReport` - Complete audit report with summary

## Best Practices

1. **Run regularly**: Schedule audits to run automatically
2. **Review warnings**: Don't ignore warnings - they may indicate issues
3. **Check reports**: Review JSON reports for detailed information
4. **Auto-repair with caution**: Review repaired items to ensure correctness
5. **Add custom checks**: Extend the tool for your specific needs

## Troubleshooting

### Common Issues

**Issue**: Tool fails with "Module not found"
```bash
# Solution: Make sure you're in the repository root
cd /path/to/SR-AIbridge-
python3 scripts/sovereign_audit_orchestrator.py
```

**Issue**: Git checks fail
```bash
# Solution: Make sure Git is installed and repository is initialized
git --version
git status
```

**Issue**: Netlify checks show warnings
```bash
# Solution: Review netlify.toml and environment files
cat netlify.toml
cat .env.netlify
```

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review existing documentation
- Check test cases for usage examples

## Future Enhancements

Planned features:
- [ ] More comprehensive auto-repair capabilities
- [ ] Interactive mode for manual repairs
- [ ] Audit history tracking and trending
- [ ] Custom rule definitions
- [ ] Integration with monitoring systems
- [ ] Email/Slack notifications
- [ ] Diff-based change tracking

## License

Part of the SR-AIbridge project. See main repository LICENSE for details.

---

**Last Updated**: 2025-11-05  
**Version**: 1.0.0  
**Status**: Production Ready ✅
