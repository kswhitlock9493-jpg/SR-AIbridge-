# Self-Test Report Schema

## v1.9.7j — JSON Schema for Self-Test Reports

This document defines the JSON schema for Bridge self-test diagnostic reports.

## Report Structure

### Root Schema

```json
{
  "test_id": "string",
  "summary": {
    "engines_total": "number",
    "engines_verified": "number",
    "autoheal_invocations": "number",
    "status": "string",
    "runtime_ms": "number"
  },
  "events": [
    {
      "engine": "string",
      "action": "string",
      "result": "string",
      "strategy": "string (optional)",
      "attempts": "number (optional)",
      "duration_seconds": "number (optional)",
      "error": "string (optional)"
    }
  ],
  "timestamp": "string (ISO 8601)",
  "error": "string (optional)"
}
```

## Field Definitions

### test_id

- **Type**: string
- **Format**: `bridge_selftest_YYYYMMDD_HHMMSS`
- **Example**: `bridge_selftest_20241012_123456`
- **Description**: Unique identifier for each test run

### summary

Container for test summary metrics.

#### summary.engines_total

- **Type**: number
- **Example**: `31`
- **Description**: Total number of engines tested

#### summary.engines_verified

- **Type**: number
- **Example**: `31`
- **Description**: Number of engines that passed verification

#### summary.autoheal_invocations

- **Type**: number
- **Example**: `2`
- **Description**: Number of times auto-healing was triggered

#### summary.status

- **Type**: string
- **Enum**: `["Stable", "Degraded", "Failed"]`
- **Description**: Overall test status
  - `Stable`: All engines verified
  - `Degraded`: Some engines failed but were healed
  - `Failed`: Critical failures that couldn't be healed

#### summary.runtime_ms

- **Type**: number
- **Example**: `482`
- **Description**: Total test runtime in milliseconds

### events

Array of test events, one per engine test or healing action.

#### Event Object

##### event.engine

- **Type**: string
- **Example**: `"Hydra"`
- **Description**: Name of the engine being tested

##### event.action

- **Type**: string
- **Enum**: `["health_check", "repair_patch_applied", "auto_heal_failed", "auto_heal_exhausted", "auto_heal_skipped"]`
- **Description**: Action performed during test

##### event.result

- **Type**: string
- **Enum**: `["✅", "⚠️ auto-heal launched", "✅ certified", "❌ healing failed", "❌ auto-heal disabled"]`
- **Description**: Result of the action

##### event.strategy (optional)

- **Type**: string
- **Enum**: `["arie", "chimera", "cascade", "generic"]`
- **Description**: Healing strategy used (only present for healing events)

##### event.attempts (optional)

- **Type**: number
- **Example**: `1`
- **Description**: Number of healing attempts (only present for healing events)

##### event.duration_seconds (optional)

- **Type**: number
- **Example**: `1.234`
- **Description**: Duration of healing operation (only present for healing events)

##### event.error (optional)

- **Type**: string
- **Example**: `"Configuration drift detected"`
- **Description**: Error message if action failed

### timestamp

- **Type**: string
- **Format**: ISO 8601 (UTC)
- **Example**: `"2024-10-12T12:34:56.789Z"`
- **Description**: Timestamp when test completed

### error (optional)

- **Type**: string
- **Description**: Error message if entire test failed

## Example Reports

### Successful Test (No Healing Required)

```json
{
  "test_id": "bridge_selftest_20241012_123456",
  "summary": {
    "engines_total": 31,
    "engines_verified": 31,
    "autoheal_invocations": 0,
    "status": "Stable",
    "runtime_ms": 350
  },
  "events": [
    {
      "engine": "Truth",
      "action": "health_check",
      "result": "✅"
    },
    {
      "engine": "Cascade",
      "action": "health_check",
      "result": "✅"
    },
    {
      "engine": "Genesis",
      "action": "health_check",
      "result": "✅"
    }
  ],
  "timestamp": "2024-10-12T12:34:56.789Z"
}
```

### Test with Auto-Healing

```json
{
  "test_id": "bridge_selftest_20241012_140000",
  "summary": {
    "engines_total": 31,
    "engines_verified": 31,
    "autoheal_invocations": 2,
    "status": "Stable",
    "runtime_ms": 482
  },
  "events": [
    {
      "engine": "Hydra",
      "action": "health_check",
      "result": "✅"
    },
    {
      "engine": "EnvRecon",
      "action": "health_check",
      "result": "⚠️ auto-heal launched",
      "error": "Configuration drift detected"
    },
    {
      "engine": "EnvRecon",
      "action": "repair_patch_applied",
      "result": "✅ certified",
      "strategy": "arie",
      "attempts": 1,
      "duration_seconds": 1.234
    },
    {
      "engine": "Chimera",
      "action": "health_check",
      "result": "⚠️ auto-heal launched",
      "error": "Build configuration invalid"
    },
    {
      "engine": "Chimera",
      "action": "repair_patch_applied",
      "result": "✅ certified",
      "strategy": "chimera",
      "attempts": 2,
      "duration_seconds": 2.567
    }
  ],
  "timestamp": "2024-10-12T14:00:01.234Z"
}
```

### Test with Failed Healing

```json
{
  "test_id": "bridge_selftest_20241012_160000",
  "summary": {
    "engines_total": 31,
    "engines_verified": 30,
    "autoheal_invocations": 1,
    "status": "Degraded",
    "runtime_ms": 890
  },
  "events": [
    {
      "engine": "Firewall",
      "action": "health_check",
      "result": "⚠️ auto-heal launched",
      "error": "Policy validation failed"
    },
    {
      "engine": "Firewall",
      "action": "auto_heal_exhausted",
      "result": "❌ healing failed",
      "attempts": 3
    }
  ],
  "timestamp": "2024-10-12T16:00:01.890Z"
}
```

### Complete Test Failure

```json
{
  "test_id": "bridge_selftest_20241012_180000",
  "summary": {
    "engines_total": 31,
    "engines_verified": 0,
    "autoheal_invocations": 0,
    "status": "Failed",
    "runtime_ms": 0
  },
  "events": [],
  "error": "Genesis bus unavailable",
  "timestamp": "2024-10-12T18:00:00.123Z"
}
```

## Report Locations

### Individual Reports

Each test run creates a uniquely named report:

```
bridge_backend/logs/selftest_reports/bridge_selftest_YYYYMMDD_HHMMSS.json
```

### Latest Report

The most recent test result is always available at:

```
bridge_backend/logs/selftest_reports/latest.json
```

## Usage

### Reading Reports in Python

```python
import json
from pathlib import Path

# Read latest report
report_path = Path("bridge_backend/logs/selftest_reports/latest.json")
with open(report_path) as f:
    report = json.load(f)

print(f"Status: {report['summary']['status']}")
print(f"Verified: {report['summary']['engines_verified']}/{report['summary']['engines_total']}")
```

### Querying with jq

```bash
# Get test status
jq '.summary.status' bridge_backend/logs/selftest_reports/latest.json

# Count failed engines
jq '.events | map(select(.result | contains("❌"))) | length' bridge_backend/logs/selftest_reports/latest.json

# List all healing events
jq '.events | map(select(.action == "repair_patch_applied"))' bridge_backend/logs/selftest_reports/latest.json
```

## Validation

Reports conform to this schema and can be validated using standard JSON schema validators.

### Schema Validation Example

```python
import json
from jsonschema import validate

schema = {
    "type": "object",
    "required": ["test_id", "summary", "events", "timestamp"],
    "properties": {
        "test_id": {"type": "string"},
        "summary": {
            "type": "object",
            "required": ["engines_total", "engines_verified", "autoheal_invocations", "status", "runtime_ms"],
            "properties": {
                "engines_total": {"type": "number"},
                "engines_verified": {"type": "number"},
                "autoheal_invocations": {"type": "number"},
                "status": {"type": "string", "enum": ["Stable", "Degraded", "Failed"]},
                "runtime_ms": {"type": "number"}
            }
        },
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["engine", "action", "result"],
                "properties": {
                    "engine": {"type": "string"},
                    "action": {"type": "string"},
                    "result": {"type": "string"}
                }
            }
        },
        "timestamp": {"type": "string"}
    }
}

# Validate report
with open("bridge_backend/logs/selftest_reports/latest.json") as f:
    report = json.load(f)
    validate(instance=report, schema=schema)
```
