# Autonomy Engine - Originality & Compliance Integration

## Overview

The Autonomy Engine has been enhanced with integrated anti-copyright and compliance checking capabilities, ensuring that all autonomous tasks start with verified original and properly licensed code.

## Features

### 1. Anti-Copyright Engine Integration

The autonomy engine now automatically runs compliance scans when creating tasks to ensure:
- **License Compliance**: Detects and blocks use of incompatible licenses (GPL, AGPL)
- **Originality Verification**: Uses counterfeit detection to ensure code is not accidentally copied
- **Policy Enforcement**: Applies configurable thresholds for blocking or flagging suspicious code

### 2. LOC Engine Integration

The autonomy engine now tracks Lines of Code (LOC) metrics for each project:
- **Total Lines**: Count of all code lines in the project
- **Total Files**: Number of source files
- **By Type**: Breakdown by file extension (.py, .js, .ts, etc.)

### 3. Enhanced Task Contracts

All task contracts now include:
```python
{
  "id": "task-uuid",
  "project": "project-name",
  "captain": "captain-name",
  "mode": "screen",
  "permissions": {...},
  "objective": "task objective",
  "status": "pending",
  
  // NEW FIELDS
  "compliance_check": {
    "state": "ok",  // ok | flagged | blocked | error
    "license": {...},
    "counterfeit": [...],
    "timestamp": "2025-10-11T06:37:58Z"
  },
  "loc_metrics": {
    "total_lines": 1234,
    "total_files": 15,
    "by_type": {
      ".py": {"files": 10, "lines": 980},
      ".js": {"files": 5, "lines": 254}
    },
    "timestamp": "2025-10-11T06:37:58Z"
  },
  "originality_verified": true
}
```

## API Usage

### Create Task with Originality Check (Default)

```bash
POST /engines/autonomy/task
{
  "project": "my_project",
  "captain": "Kyle",
  "objective": "Build new feature",
  "permissions": {"read": ["docs"], "write": ["code"]},
  "mode": "screen",
  "verify_originality": true  // default
}
```

### Create Task without Originality Check

```bash
POST /engines/autonomy/task
{
  "project": "my_project",
  "captain": "Kyle",
  "objective": "Build new feature",
  "permissions": {"read": ["docs"], "write": ["code"]},
  "mode": "screen",
  "verify_originality": false  // skip compliance checks
}
```

## Compliance States

### OK
- No blocked licenses detected
- No counterfeit code above threshold
- Task is safe to execute
- `originality_verified = true`

### Flagged
- Potential issues detected
- Similarity score between 0.60 and 0.94
- Review recommended but task can proceed
- `originality_verified = false`

### Blocked
- Blocked license detected (GPL, AGPL)
- High similarity score (>= 0.94)
- Task should not proceed without review
- `originality_verified = false`

### Error
- Compliance check failed
- Task can still be created but verification incomplete
- `originality_verified = false`

## Configuration

Compliance policy is controlled by `scan_policy.yaml`:

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
  counterfeit_confidence_block: 0.94
  counterfeit_confidence_flag: 0.60

max_file_size_bytes: 750000

scan_exclude_paths:
  - node_modules
  - .venv
  - __pycache__
  - bridge_backend/scan_reports
```

## How It Works

### Compliance Check Process

1. **File Discovery**: Scans project directory for source files
2. **License Detection**: 
   - Checks for SPDX license identifiers
   - Matches against known license signatures
   - Reports findings per file
3. **Counterfeit Detection**:
   - Tokenizes and normalizes code
   - Creates 6-token shingles
   - Compares against internal corpus using Jaccard similarity
   - Flags matches above threshold
4. **Policy Evaluation**:
   - Checks for blocked licenses
   - Evaluates similarity scores against thresholds
   - Returns state: ok/flagged/blocked

### LOC Metrics Process

1. **File Enumeration**: Finds all source files in project directory
2. **Line Counting**: Counts lines per file
3. **Categorization**: Groups by file extension
4. **Aggregation**: Totals and categorizes metrics

## Testing

Run the integrated tests:

```bash
cd bridge_backend
pytest tests/test_autonomy_engine.py::test_task_with_originality_check -v
pytest tests/test_autonomy_engine.py::test_task_without_originality_check -v
pytest tests/test_autonomy_engine.py::test_task_compliance_and_loc_metrics -v
```

## Integration Points

### With Compliance Scan Engine
- Uses `bridge_backend.utils.license_scanner`
- Uses `bridge_backend.utils.counterfeit_detector`
- Uses `bridge_backend.utils.scan_policy`

### With LOC Counter
- Integrates LOC counting logic from `count_loc.py`
- Provides per-project metrics
- Tracks code growth over time

## Benefits

1. **Automatic Copyright Protection**: No accidental code theft
2. **License Compliance**: Ensures open source compatibility
3. **Code Metrics**: Track project size and growth
4. **Trust & Transparency**: Verifiable originality for all autonomous work
5. **Policy Enforcement**: Configurable rules for code quality

## Future Enhancements

- Real-time monitoring of code originality during task execution
- Integration with external license databases
- Enhanced similarity detection with LSH indexing
- Automated remediation suggestions for flagged code
- Historical tracking of compliance over time

## License

This integration is part of the SR-AIbridge project and follows the same MIT license.
