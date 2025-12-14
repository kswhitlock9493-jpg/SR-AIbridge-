# Compliance Integration Quick Reference

## Overview
The Autonomy Engine integrates three validation engines to ensure all autonomous tasks start with original, open-source compliant code:
- **License Scanner** - Validates files against policy (blocks GPL/AGPL, allows MIT/Apache/BSD)
- **Copyright Detection** - Uses counterfeit detection to identify code similarity (blocks >94%, flags >60%)
- **LOC Tracking** - Counts lines of code by file extension for metrics

## API Endpoints

### Create Task with Compliance
```bash
POST /engines/autonomy/task
```

**Request Body:**
```json
{
  "project": "my_project",
  "captain": "Kyle",
  "objective": "build_feature",
  "permissions": {"read": ["src"], "write": ["docs"]},
  "mode": "screen",
  "verify_originality": true,
  "files": ["src/main.py", "src/utils.py"]  // Optional
}
```

**Response:**
```json
{
  "task": {
    "id": "task-uuid",
    "compliance_check": {
      "state": "ok|flagged|blocked|error",
      "license": {...},
      "counterfeit": [...],
      "timestamp": "2025-10-11T06:37:58Z"
    },
    "loc_metrics": {
      "total_lines": 1234,
      "total_files": 15,
      "by_type": {".py": {"files": 10, "lines": 980}}
    },
    "originality_verified": true
  }
}
```

### Get Compliance Validation
```bash
GET /engines/autonomy/task/{task_id}/compliance
```

**Response:**
```json
{
  "compliance_validation": {
    "compliance_state": {
      "state": "ok|flagged|blocked|error",
      "safe_to_proceed": true|false
    },
    "compliance_check": {...},
    "originality_verified": true|false
  }
}
```

### Update LOC Metrics
```bash
POST /engines/autonomy/task/{task_id}/loc
```

**Response:**
```json
{
  "loc_metrics": {
    "total_lines": 1234,
    "total_files": 15,
    "by_type": {".py": {"files": 10, "lines": 980}},
    "timestamp": "2025-10-11T06:37:58Z"
  }
}
```

## Compliance States

| State | Meaning | Safe to Proceed? | originality_verified |
|-------|---------|------------------|---------------------|
| ✅ ok | No issues | ✅ Yes | true |
| ⚠️ flagged | Review needed | ⚠️ Yes (with caution) | false |
| 🚫 blocked | Policy violation | ❌ No | false |
| ❌ error | Scan failed | ⚠️ Maybe | false |

## Configuration

Via `scan_policy.yaml`:
```yaml
blocked_licenses: ["GPL-2.0", "GPL-3.0", "AGPL-3.0"]
allowed_licenses: ["MIT", "Apache-2.0", "BSD-3-Clause"]
thresholds:
  counterfeit_confidence_block: 0.94  # Block if >94% similar
  counterfeit_confidence_flag: 0.60   # Flag if >60% similar
```

## Usage Example

```python
from bridge_backend.bridge_core.engines.autonomy.service import AutonomyEngine

# Create engine
engine = AutonomyEngine()

# Create task with compliance validation (default)
task = engine.create_task(
    project="my_project",
    captain="Kyle",
    objective="build_feature",
    permissions={"read": ["src"], "write": ["docs"]},
    verify_originality=True,  # Default
    files=["src/main.py"]     # Optional: specific files
)

# Check compliance state
state = task.compliance_check["state"]  # "ok", "flagged", "blocked", or "error"
safe = task.originality_verified       # True if state == "ok"

# Get compliance validation later
validation = engine.get_compliance_validation(task.id)
safe_to_proceed = validation["compliance_state"]["safe_to_proceed"]

# Update LOC metrics
loc = engine.update_task_loc(task.id)
```

## Disable Compliance (if needed)

```python
# Disable per task
task = engine.create_task(..., verify_originality=False)
```

## Benefits
- 🛡️ **Security**: Prevents accidental code theft via counterfeit detection
- 📜 **Compliance**: Ensures proper open-source licensing
- 📊 **Metrics**: Automatic LOC tracking and project growth monitoring
- 🔍 **Transparency**: Full audit trail stored in vault
- 🤖 **Automation**: Runs automatically on every task creation
- ✅ **Originality**: Guarantees original, open-source compliant code
