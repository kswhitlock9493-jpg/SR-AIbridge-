# Sovereign Engines

**Quantum-resistant evaluation engines with bridge resonance integration**

Version: 1.0.0

---

## Overview

The Sovereign Engines suite provides enterprise-grade code analysis, compliance management, and log intelligence with quantum-resistant security and bridge resonance awareness.

### Components

1. **Sovereign Compliance Guard** - Quantum-resistant license management with military-grade audit trails
2. **Sovereign MicroScribe Engine** - Quantum-enhanced diff analysis and PR generation
3. **Sovereign MicroLogician Engine** - Advanced log analysis with security intelligence

---

## Features

### 🔐 Sovereign Compliance Guard

- **Quantum-resistant license validation** using HMAC-SHA384
- **Bridge resonance-aware compliance** (≥0.95 threshold)
- **Military-grade audit trails** integrated with Genesis bus
- **Sovereign policy enforcement** with route protection

### 📝 Sovereign MicroScribe Engine

- **Quantum-enhanced diff analysis** with security validation
- **Resonance-aware PR generation** (QUANTUM/DEEP/STANDARD modes)
- **Enterprise-grade change intelligence** with risk assessment
- **Bridge-native integration** with sovereign compliance

### 🔍 Sovereign MicroLogician Engine

- **Quantum-enhanced log pattern detection**
- **Security threat intelligence** with anomaly detection
- **Performance bottleneck analysis** and metrics
- **Resonance-aware confidence scoring**

---

## Installation

The Sovereign Engines are included in the SR-AIbridge ecosystem.

### Dependencies

```bash
pip install pydantic fastapi python-multipart
```

---

## Quick Start

### Using the Engines Programmatically

```python
from bridge_backend.bridge_engines.sovereign_guard import SovereignComplianceGuard
from bridge_backend.bridge_engines.micro_scribe import SovereignMicroScribe
from bridge_backend.bridge_engines.micro_logician import SovereignMicroLogician

# Compliance Guard
guard = SovereignComplianceGuard()
compliance = guard.check_compliance("my_operation")
print(f"Compliant: {compliance.compliant}")

# MicroScribe - Diff Analysis
scribe = SovereignMicroScribe()
diff_content = open("my.diff").read()
analysis = scribe.analyze_diff(diff_content)
print(f"Risk Level: {analysis.risk_level}")

# PR Generation
pr = scribe.generate_pr(analysis, "My PR Title", "Description")
print(f"PR with {len(pr.labels)} labels generated")

# MicroLogician - Log Analysis
logician = SovereignMicroLogician()
log_content = open("app.log").read()
analysis = logician.analyze_logs(log_content)
print(f"Security Findings: {len(analysis.security_findings)}")
```

### Using the API

Start the SR-AIbridge server:

```bash
uvicorn bridge_backend.main:app --reload
```

Then access the Sovereign Engines API:

```bash
# Check engine status
curl http://localhost:8000/bridge/engines/status

# Analyze a diff
curl -X POST http://localhost:8000/bridge/engines/microscribe/analyze \
  -F "diff_file=@changes.diff"

# Analyze logs
curl -X POST http://localhost:8000/bridge/engines/micrologician/analyze \
  -F "log_file=@app.log"

# Check compliance
curl "http://localhost:8000/bridge/engines/compliance/check?operation=test"
```

---

## API Endpoints

### Health & Status

- `GET /bridge/engines/health` - Health check
- `GET /bridge/engines/status` - Engine status and capabilities

### Compliance Guard

- `GET /bridge/engines/compliance/check` - Check compliance for an operation
- `GET /bridge/engines/compliance/audit` - Get audit trail

### MicroScribe

- `POST /bridge/engines/microscribe/analyze` - Analyze a diff file
- `POST /bridge/engines/microscribe/generate-pr` - Generate PR template from diff

### MicroLogician

- `POST /bridge/engines/micrologician/analyze` - Analyze log file
- `POST /bridge/engines/micrologician/security` - Get security intelligence
- `POST /bridge/engines/micrologician/performance` - Get performance metrics

---

## Configuration

### Environment Variables

```bash
# Enable/disable Sovereign Engines
export SOVEREIGN_ENGINES_ENABLED=true

# License key (for production)
export SOVEREIGN_LICENSE_KEY="your-license-key"

# Bridge resonance level (0.0-1.0)
export BRIDGE_RESONANCE=0.99

# Minimum resonance threshold
export SOVEREIGN_MIN_RESONANCE=0.95
```

### Sovereign Policy

Edit `.forge/sovereign_policy.json` to configure:

- Protected routes
- Security thresholds
- Feature flags
- Integration settings

---

## Analysis Modes

The engines operate in different modes based on **bridge resonance**:

| Mode     | Resonance | Features                           |
|----------|-----------|-------------------------------------|
| QUANTUM  | ≥ 0.99    | Full quantum analysis, maximum security |
| DEEP     | ≥ 0.95    | Enhanced analysis, deep validation |
| STANDARD | < 0.95    | Basic analysis, standard checks    |

---

## Security Levels

### MicroScribe Security Levels

- **CRITICAL** - Immediate action required (e.g., exposed credentials)
- **HIGH** - Security review required (e.g., code execution patterns)
- **MEDIUM** - Review recommended (e.g., deprecated APIs)
- **LOW** - Minor concerns (e.g., debug statements)
- **NONE** - No security concerns detected

### MicroLogician Threat Levels

- **CRITICAL** - Credential exposure, private key leaks
- **HIGH** - Injection attacks, authentication failures
- **MEDIUM** - Deprecated code, insecure connections
- **LOW** - Warnings, debug messages

---

## Testing

### Run Unit Tests

```bash
# All tests
pytest bridge_backend/tests/test_sovereign_guard.py \
       bridge_backend/tests/test_micro_scribe.py \
       bridge_backend/tests/test_micro_logician.py -v

# Specific engine
pytest bridge_backend/tests/test_micro_scribe.py -v
```

### Run Verification Script

```bash
python scripts/verify_sovereign_engines.py
```

### Run API Smoke Tests

```bash
# Start server first
uvicorn bridge_backend.main:app --reload

# In another terminal
python scripts/smoke_test_sovereign_engines.py
```

---

## Examples

### Analyzing Git Diffs

```python
from bridge_backend.bridge_engines.micro_scribe import SovereignMicroScribe
import subprocess

# Get diff from git
diff = subprocess.check_output(["git", "diff", "HEAD~1"]).decode()

# Analyze
engine = SovereignMicroScribe()
analysis = engine.analyze_diff(diff)

# Generate PR
if analysis.risk_level.value in ["HIGH", "CRITICAL"]:
    print("⚠️ Security concerns detected!")
    for finding in analysis.security_findings:
        print(f"  - {finding}")

pr = engine.generate_pr(analysis, "My Feature", "Implements XYZ")
print(f"PR Title: {pr.title}")
print(f"Labels: {', '.join(pr.labels)}")
```

### Analyzing Application Logs

```python
from bridge_backend.bridge_engines.micro_logician import SovereignMicroLogician

# Read logs
with open("/var/log/app.log") as f:
    logs = f.read()

# Analyze
engine = SovereignMicroLogician()
analysis = engine.analyze_logs(logs)

# Report findings
print(f"Mode: {analysis.mode}")
print(f"Confidence: {analysis.confidence}")
print(f"Error Rate: {analysis.performance_metrics.error_rate:.2%}")

for finding in analysis.security_findings:
    print(f"\n{finding.threat_level}: {finding.description}")
    print(f"Recommendation: {finding.recommendation}")
```

---

## License

See [SOVEREIGN_LICENSE.md](./SOVEREIGN_LICENSE.md) for licensing details.

**Bridge-Integrated Perpetual License v1.0.0**

- ✅ Enterprise deployment permitted
- ✅ Integration within SR-AIbridge ecosystem
- ✅ Modification for bridge-native operations
- ❌ Standalone deployment prohibited

---

## Support

For issues, questions, or enterprise support:

- GitHub Issues: [SR-AIbridge Issues](https://github.com/kswhitlock9493-jpg/SR-AIbridge-/issues)
- Documentation: See inline code documentation

---

## Changelog

### Version 1.0.0 (2025-11-05)

**Initial Release**

- ✨ Sovereign Compliance Guard with quantum-resistant validation
- ✨ Sovereign MicroScribe Engine with diff analysis and PR generation
- ✨ Sovereign MicroLogician Engine with log intelligence
- ✨ FastAPI routes with file upload support
- ✨ Comprehensive test suite (34 tests)
- ✨ Deployment verification scripts
- ✨ Sovereign policy configuration system

---

**Built with ❤️ for the SR-AIbridge ecosystem**
