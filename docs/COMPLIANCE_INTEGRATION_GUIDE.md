# Compliance Integration Guide

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Compliance States](#compliance-states)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Overview

This integration combines three critical validation engines into the Autonomy Engine:

1. **License Scanner** (`bridge_backend/utils/license_scanner.py`)
   - Detects SPDX license identifiers
   - Matches license signatures
   - Reports findings per file

2. **Counterfeit Detector** (`bridge_backend/utils/counterfeit_detector.py`)
   - 6-token shingling algorithm
   - Jaccard similarity comparison
   - Configurable thresholds (0.60 flag, 0.94 block)

3. **LOC Engine** (`count_loc.py`)
   - Multi-language support (.py, .js, .ts, .jsx, .tsx)
   - Project-level aggregation
   - Type-based categorization

## Architecture

### Data Flow
```
User creates task
    ↓
verify_originality=true (default)
    ↓
Autonomy Engine scans project
    ↓
┌─────────────────────┐
│ License Scanner     │ → Detect licenses
│ Counterfeit Detector│ → Check originality
│ LOC Counter        │ → Count lines
└─────────────────────┘
    ↓
Policy Evaluation
    ↓
┌─────────────────────┐
│ Task Contract       │
│  + compliance_check │
│  + loc_metrics      │
│  + originality_verified │
└─────────────────────┘
    ↓
Sealed to vault/autonomy/
```

### Components

**AutonomyEngine** (`bridge_backend/bridge_core/engines/autonomy/service.py`)
- `_check_compliance()` - Runs license scan and counterfeit detection
- `_get_loc_metrics()` - Counts lines of code
- `create_task()` - Creates task with validation
- `get_compliance_validation()` - Retrieves compliance results
- `update_task_loc()` - Updates LOC metrics

**TaskContract** (dataclass)
```python
@dataclass
class TaskContract:
    id: str
    project: str
    captain: str
    mode: str
    permissions: Dict[str, Any]
    objective: str
    created_at: str
    status: str = "pending"
    result: Optional[Dict] = None
    compliance_check: Optional[Dict] = None
    loc_metrics: Optional[Dict] = None
    originality_verified: bool = False
```

## API Reference

### POST /engines/autonomy/task

Create a new autonomy task with integrated compliance validation.

**Parameters:**
- `project` (string, required) - Project name
- `captain` (string, required) - Task captain/owner
- `objective` (string, required) - Task objective
- `permissions` (object, required) - Permission dictionary
- `mode` (string, optional) - Task mode: "screen", "connector", or "hybrid" (default: "screen")
- `verify_originality` (boolean, optional) - Run compliance checks (default: true)
- `files` (array[string], optional) - Specific files to scan

**Response:**
```json
{
  "task": {
    "id": "uuid",
    "project": "project_name",
    "captain": "captain_name",
    "mode": "screen",
    "permissions": {},
    "objective": "objective",
    "created_at": "2025-10-11T06:37:58Z",
    "status": "pending",
    "result": null,
    "compliance_check": {
      "state": "ok",
      "license": {
        "files": [...],
        "summary": {"counts_by_license": {...}}
      },
      "counterfeit": [...],
      "timestamp": "2025-10-11T06:37:58Z"
    },
    "loc_metrics": {
      "total_lines": 1234,
      "total_files": 15,
      "by_type": {...},
      "timestamp": "2025-10-11T06:37:58Z"
    },
    "originality_verified": true
  }
}
```

### GET /engines/autonomy/task/{task_id}/compliance

Retrieve compliance validation results for a specific task.

**Response:**
```json
{
  "compliance_validation": {
    "compliance_state": {
      "state": "ok",
      "safe_to_proceed": true
    },
    "compliance_check": {...},
    "originality_verified": true
  }
}
```

### POST /engines/autonomy/task/{task_id}/loc

Update LOC metrics for a specific task.

**Response:**
```json
{
  "loc_metrics": {
    "total_lines": 1234,
    "total_files": 15,
    "by_type": {...},
    "timestamp": "2025-10-11T06:37:58Z"
  }
}
```

## Usage Examples

### Basic Task Creation

```python
from bridge_backend.bridge_core.engines.autonomy.service import AutonomyEngine

engine = AutonomyEngine()

task = engine.create_task(
    project="my_project",
    captain="Kyle",
    objective="build_feature",
    permissions={"read": ["src"], "write": ["docs"]},
    mode="screen"
)

# Check if task is safe to proceed
if task.originality_verified:
    print("✅ Task is verified as original")
else:
    print(f"⚠️ Task compliance state: {task.compliance_check['state']}")
```

### Scan Specific Files

```python
task = engine.create_task(
    project="my_project",
    captain="Kyle",
    objective="scan_specific_files",
    permissions={"read": ["src"]},
    files=["src/main.py", "src/utils.py"]
)
```

### Disable Compliance (if needed)

```python
task = engine.create_task(
    project="my_project",
    captain="Kyle",
    objective="quick_task",
    permissions={"read": ["tmp"]},
    verify_originality=False  # Skip compliance checks
)
```

### Retrieve Compliance Later

```python
# Get compliance validation for a task
validation = engine.get_compliance_validation(task.id)

if validation["compliance_state"]["safe_to_proceed"]:
    print("✅ Safe to proceed")
else:
    print(f"⚠️ State: {validation['compliance_state']['state']}")
```

### Update LOC Metrics

```python
# Refresh LOC metrics for a task
loc_metrics = engine.update_task_loc(task.id)
print(f"Total lines: {loc_metrics['total_lines']}")
```

## Compliance States

### OK ✅
- No blocked licenses detected
- No counterfeit code above threshold
- Task is safe to execute
- `originality_verified = true`

### Flagged ⚠️
- Potential issues detected
- Similarity score between 0.60 and 0.94
- Review recommended but task can proceed
- `originality_verified = false`

### Blocked 🚫
- Blocked license detected (GPL, AGPL)
- High similarity score (>= 0.94)
- Task should not proceed without review
- `originality_verified = false`

### Error ❌
- Compliance check failed
- Task can still be created but verification incomplete
- `originality_verified = false`

## Configuration

### Policy File: `scan_policy.yaml`

```yaml
blocked_licenses:
  - GPL-2.0
  - GPL-3.0
  - AGPL-3.0

allowed_licenses:
  - MIT
  - Apache-2.0
  - BSD-3-Clause

thresholds:
  counterfeit_confidence_block: 0.94  # Block if similarity >= 94%
  counterfeit_confidence_flag: 0.60   # Flag if similarity >= 60%

max_file_size_bytes: 750000

scan_exclude_paths:
  - node_modules
  - .venv
  - __pycache__
  - bridge_backend/scan_reports
```

### Environment Variables

None required. The integration uses existing configurations.

## Testing

### Run Tests

```bash
# Run all autonomy engine tests
cd /home/runner/work/SR-AIbridge-/SR-AIbridge-
PYTHONPATH=. python3 -m pytest bridge_backend/tests/test_autonomy_engine.py -v
```

### Test Coverage

The test suite includes:
- ✅ Task creation and update
- ✅ Different task modes (screen, connector, hybrid)
- ✅ Task listing
- ✅ Originality verification on/off
- ✅ Compliance check structure validation
- ✅ LOC metrics structure validation
- ✅ GET /task/{id}/compliance endpoint
- ✅ POST /task/{id}/loc endpoint
- ✅ Files parameter support
- ✅ Error handling (404 for non-existent tasks)

## Troubleshooting

### Issue: Compliance check returns "error" state

**Cause:** Missing dependencies or file access issues

**Solution:**
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check file permissions in project directory
3. Verify `scan_policy.yaml` exists

### Issue: High false-positive rate in counterfeit detection

**Cause:** Threshold too low

**Solution:**
Adjust threshold in `scan_policy.yaml`:
```yaml
thresholds:
  counterfeit_confidence_flag: 0.70  # Increase from 0.60
```

### Issue: Task creation is slow

**Cause:** Large project with many files

**Solution:**
1. Use `files` parameter to scan specific files only
2. Or disable compliance for non-critical tasks: `verify_originality=False`

### Issue: LOC metrics show 0 lines

**Cause:** Project path doesn't exist or no files found

**Solution:**
1. Verify project exists in `bridge_backend/bridge_core/engines/{project}/`
2. Ensure files have supported extensions (.py, .js, .ts, .jsx, .tsx)

## License

This integration is part of SR-AIbridge and follows the project's license.
