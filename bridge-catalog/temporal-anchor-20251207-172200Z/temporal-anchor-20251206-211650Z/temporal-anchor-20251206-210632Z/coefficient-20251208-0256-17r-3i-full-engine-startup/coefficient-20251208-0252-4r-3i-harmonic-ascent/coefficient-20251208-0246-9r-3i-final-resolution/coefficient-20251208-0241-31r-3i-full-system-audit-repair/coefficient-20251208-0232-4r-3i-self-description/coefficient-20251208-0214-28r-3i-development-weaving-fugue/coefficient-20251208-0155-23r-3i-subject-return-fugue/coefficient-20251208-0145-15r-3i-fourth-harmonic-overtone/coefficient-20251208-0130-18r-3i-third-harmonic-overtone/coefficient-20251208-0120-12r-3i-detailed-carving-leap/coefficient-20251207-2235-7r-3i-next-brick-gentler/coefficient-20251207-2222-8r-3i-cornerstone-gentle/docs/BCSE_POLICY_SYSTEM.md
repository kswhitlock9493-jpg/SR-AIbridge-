# BCSE Sovereign Policy System

## Overview

The Bridge Code Super-Engine (BCSE) now features a **Sovereign Policy System** that dynamically adjusts quality gates based on:
- **Git branch** (main, feature/*, release/*, hotfix/*, staging/*)
- **Environment tier** (development, staging, production)
- **BRH federation role** (leader, witness)
- **Code path** (stricter rules for critical directories)

This enables self-governing quality enforcement that adapts automatically based on context.

## Policy Architecture

### 1. Policy File Location

The authoritative policy file is located at:
```
bridge_tools/bcse/policies.yaml
```

This file defines all quality gates and their variations across different contexts.

### 2. Policy Loading Hierarchy

Policies are loaded in the following order of precedence:

1. **Forge Dominion API** (if `FORGE_POLICY_URL` is set)
   - Centralized policy management
   - Real-time updates without code changes
   - Requires `DOMINION_SEAL` authentication

2. **Local Policy File** (fallback)
   - `bridge_tools/bcse/policies.yaml`
   - Version controlled with your code
   - Used when Forge is unavailable

### 3. Policy Merge Strategy

When loading policies, the system applies configurations in this order:

1. **Defaults** - Base quality standards
2. **Environment Override** - Adjust for dev/staging/prod
3. **Branch-Specific Rules** - Fine-tune per branch pattern
4. **Federation Role Modifiers** - Leader/witness adjustments

Each layer overrides values from the previous layer.

## Policy Configuration

### Branch-Aware Quality Gates

Different branches enforce different quality standards:

| Branch Pattern | Coverage | MyPy Strict | Max Complexity | Fail on Vuln |
|---------------|----------|-------------|----------------|--------------|
| `main` | 85% | ✓ | 10 | ✓ |
| `release/*` | 88% | ✓ | 8 | ✓ (HIGH) |
| `hotfix/*` | 75% | ✓ | 12 | ✓ |
| `feature/*` | 70% | ✗ | 12 | ✗ |
| `develop` | 80% | ✓ | 12 | ✓ |
| `staging/*` | 75% | ✓ | 12 | ✓ |

### Environment Tiers

Quality standards adjust based on environment:

| Environment | Coverage | MyPy Strict | Max Complexity | Fail on Vuln |
|------------|----------|-------------|----------------|--------------|
| Development | 65% | ✗ | 14 | ✗ (warn) |
| Staging | 75% | ✓ | 12 | ✓ |
| Production | 90% | ✓ | 8 | ✓ (strict) |

**Environment Detection:**
- Explicit: Set `ENVIRONMENT=production` environment variable
- Inferred from branch:
  - `feature/*`, `develop` → development
  - `staging/*` → staging
  - `main`, `release/*` → production

### Federation Role Behavior

When running in a BRH federation, quality gates adapt based on node role:

| Role | Coverage Modifier | Complexity Modifier |
|------|------------------|---------------------|
| Leader | +5% | -1 (stricter) |
| Witness | -5% | +2 (lenient) |

**Example:** On `main` branch (85% coverage, complexity 10):
- **Leader node:** 90% coverage, complexity 9
- **Witness node:** 80% coverage, complexity 12

This prevents witnesses from blocking leader deployments while maintaining quality.

### Path-Specific Overrides

Critical code paths enforce stricter rules:

```yaml
overrides:
  # Core engines - highest security
  - when_paths: ["bridge_backend/bridge_core/engines/**"]
    set:
      bandit_min_severity: "HIGH"
      max_cyclomatic: 8
      mypy_strict: true

  # Security-critical paths
  - when_paths: 
      - "bridge_backend/bridge_core/security/**"
      - "bridge_backend/bridge_core/auth/**"
    set:
      bandit_min_severity: "HIGH"
      mypy_strict: true
      max_cyclomatic: 6
```

## Using the Policy System

### Local Development

1. **Check current policy:**
   ```bash
   python -m bridge_tools.bcse.cli gates
   ```

2. **Run quality checks:**
   ```bash
   python -m bridge_tools.bcse.cli analyze
   ```

3. **Test with different branch:**
   ```bash
   export GITHUB_REF_NAME=feature/my-feature
   python -m bridge_tools.bcse.cli gates
   ```

4. **Test with federation role:**
   ```bash
   export BRH_FEDERATION_ROLE=leader
   python -m bridge_tools.bcse.cli gates
   ```

### CI/CD Integration

The GitHub Actions workflow automatically uses branch-aware policies:

```yaml
# .github/workflows/bridge-quality.yml
env:
  FORGE_DOMINION_ROOT: ${{ secrets.FORGE_DOMINION_ROOT }}
  DOMINION_SEAL: ${{ secrets.DOMINION_SEAL }}
  # Optional: Use Forge API for centralized policy management
  # FORGE_POLICY_URL: https://sovereign.bridge/api/forge/policy/quality
```

The workflow automatically:
- Detects the current branch (`${{ github.ref_name }}`)
- Loads appropriate policy from local file or Forge
- Enforces quality gates based on context

### Forge API Endpoints

If using the Forge policy API, the following endpoints are available:

#### Get Policy for Branch
```bash
GET /forge/policy/quality?branch=main&federation_role=leader
```

#### Get Policy Version
```bash
GET /forge/policy/version
```

#### List Available Branches
```bash
GET /forge/policy/branches
```

#### List Available Environments
```bash
GET /forge/policy/environments
```

**Authentication:** Include `Authorization: Bearer $DOMINION_SEAL` header

## Policy Customization

### Modifying Quality Gates

Edit `bridge_tools/bcse/policies.yaml`:

```yaml
branches:
  main:
    coverage_min: 0.85      # Change to your requirement
    mypy_strict: true
    max_cyclomatic: 10
    fail_on_vuln: true
```

### Adding New Branch Patterns

```yaml
branches:
  "epic/*":
    coverage_min: 0.65
    mypy_strict: false
    max_cyclomatic: 16
    fail_on_vuln: false
```

### Creating Custom Environments

```yaml
env:
  testing:
    coverage_min: 0.70
    mypy_strict: false
    max_cyclomatic: 15
```

### Adjusting Federation Behavior

```yaml
federation:
  leader:
    coverage_min: "+0.10"    # Stricter for leaders
    max_cyclomatic: "-2"
  witness:
    coverage_min: "-0.10"    # More lenient for witnesses
    max_cyclomatic: "+3"
```

## Quality Gate Checks

The BCSE runs the following checks:

1. **Style** - `black`, `ruff`
2. **Typing** - `mypy`
3. **Complexity** - `radon` (cyclomatic complexity)
4. **Structure** - `import-linter` (architecture validation)
5. **Security** - `bandit`, `semgrep`
6. **Dependencies** - `pip-audit`, `npm audit`
7. **Tests** - `pytest` with coverage analysis

Each check's behavior is controlled by the active policy.

## Troubleshooting

### Policy Not Loading

**Problem:** BCSE uses default policy instead of custom configuration

**Solutions:**
1. Verify `bridge_tools/bcse/policies.yaml` exists
2. Check YAML syntax: `python -c "import yaml; yaml.safe_load(open('bridge_tools/bcse/policies.yaml'))"`
3. Check file permissions

### Branch Detection Issues

**Problem:** Wrong branch detected

**Solutions:**
1. Set explicitly: `export GITHUB_REF_NAME=main`
2. Check git branch: `git rev-parse --abbrev-ref HEAD`
3. Verify not in detached HEAD state

### Federation Role Not Applied

**Problem:** Leader/witness modifiers not working

**Solutions:**
1. Set explicitly: `export BRH_FEDERATION_ROLE=leader`
2. Verify role is `leader` or `witness` (case-sensitive)
3. Check policy file has `federation:` section

### Forge API Connection Failed

**Problem:** Cannot connect to Forge API

**Solutions:**
1. Verify `FORGE_POLICY_URL` is correct
2. Check network connectivity
3. Verify `DOMINION_SEAL` is set correctly
4. System will automatically fallback to local policy

## Best Practices

1. **Version Control Policies** - Always commit `policies.yaml` with your code
2. **Test Before Merge** - Run `bcse analyze` locally before pushing
3. **Document Exceptions** - Add comments when relaxing rules temporarily
4. **Use Feature Branches** - Take advantage of relaxed quality gates for exploration
5. **Tighten Before Release** - Ensure release branches enforce stricter standards
6. **Monitor Federation** - Check that leader/witness modifiers work as expected

## Examples

### Example 1: Feature Development
```bash
# On feature/new-widget branch
$ python -m bridge_tools.bcse.cli gates

Coverage Minimum:      70%    # Relaxed for exploration
MyPy Strict Mode:      False  # Allow rapid iteration
Max Cyclomatic:        12     # More complexity allowed
Fail on Vulnerabilities: False # Warn but don't block
```

### Example 2: Production Deployment
```bash
# On main branch, leader node
$ export BRH_FEDERATION_ROLE=leader
$ python -m bridge_tools.bcse.cli gates

Coverage Minimum:      90%    # 85% + 5% leader modifier
MyPy Strict Mode:      True   # Strict typing enforced
Max Cyclomatic:        9      # 10 - 1 leader modifier
Fail on Vulnerabilities: True  # Must be clean
```

### Example 3: Hotfix Emergency
```bash
# On hotfix/urgent-fix branch
$ python -m bridge_tools.bcse.cli gates

Coverage Minimum:      75%    # Balanced for urgency
MyPy Strict Mode:      True   # Type safety maintained
Max Cyclomatic:        12     # Some complexity allowed
Fail on Vulnerabilities: True  # Security still enforced
```

## Migration from Static Policies

If you had hardcoded policies in your CI:

**Before:**
```yaml
# Fixed thresholds
- coverage_min: 0.80
- mypy_strict: true
```

**After:**
```yaml
# Branch-aware, automatically adjusts
# No changes needed - policy system handles it
```

Your existing configurations will work unchanged, but you gain:
- Branch-specific quality gates
- Environment-aware enforcement
- Federation role support
- Centralized policy management via Forge

## Sovereign Quality Enforcement

The BCSE policy system represents **Sovereign Quality Enforcement**:

✅ **Self-Governing** - Quality gates adapt automatically to context  
✅ **Self-Documenting** - Policy file explicitly defines all rules  
✅ **Self-Validating** - Local and CI environments use same policies  
✅ **Self-Updating** - Forge API enables real-time policy updates  

This ensures consistent, context-aware quality enforcement across all development scenarios.
