# 🜂 Bridge Code Super-Engine (BCSE) Documentation

## Overview

The Bridge Code Super-Engine (BCSE) is a comprehensive quality gate system with Sovereign Git integration. It provides automated code quality analysis, security scanning, and enforcement for the SR-AIBridge project.

## Key Features

### 🔒 Sovereign Git Integration

- **Always Enabled**: BCSE is always active - no feature flags or toggles
- **Forge Dominion**: Pulls policies from Forge Dominion at runtime
- **No Static Secrets**: Uses DOMINION_SEAL for authentication
- **Placeholder Mode**: All quality gates are revealed for inspection and configuration

### 🛠️ Quality Checks

BCSE performs comprehensive quality analysis across multiple dimensions:

1. **Style** - Code formatting with black & ruff
2. **Typing** - Type checking with mypy (strict mode)
3. **Complexity** - Cyclomatic complexity analysis with radon
4. **Structure** - Architecture contract validation with import-linter
5. **Security** - Vulnerability scanning with bandit & semgrep
6. **Dependencies** - Dependency vulnerability checking (pip-audit, npm audit)
7. **Tests** - Test execution with coverage gates (pytest)

## Installation

### Development Dependencies

Install all BCSE tooling:

```bash
make init
```

Or manually:

```bash
pip install -r requirements-dev.txt
npm --prefix bridge-frontend ci
```

### Pre-commit Hooks

Install pre-commit hooks for automatic quality checks:

```bash
pip install pre-commit
pre-commit install
```

## Usage

### Quick Commands

```bash
# Show all quality gates (placeholder mode)
make gates

# Run full quality analysis
make analyze

# Auto-fix style issues
make fix

# Run tests only
make test
```

### Command Details

#### `make gates` - Show Quality Gates

Reveals all quality gates in placeholder mode, showing current policy configuration and available checks.

```bash
make gates
```

Output includes:
- Current policy settings (coverage threshold, severity levels, etc.)
- Sovereign features status
- List of all available quality checks

#### `make analyze` - Run Quality Analysis

Performs comprehensive quality analysis on the entire codebase.

```bash
make analyze
```

Checks performed:
- ✅ Code style (black, ruff)
- ✅ Type checking (mypy)
- ✅ Cyclomatic complexity (radon)
- ✅ Architecture contracts (import-linter)
- ✅ Security vulnerabilities (bandit, semgrep)
- ✅ Dependency vulnerabilities (pip-audit, npm audit)
- ✅ Tests with coverage (pytest)

Results are written to:
- `bcse_summary.md` - Markdown summary for PR comments
- `bcse.sarif` - SARIF format for GitHub Security
- `bcse_junit.xml` - JUnit format for CI systems

#### `make fix` - Auto-fix Issues

Automatically fixes style and simple code issues.

```bash
make fix
```

Performs:
- Black formatting
- Ruff auto-fixes (safe refactorings)

#### `make test` - Run Tests

Run the test suite:

```bash
make test
```

## Configuration

### Policy Configuration

BCSE policies can be configured in three ways (in order of precedence):

1. **Forge Dominion** (Sovereign mode) - Set environment variables:
   - `FORGE_POLICY_URL` - URL to fetch policies from
   - `DOMINION_SEAL` - Authentication token

2. **Local policy file** - Create `bridge_tools/bcse/policies.yaml`:
   ```yaml
   coverage_min: 0.80
   mypy_strict: true
   ruff_severity: "E,W,F"
   bandit_min_severity: "MEDIUM"
   max_cyclomatic: 10
   fail_on_vuln: true
   allowed_licenses:
     - MIT
     - BSD-3-Clause
     - Apache-2.0
     - ISC
   ```

3. **Default policy** - Built-in defaults (see `bridge_tools/bcse/config.py`)

### Environment Variables

- `FORGE_DOMINION_ROOT` - Forge Dominion endpoint (default: `dominion://local`)
- `FORGE_POLICY_URL` - URL to fetch policies from
- `DOMINION_SEAL` - Authentication token for Forge Dominion

## CI Integration

### GitHub Actions

BCSE runs automatically on all pull requests via the `bridge-quality.yml` workflow.

The workflow:
1. Installs dependencies
2. Runs BCSE analysis
3. Uploads SARIF to GitHub Security
4. Posts PR comment with summary
5. Fails the build if quality gate fails

### Secrets Configuration

Configure these GitHub secrets for full functionality:

- `FORGE_DOMINION_ROOT` - Forge Dominion endpoint
- `DOMINION_SEAL` - Authentication token
- `FORGE_POLICY_URL` - (Optional) URL to fetch policies from

## Placeholder Mode

In placeholder mode (always active), all quality gates are revealed:

- ✅ All policy settings are visible and configurable
- ✅ All quality checks are listed
- ✅ Sovereign features status is shown
- ✅ Use `make gates` to inspect current configuration

This transparency ensures developers understand exactly what quality standards are being enforced.

## Architecture

### Directory Structure

```
bridge_tools/bcse/
├── __init__.py           # Package initialization
├── __main__.py           # Module entry point
├── cli.py                # Command-line interface
├── config.py             # Policy configuration
├── forge.py              # Forge Dominion integration
├── reporters.py          # Output formatters (SARIF, Markdown)
├── runners/              # Tool runners
│   ├── __init__.py
│   ├── python_linters.py # black, ruff, mypy, radon
│   ├── security.py       # bandit, semgrep
│   ├── deps.py           # pip-audit, npm audit
│   ├── tests.py          # pytest with coverage
│   └── structure.py      # import-linter
├── rules/                # Quality rules
│   ├── semgrep.yaml      # Semgrep security rules
│   └── import_contracts.ini # Import linter contracts
└── templates/            # Output templates
    └── pr_summary.md.j2  # PR comment template
```

### Tool Integration

Each runner module wraps a specific quality tool:

- **python_linters.py**: black, ruff, mypy, radon
- **security.py**: bandit, semgrep
- **deps.py**: pip-audit, npm audit
- **tests.py**: pytest with coverage
- **structure.py**: import-linter

Runners handle:
- Tool execution
- Error handling (missing tools)
- Output parsing
- Exit code mapping

## Troubleshooting

### Tool Not Found

If a tool is not found, BCSE skips that check with a warning:

```
⚠️  black not found, skipping
```

Install missing tools:

```bash
make init
```

### Coverage Below Threshold

If coverage is below the minimum threshold:

```
❌ Coverage 65.0% is below minimum 80.0%
```

Solutions:
- Add more tests
- Adjust coverage threshold in policy configuration

### Import Contract Violations

If architecture contracts are violated:

```
❌ import-linter found violations
```

Review and fix imports to comply with contracts in `bridge_tools/bcse/rules/import_contracts.ini`.

## Development

### Adding New Quality Checks

1. Create a runner module in `bridge_tools/bcse/runners/`
2. Implement tool execution and result parsing
3. Add to `cli.py` in `cmd_analyze()`
4. Update documentation

### Adding Security Rules

Add semgrep rules to `bridge_tools/bcse/rules/semgrep.yaml`:

```yaml
rules:
  - id: my-custom-rule
    pattern: dangerous_function(...)
    message: "Don't use dangerous_function"
    severity: ERROR
    languages: [python]
```

### Testing

Run BCSE tests:

```bash
pytest tests/test_bcse.py -v
```

## Support

For issues or questions:
- Open an issue in the SR-AIBridge repository
- Check the README for general documentation
- Review the BCSE source code in `bridge_tools/bcse/`

---

**BCSE Status**: ✅ Always Enabled | 👁️ Placeholder Mode Active
