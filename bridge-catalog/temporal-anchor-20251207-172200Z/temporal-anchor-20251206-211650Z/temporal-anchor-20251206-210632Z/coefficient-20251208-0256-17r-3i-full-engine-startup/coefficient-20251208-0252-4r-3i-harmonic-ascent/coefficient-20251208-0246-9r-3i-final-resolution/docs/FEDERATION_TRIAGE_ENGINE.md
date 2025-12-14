# Federation Triage Engine v1.8.1

## Overview

The Federation Triage Engine provides self-healing mesh capabilities for SR-AIbridge federation endpoints. It detects endpoint/schema/path drift, repairs it in place with guarded writes, and revalidates until healthy.

## Components

### 1. Federation Map (`bridge_backend/federation_map.json`)

Canonical registry of federation endpoints with:
- Endpoint URLs and heartbeat paths
- Schema versions and probe endpoints
- Patch targets (environment variables and cache files)
- Expected HTTP methods

### 2. Network Helper (`.github/scripts/_net.py`)

Utility functions for robust network operations:
- **DNS warm-up**: Pre-resolves hostnames to avoid cold-start failures
- **CA-aware HTTP**: Honors custom certificate authorities via `ACTIONS_CA_BUNDLE`
- **Exponential backoff**: Retries with increasing delays

### 3. Deep-Seek Triage Script (`.github/scripts/deep_seek_triage.py`)

Main auto-repair engine that:
1. Performs DNS warm-up for each federation node
2. Tests heartbeat endpoints and measures latency
3. Probes schema endpoints and compares versions
4. Refreshes local schema caches on drift detection
5. Exercises live routes with exponential backoff
6. Generates non-destructive patch intents for environment updates

### 4. GitHub Actions Workflow (`.github/workflows/federation_deepseek.yml`)

Automated workflow that:
- Runs every 6 hours via cron schedule
- Can be triggered manually via workflow_dispatch
- Uploads detailed repair reports as artifacts
- Fails only if ALL federation nodes fail (not just one)

## Signal Taxonomy

### Health Status
- **PASS**: Node is reachable AND (schema matches OR live call succeeded)
- **FAIL**: Node is unreachable OR (schema mismatch AND live call failed)

### Repair Actions
1. **cache_refreshed**: Local schema cache updated with latest version
2. **live_call_ok@attempt_N**: Route exercised successfully after N attempts
3. **intent:update_env**: Staged environment variable update (requires manual apply)

### Error Signals
- **DNS warmup failed**: Cannot resolve federation hostname
- **HB error**: Heartbeat endpoint unreachable or errored
- **Schema drift**: Version mismatch detected
- **Schema probe error**: Cannot fetch schema information
- **live_call_status**: Unexpected HTTP status from live route
- **live_call_error**: Exception during live route exercise

## Usage

### Running Manually

```bash
# Install dependencies
pip install requests

# Run deep-seek triage
python3 .github/scripts/deep_seek_triage.py

# Check report
cat bridge_backend/diagnostics/federation_repair_report.json
```

### Reading Reports

Reports are uploaded as GitHub Actions artifacts:

1. Go to **Actions** → **Federation Deep-Seek**
2. Select a workflow run
3. Download **federation_repair_report** artifact
4. Extract and review JSON file

Example report structure:

```json
{
  "generated_at": 1760000123,
  "health": {
    "diagnostics_federation": "PASS",
    "bridge_auto_deploy": "PASS",
    "triage_federation": "PASS"
  },
  "details": {
    "triage_federation": {
      "reachable": true,
      "schema_match": false,
      "latency_ms": 142.7,
      "repairs": [
        "cache_refreshed:bridge_backend/.cache/triage_schema.json",
        "live_call_ok@attempt_2",
        "intent:update_env:['FEDERATION_SCHEMA_VERSION_TRIAGE']=>1.7"
      ],
      "errors": ["Schema drift (want 1.7, probe 200); staged patch intent"]
    }
  }
}
```

## Escalation

If a federation node remains in **FAIL** status for more than 3 consecutive cycles:

1. Download the latest repair report artifact
2. Review the `details` section for the failing node
3. Check `errors` array for root cause
4. Apply suggested `intent:update_env` patches if present
5. Manually verify endpoint availability
6. Re-run the workflow to confirm resolution

### Applying Patch Intents

Environment variable updates are staged as intents (not automatically applied). To apply:

1. Review the intent in the report: `intent:update_env:['VAR_NAME']=>new_value`
2. Update the environment variable in your platform dashboard (Render, Netlify, etc.)
3. Restart the affected service
4. Re-run the Federation Deep-Seek workflow
5. Verify the node status changes to **PASS**

## Security

- Only communicates with allowlisted federation domains
- No credentials printed in logs or reports
- Reports contain paths, status codes, and metadata only
- CA certificate verification can be customized via `ACTIONS_CA_BUNDLE`

## Troubleshooting

### All Nodes Failing

Check network connectivity from CI environment:
```bash
curl -I https://diagnostics.sr-aibridge.com/api/heartbeat
curl -I https://bridge.sr-aibridge.com/api/deploy/status
curl -I https://triage.sr-aibridge.com/api/heartbeat
```

### Schema Drift Persists

1. Check if the schema version in `federation_map.json` is outdated
2. Update to match the actual deployed version
3. Commit and push changes
4. Re-run the workflow

### DNS Warm-up Failures

Federation domain may be unreachable. Verify:
- Domain DNS records are properly configured
- No firewall/egress rules blocking access
- Certificate is valid and not expired

## Integration with Existing Systems

This federation triage system complements:

- **Legacy Triage** (`bridge_backend/scripts/`): Detailed schema validation
- **Tools Triage** (`bridge_backend/tools/triage/`): Federation heartbeat aggregation
- **Diagnostics Timeline**: Frontend visibility via DeepScanPanel

The Deep-Seek engine provides a unified, self-healing view across all federation operations.

## Version History

### v1.8.1 (Current)
- Initial release with Deep-Seek + Auto-Repair
- DNS warm-up and CA-aware retries
- Schema cache refresh
- Non-destructive patch intents
- Live route exercise with backoff
- Health classification (fail only if all nodes fail)
