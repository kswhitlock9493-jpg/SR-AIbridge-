# Compliance Integration Quick Reference

## What's New?

✅ **Anti-Copyright + Compliance + LOC + Autonomy = Secure Autonomous Work**

The Autonomy Engine now automatically validates:
- Copyright originality (counterfeit detection)
- License compliance (blocked/allowed licenses)
- LOC metrics (lines of code tracking)

## Quick Commands

### Create Task with Compliance (Default)
```python
from bridge_core.engines.autonomy import AutonomyEngine

engine = AutonomyEngine()
task = engine.create_task(
    project="my_project",
    captain="Kyle",
    objective="build_feature",
    permissions={"read": ["src"]},
    files=["src/main.py"]  # Optional
)

# Task automatically validated for compliance
print(task.compliance_validation)
```

### Check Compliance State
```python
validation = engine.get_compliance_validation(task_id)
state = validation["compliance_state"]["state"]
# Returns: "compliant", "flagged", or "blocked"
```

### Update LOC Metrics
```python
engine.update_task_loc(task_id, {
    "total_lines": 1500,
    "files_counted": 10,
    "by_extension": {".py": 1200, ".js": 300}
})
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/engines/autonomy/task` | POST | Create task with compliance |
| `/engines/autonomy/task/{id}/compliance` | GET | Get compliance validation |
| `/engines/autonomy/task/{id}/loc` | POST | Update LOC metrics |

## Compliance States

| State | Meaning | Action |
|-------|---------|--------|
| `compliant` | ✅ All checks passed | Proceed |
| `flagged` | ⚠️ Potential issues | Review & proceed |
| `blocked` | 🚫 Critical violations | Do not proceed |

## What Gets Checked?

### 1. License Scan
- Detects licenses in files
- Blocks: GPL-2.0, GPL-3.0, AGPL-3.0
- Allows: MIT, Apache-2.0, BSD-3-Clause

### 2. Copyright Check
- Counterfeit detection (similarity matching)
- Block threshold: 94% similarity
- Flag threshold: 60% similarity

### 3. LOC Counting
- Total lines of code
- Breakdown by file extension
- File count

## Configuration

Edit `scan_policy.yaml`:
```yaml
blocked_licenses: ["GPL-2.0", "GPL-3.0", "AGPL-3.0"]
allowed_licenses: ["MIT", "Apache-2.0", "BSD-3-Clause"]
thresholds:
  counterfeit_confidence_block: 0.94
  counterfeit_confidence_flag: 0.6
```

## Validation Result Structure

```json
{
  "compliance_state": {
    "state": "compliant",
    "license_compliant": true,
    "copyright_original": true,
    "safe_to_proceed": true
  },
  "license_scan": {
    "compliant": true,
    "violations": []
  },
  "copyright_check": {
    "original": true,
    "suspicious_matches": []
  },
  "loc_metrics": {
    "total_lines": 1250,
    "by_extension": {".py": 1000}
  }
}
```

## Vault Storage

- **Task Contracts**: `vault/autonomy/{task_id}.json`
- **Compliance Details**: `vault/autonomy/compliance/{task_id}.json`

## Testing

```bash
# Run compliance tests
cd bridge_backend
python3 tests/test_compliance_integration.py

# Run existing autonomy tests
python3 -m pytest tests/test_autonomy_engine.py
```

## Disable Compliance (Not Recommended)

```python
# Disable for engine
engine = AutonomyEngine(enable_compliance=False)

# Or per task
task = engine.create_task(..., validate_compliance=False)
```

## Benefits Summary

🛡️ **Security**: Prevents accidental code theft  
📜 **Compliance**: Ensures proper licensing  
📊 **Metrics**: Tracks code growth  
🔍 **Transparency**: Full audit trail  
🤖 **Automation**: Runs on every task  

## Integration Flow

```
Task Creation
    ↓
Compliance Validation
    ├─ License Scan
    ├─ Copyright Check  
    └─ LOC Count
    ↓
Evaluate State
    ├─ Compliant → Proceed
    ├─ Flagged → Review
    └─ Blocked → Stop
    ↓
Store in Vault
    ↓
Task Execution
```

## Key Files

| File | Purpose |
|------|---------|
| `compliance_validator.py` | Core validation logic |
| `service.py` | Enhanced AutonomyEngine |
| `routes.py` | API endpoints |
| `test_compliance_integration.py` | Tests |
| `scan_policy.yaml` | Configuration |

## See Also

- [Full Integration Guide](COMPLIANCE_INTEGRATION_GUIDE.md)
- [License Scanner](bridge_backend/utils/license_scanner.py)
- [Counterfeit Detector](bridge_backend/utils/counterfeit_detector.py)
- [LOC Counter](count_loc.py)
