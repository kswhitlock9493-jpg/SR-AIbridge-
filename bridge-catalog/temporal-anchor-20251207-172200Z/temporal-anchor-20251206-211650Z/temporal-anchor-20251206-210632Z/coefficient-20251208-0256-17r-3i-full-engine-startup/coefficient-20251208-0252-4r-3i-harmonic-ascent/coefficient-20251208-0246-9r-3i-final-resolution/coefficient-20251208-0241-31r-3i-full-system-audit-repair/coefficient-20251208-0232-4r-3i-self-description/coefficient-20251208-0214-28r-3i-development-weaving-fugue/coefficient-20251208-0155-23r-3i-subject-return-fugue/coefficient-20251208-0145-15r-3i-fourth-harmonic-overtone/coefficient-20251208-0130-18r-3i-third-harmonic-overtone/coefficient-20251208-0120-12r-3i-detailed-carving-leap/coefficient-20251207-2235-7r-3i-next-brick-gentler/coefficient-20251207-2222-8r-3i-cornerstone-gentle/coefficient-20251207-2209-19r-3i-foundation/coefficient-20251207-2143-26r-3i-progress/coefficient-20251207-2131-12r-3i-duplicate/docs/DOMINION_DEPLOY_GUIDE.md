# Forge Dominion Deployment Guide v1.9.7s-SOVEREIGN

## Quick Start

### 1. Generate Root Key

For GitHub Actions, generate and set the sovereign root key:

```bash
# Generate new root key
python3 -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip('='))"
```

Store the output securely and set as GitHub secret:

```bash
gh secret set FORGE_DOMINION_ROOT --body "<your-generated-key>"
```

### 2. Set Configuration Variables

```bash
# Set forge mode
gh variable set FORGE_DOMINION_MODE --body "sovereign"

# Set forge version
gh variable set FORGE_DOMINION_VERSION --body "1.9.7s"
```

### 3. Verify Installation

```bash
# Run quantum predeploy orchestrator
python3 bridge_backend/runtime/quantum_predeploy_orchestrator.py
```

Expected output:
```
🜂 Quantum Predeploy Orchestrator v1.9.7s-SOVEREIGN
✅ FORGE_DOMINION_ROOT configured
✅ All pre-deployment checks passed
```

## Deployment Environments

### Local Development

No FORGE_DOMINION_ROOT required - automatically generated and stored in `.alik/forge_state.json`:

```bash
# Bootstrap will auto-generate local key
python3 -c "from bridge_backend.db.bootstrap import validate_forge_dominion_root; validate_forge_dominion_root()"
```

### Staging/Production

**Required Environment Variables**:

```bash
# Mandatory
FORGE_DOMINION_ROOT=<base64-encoded-32-byte-key>

# Optional (with defaults)
FORGE_DOMINION_MODE=sovereign
FORGE_DOMINION_VERSION=1.9.7s
FORGE_DOMINION_POLICIES=<json-encoded-policies>
```

## GitHub Actions Integration

### Workflow Setup

Create `.github/workflows/quantum_dominion.yml`:

```yaml
name: Quantum Dominion Security

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  quantum-security:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r bridge_backend/requirements.txt
      
      - name: Set environment variables
        env:
          FORGE_DOMINION_ROOT: ${{ secrets.FORGE_DOMINION_ROOT }}
        run: |
          echo "FORGE_DOMINION_MODE=${{ vars.FORGE_DOMINION_MODE }}" >> $GITHUB_ENV
          echo "FORGE_DOMINION_VERSION=${{ vars.FORGE_DOMINION_VERSION }}" >> $GITHUB_ENV
          echo "ENVIRONMENT=production" >> $GITHUB_ENV
      
      - name: Run Quantum Predeploy Orchestrator
        run: |
          python3 bridge_backend/runtime/quantum_predeploy_orchestrator.py
      
      - name: Upload Security Reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: quantum-security-reports
          path: .alik/predeploy_report.json
          retention-days: 30
      
      - name: Check Compliance Status
        run: |
          if [ -f .alik/predeploy_report.json ]; then
            python3 -c "
            import json, sys
            with open('.alik/predeploy_report.json') as f:
                report = json.load(f)
            status = report.get('compliance', {}).get('compliance_status', 'UNKNOWN')
            if status != 'COMPLIANT':
                print(f'❌ Compliance status: {status}')
                sys.exit(1)
            print(f'✅ Compliance status: {status}')
            "
          fi
```

### Integration with Existing Workflows

Add to existing deployment workflows:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      # ... existing checkout and setup steps ...
      
      - name: Quantum Security Check
        env:
          FORGE_DOMINION_ROOT: ${{ secrets.FORGE_DOMINION_ROOT }}
        run: |
          python3 bridge_backend/runtime/quantum_predeploy_orchestrator.py
      
      # ... rest of deployment steps ...
```

## Render Deployment

### Environment Variables

In Render dashboard, add the following environment variables:

```
FORGE_DOMINION_ROOT=<your-root-key>
FORGE_DOMINION_MODE=sovereign
FORGE_DOMINION_VERSION=1.9.7s
```

### Build Command

Update `render.yaml`:

```yaml
services:
  - type: web
    name: sr-aibridge
    env: python
    buildCommand: |
      pip install -r bridge_backend/requirements.txt
      python3 bridge_backend/runtime/quantum_predeploy_orchestrator.py
    startCommand: python3 bridge_backend/main.py
    envVars:
      - key: FORGE_DOMINION_ROOT
        sync: false
      - key: FORGE_DOMINION_MODE
        value: sovereign
      - key: FORGE_DOMINION_VERSION
        value: 1.9.7s
```

## Netlify Deployment

### Environment Variables

In Netlify dashboard → Site settings → Environment variables:

```
FORGE_DOMINION_ROOT=<your-root-key>
FORGE_DOMINION_MODE=sovereign
FORGE_DOMINION_VERSION=1.9.7s
```

### Build Settings

Update `netlify.toml`:

```toml
[build]
  command = """
    pip install -r bridge_backend/requirements.txt &&
    python3 bridge_backend/runtime/quantum_predeploy_orchestrator.py &&
    npm run build
  """
  publish = "dist"

[build.environment]
  FORGE_DOMINION_MODE = "sovereign"
  FORGE_DOMINION_VERSION = "1.9.7s"
```

## Token Management

### Generate Provider Tokens

```python
from bridge_backend.bridge_core.token_forge_dominion import QuantumAuthority

# Initialize authority
authority = QuantumAuthority()

# Mint token for Render
render_token = authority.mint_quantum_token(
    provider="render",
    ttl_seconds=300,  # 5 minutes
    metadata={"environment": "production"}
)

print(f"Token ID: {render_token['token_id']}")
print(f"Expires: {render_token['expires_at']}")
```

### Validate Tokens

```python
from bridge_backend.bridge_core.token_forge_dominion import QuantumAuthority

authority = QuantumAuthority()

# Verify token
is_valid, payload = authority.verify_token(token_envelope)

if is_valid:
    print(f"✅ Token valid for {payload['provider']}")
    print(f"Expires at: {payload['expires_at']}")
else:
    print("❌ Token invalid or expired")
```

## Security Scanning

### Manual Scan

```python
from bridge_backend.bridge_core.token_forge_dominion import QuantumScanner

scanner = QuantumScanner(root_path=".")
report = scanner.quantum_scan()

print(f"Status: {report['status']}")
print(f"Files scanned: {report['files_scanned']}")
print(f"Findings: {report['total_findings']}")
print(f"Risk score: {report['risk_score']}")
```

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "🔬 Running Quantum Security Scan..."

python3 - <<'PYTHON'
from bridge_backend.bridge_core.token_forge_dominion import QuantumScanner
import sys

scanner = QuantumScanner(root_path=".")
report = scanner.quantum_scan()

if report['findings_by_severity']['critical'] > 0:
    print(f"❌ Critical security findings: {report['findings_by_severity']['critical']}")
    print("Fix critical issues before committing.")
    sys.exit(1)

print(f"✅ Security scan passed (status: {report['status']})")
PYTHON

exit $?
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Key Rotation

### Manual Rotation

```python
from bridge_backend.bridge_core.token_forge_dominion import QuantumAuthority

authority = QuantumAuthority()

# Generate new root key
new_key = authority.rotate_root_key()

print(f"New root key: {new_key}")
print("⚠️  Update FORGE_DOMINION_ROOT in all environments!")
```

### Automated Rotation (Future)

Currently, rotation must be manual. Future versions will support:
- Automated 30-day rotation
- Zero-downtime key migration
- Multi-key validation period

## Monitoring & Compliance

### Health Check

```bash
python3 - <<'PYTHON'
from bridge_backend.bridge_core.token_forge_dominion import EnterpriseOrchestrator

orchestrator = EnterpriseOrchestrator()
health = orchestrator.health_check()

print(f"Overall Status: {health['overall_status']}")
for component, status in health['components'].items():
    print(f"  {component}: {status['status']}")
PYTHON
```

### Compliance Report

```bash
python3 - <<'PYTHON'
from bridge_backend.bridge_core.token_forge_dominion import EnterpriseOrchestrator
import json

orchestrator = EnterpriseOrchestrator()
compliance = orchestrator.generate_compliance_report()

print(json.dumps(compliance, indent=2))
PYTHON
```

### View Audit Trail

```bash
cat .alik/forge_state.json | python3 -m json.tool
```

## Troubleshooting

### Root Key Not Found

**Symptom**: `⚠️ FORGE_DOMINION_ROOT not set`

**Solution**: 
```bash
# Generate and set root key
NEW_KEY=$(python3 -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip('='))")
export FORGE_DOMINION_ROOT="$NEW_KEY"

# Or for GitHub Actions
gh secret set FORGE_DOMINION_ROOT --body "$NEW_KEY"
```

### Security Scan Failures

**Symptom**: `❌ Security scan status 'CRITICAL' not acceptable for production`

**Solution**:
1. Review scan report: `cat .alik/predeploy_report.json`
2. Identify critical findings
3. Move hardcoded secrets to environment variables
4. Re-run scan to verify

### Low Resonance Score

**Symptom**: `❌ Resonance too low for production: 25`

**Solution**:
1. Check bridge health: `python3 bridge_backend/runtime/health_probe.py`
2. Review error logs
3. Fix underlying issues
4. Wait for resonance to recover
5. Or deploy to staging instead

### Token Validation Failures

**Symptom**: Token verification returns `False`

**Possible Causes**:
- Expired token (check TTL)
- Wrong root key (verify FORGE_DOMINION_ROOT)
- Token envelope modified (check signature)

**Debug**:
```python
is_valid, payload = authority.verify_token(token_envelope)
if not is_valid:
    print("Token validation failed")
    print(f"Token envelope: {token_envelope}")
```

## Best Practices

### Security

1. **Never commit** FORGE_DOMINION_ROOT to version control
2. **Rotate keys** every 30 days minimum
3. **Use short TTLs** in production (5-15 minutes)
4. **Monitor** audit trail regularly
5. **Scan** before every deployment

### Operational

1. **Test** in staging before production
2. **Automate** security scans in CI/CD
3. **Monitor** health and compliance metrics
4. **Document** all key rotations
5. **Review** audit trail weekly

### Development

1. **Use** local key generation for development
2. **Exclude** `.alik/` from version control
3. **Run** quantum scanner before commits
4. **Set up** pre-commit hooks
5. **Keep** dependencies updated

## Support & Resources

- **Documentation**: `/docs/DOMINION_SECURITY_SPEC.md`
- **Source Code**: `/bridge_backend/bridge_core/token_forge_dominion/`
- **Issue Tracker**: GitHub Issues
- **Security Contact**: See `SECURITY.md`

---

**Guide Version**: 1.9.7s-SOVEREIGN  
**Last Updated**: 2025-11-03  
**Next Review**: 2025-12-03
