# Compliance Integration for Autonomy Engine

## Overview

The Autonomy Engine has been enhanced with integrated compliance validation, combining:
- **Anti-Copyright Engine** (counterfeit_detector.py) - Detects potential copyright violations
- **Compliance Engine** (license_scanner.py) - Validates license compliance
- **LOC Engine** (count_loc.py) - Tracks lines of code

This ensures all autonomous tasks start with original, open-source compliant code and nothing is accidentally stolen.

## Architecture

### New Components

1. **ComplianceValidator** (`bridge_backend/bridge_core/engines/autonomy/compliance_validator.py`)
   - Validates compliance for autonomous tasks
   - Runs license scans, copyright checks, and LOC counting
   - Evaluates overall compliance state
   - Stores validation records in vault

2. **Enhanced AutonomyEngine** (`bridge_backend/bridge_core/engines/autonomy/service.py`)
   - Integrated ComplianceValidator
   - Automatic compliance validation on task creation
   - LOC tracking for tasks
   - Compliance state accessible via API

3. **Updated API Routes** (`bridge_backend/bridge_core/engines/autonomy/routes.py`)
   - `/engines/autonomy/task` - Creates tasks with optional compliance validation
   - `/engines/autonomy/task/{task_id}/compliance` - Retrieves compliance validation
   - `/engines/autonomy/task/{task_id}/loc` - Updates LOC metrics

### Enhanced TaskContract

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
    compliance_validation: Optional[Dict] = None  # NEW: Compliance results
```

## How It Works

### 1. Task Creation with Compliance

When a task is created, the AutonomyEngine:

```python
task = engine.create_task(
    project="my_project",
    captain="Kyle",
    objective="implement_feature",
    permissions={"read": ["src"], "write": ["src"]},
    mode="screen",
    files=["src/main.py", "src/utils.py"],  # Optional: specific files to check
    validate_compliance=True  # Default: True
)
```

The system automatically:
1. Scans files for license compliance
2. Checks for copyright violations using counterfeit detection
3. Counts lines of code
4. Evaluates compliance state
5. Stores validation in vault

### 2. Compliance Validation Result

The compliance validation includes:

```json
{
  "task_id": "uuid-here",
  "project": "my_project",
  "timestamp": "2025-10-11T06:00:00Z",
  "license_scan": {
    "compliant": true,
    "licenses": {"MIT": 5, "Apache-2.0": 2},
    "files_scanned": 7,
    "violations": []
  },
  "copyright_check": {
    "original": true,
    "files_checked": 7,
    "suspicious_matches": [],
    "flagged_matches": []
  },
  "loc_metrics": {
    "total_lines": 1250,
    "files_counted": 7,
    "by_extension": {".py": 1000, ".js": 250}
  },
  "compliance_state": {
    "state": "compliant",  // "compliant" | "flagged" | "blocked"
    "reason": "all_checks_passed",
    "license_compliant": true,
    "copyright_original": true,
    "safe_to_proceed": true
  }
}
```

### 3. Compliance States

- **compliant**: All checks passed, safe to proceed
- **flagged**: Some potential issues (e.g., flagged matches), review recommended but can proceed
- **blocked**: Critical violations (e.g., blocked license, high-confidence copyright match), should not proceed

### 4. LOC Tracking

Update LOC metrics during or after task execution:

```python
engine.update_task_loc(task_id, {
    "total_lines": 1500,
    "files_counted": 10,
    "by_extension": {".py": 1200, ".js": 300}
})
```

## API Usage

### Create Task with Compliance

```bash
POST /engines/autonomy/task
{
  "project": "my_project",
  "captain": "Kyle",
  "objective": "implement_feature",
  "permissions": {"read": ["src"]},
  "mode": "screen",
  "files": ["src/main.py"],
  "validate_compliance": true
}
```

### Get Compliance Validation

```bash
GET /engines/autonomy/task/{task_id}/compliance
```

### Update LOC Metrics

```bash
POST /engines/autonomy/task/{task_id}/loc
{
  "total_lines": 1500,
  "files_counted": 10,
  "by_extension": {".py": 1200, ".js": 300}
}
```

## Configuration

Compliance validation uses the existing `scan_policy.yaml`:

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
  counterfeit_confidence_block: 0.94  # Block if > 94% match
  counterfeit_confidence_flag: 0.6    # Flag if > 60% match

scan_exclude_paths:
  - node_modules
  - .venv
  - __pycache__
```

## Vault Storage

Compliance validations are stored in:
- `vault/autonomy/{task_id}.json` - Full task contract with compliance
- `vault/autonomy/compliance/{task_id}.json` - Detailed compliance validation

## Testing

Run compliance integration tests:

```bash
cd bridge_backend
python3 tests/test_compliance_integration.py
```

Tests cover:
- ✅ AutonomyEngine with compliance validation
- ✅ ComplianceValidator basic functionality
- ✅ Compliance state evaluation
- ✅ LOC counting
- ✅ License scanning
- ✅ Copyright detection
- ✅ Task persistence
- ✅ API integration

## Benefits

### 1. **Original Code Guarantee**
- Automatic copyright violation detection
- Counterfeit code matching against corpus
- Prevents accidental code theft

### 2. **License Compliance**
- Validates all licenses against policy
- Blocks incompatible licenses (GPL, AGPL)
- Ensures open-source compatibility

### 3. **LOC Tracking**
- Automatic line counting
- Breakdown by file type
- Project growth metrics

### 4. **Audit Trail**
- All validations stored in vault
- Compliance history per task
- Accountability and transparency

### 5. **Safe Autonomy**
- Guardrails prevent non-compliant code
- Automatic validation on task creation
- Manual override available if needed

## Example Workflow

1. **Create Task**: Autonomy engine creates a new task
2. **Auto-Validate**: System automatically runs compliance checks
3. **Evaluate**: Compliance state determines if task can proceed
4. **Track**: LOC metrics updated as work progresses
5. **Audit**: All validation records stored in vault
6. **Review**: Compliance validation accessible via API

## Disabling Compliance

For testing or special cases, compliance can be disabled:

```python
# Disable for entire engine
engine = AutonomyEngine(enable_compliance=False)

# Or disable per task
task = engine.create_task(..., validate_compliance=False)
```

## Future Enhancements

- [ ] Automated remediation suggestions
- [ ] Real-time file watching with continuous validation
- [ ] Integration with CI/CD pipelines
- [ ] Compliance reporting dashboard
- [ ] Custom policy rules per project
- [ ] AI-powered license detection improvements

## Summary

The integration of copyright, compliance, and LOC engines with the autonomy engine ensures:

✅ **Original code** - No accidental theft via counterfeit detection  
✅ **Open-source compliant** - Proper license validation  
✅ **Tracked metrics** - LOC counting integrated  
✅ **Automatic validation** - Runs on task creation  
✅ **Audit trail** - All validations stored in vault  
✅ **Safe autonomy** - Guardrails prevent non-compliant work  

**Result**: All autonomous tasks start original and true open source with nothing accidentally stolen! 🎉
