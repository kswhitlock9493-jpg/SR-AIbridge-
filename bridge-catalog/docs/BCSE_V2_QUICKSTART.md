# BCSE v2 Quick Start Guide

## What is BCSE v2?

BCSE v2 (Sovereign Autocorrect Engine) is a production readiness verification system that ensures your code is deployment-ready by:

- Detecting placeholder code and unsafe patterns
- Validating environment configuration
- Checking production security settings
- Verifying runtime health

## 5-Minute Quick Start

### 1. Install Dependencies

```bash
make init
```

### 2. Run Quality Check

```bash
make analyze
```

This runs:
- Code style checks (black, ruff)
- Type checking (mypy)
- Security scanning (bandit, semgrep)
- Dependency audits
- Test coverage

### 3. Run Production Proof

```bash
# Set your production environment variables
export FORGE_DOMINION_ROOT=https://your-forge.example.com
export ALLOWED_ORIGINS=https://your-app.netlify.app
export DEBUG=false
export CORS_ALLOW_ALL=false

# Run the proof
make prove
```

### 4. Fix Any Issues

If `make prove` fails:

```bash
# Fix style issues
make fix

# Check for placeholders
python -m bridge_tools.bcse.cli gates
```

## Common Commands

### Check for Localhost References

```bash
FORGE_DOMINION_ROOT=https://your-forge.example.com make rewrite
```

This shows what URLs would be rewritten (doesn't modify files).

### Show All Quality Gates

```bash
make gates
```

### Run Tests

```bash
make test
```

## Production Deployment

Before deploying:

```bash
# 1. Ensure environment is configured
export ENVIRONMENT=production
export DEBUG=false
export CORS_ALLOW_ALL=false
export ALLOWED_ORIGINS=https://your-production-domain.com
export FORGE_DOMINION_ROOT=https://your-forge.example.com

# 2. Run production proof
make prove

# 3. If it passes, you're ready to deploy!
```

## CI/CD Integration

BCSE v2 automatically runs in GitHub Actions on every push/PR.

Check your workflow at: `.github/workflows/bridge-proof.yml`

## Need Help?

- Full documentation: [`docs/BCSE_V2_GUIDE.md`](./BCSE_V2_GUIDE.md)
- Run tests: `pytest tests/test_bcse_v2.py -v`
- Check Makefile: `make help`

## Safety First

🔒 **All commands are safe by default:**
- `make rewrite` - Only shows what would change (dry-run)
- `make improve` - Disabled to prevent unwanted changes
- `make prove` - Read-only verification

To actually modify files, explicit flags are required.
