# Steward-EnvRecon Integration Guide

## Overview

The Env Steward engine now integrates directly with EnvRecon to provide comprehensive JSON reports of environment variable drift across all platforms (Render, Netlify, GitHub).

## Usage

### Read-Only Mode (Default)

Run the Steward diff endpoint to get a complete JSON report of what's missing in each environment:

```bash
# Enable Steward in read-only mode
export STEWARD_ENABLED=true
export STEWARD_OWNER_HANDLE=kswhitlock9493-jpg

# Run diff via API endpoint
curl -X POST "http://localhost:8000/api/steward/diff?providers=render,netlify,github&dry_run=true"
```

### JSON Report Format

The diff endpoint now returns an enhanced `DiffReport` with the following structure:

```json
{
  "has_drift": true,
  "providers": ["render", "netlify", "github"],
  "changes": [
    {
      "key": "SECRET_KEY",
      "old_value": null,
      "new_value": "<from_local>",
      "action": "create",
      "is_secret": true
    }
  ],
  "missing_in_render": [
    "SECRET_KEY",
    "DATABASE_URL",
    "API_KEY"
  ],
  "missing_in_netlify": [
    "SECRET_KEY",
    "DATABASE_URL"
  ],
  "missing_in_github": [
    "SECRET_KEY",
    "API_KEY"
  ],
  "extra_in_render": [],
  "extra_in_netlify": [],
  "conflicts": {},
  "summary": {
    "total_keys": 16,
    "local_count": 16,
    "render_count": 13,
    "netlify_count": 14,
    "github_count": 15
  },
  "timestamp": "2025-10-11T18:30:00.000000"
}
```

### Field Descriptions

- **has_drift**: `boolean` - True if any drift detected
- **providers**: `string[]` - List of providers checked
- **changes**: `EnvVarChange[]` - Detailed list of required changes
  - **key**: Variable name
  - **old_value**: Current value (null if missing)
  - **new_value**: Proposed value (from local .env)
  - **action**: "create", "update", or "delete"
  - **is_secret**: Whether the variable is a secret (API key, token, etc.)
- **missing_in_render**: `string[]` - Variables missing in Render
- **missing_in_netlify**: `string[]` - Variables missing in Netlify
- **missing_in_github**: `string[]` - Variables missing in GitHub
- **extra_in_render**: `string[]` - Variables in Render but not local
- **extra_in_netlify**: `string[]` - Variables in Netlify but not local
- **conflicts**: `object` - Variables with conflicting values across platforms
- **summary**: Summary statistics
  - **total_keys**: Total unique variables tracked
  - **local_count**: Count in local .env files
  - **render_count**: Count in Render
  - **netlify_count**: Count in Netlify
  - **github_count**: Count in GitHub
- **timestamp**: ISO 8601 timestamp of report generation

## Integration Details

### How It Works

1. **Steward's `diff()` method** calls EnvRecon's `reconcile()` method
2. **EnvRecon** fetches environment variables from:
   - Local .env files
   - Render API (if credentials configured)
   - Netlify API (if credentials configured)
   - GitHub Secrets API (if credentials configured)
3. **EnvRecon** analyzes drift and generates a comprehensive report
4. **Steward** converts the EnvRecon report into a DiffReport with:
   - Missing variables per platform
   - Conflicts across platforms
   - Summary statistics
   - Actionable change list

### Secret Detection

Steward automatically identifies secrets based on variable names containing:
- SECRET
- KEY
- TOKEN
- PASSWORD
- API_KEY
- AUTH
- CREDENTIAL
- PRIVATE
- BEARER

Variables identified as secrets are marked with `is_secret: true` in the changes list.

## Example: Using the JSON Report

### Python Script

```python
import asyncio
import json
from bridge_backend.engines.steward.core import steward

async def get_drift_report():
    # Run diff
    diff = await steward.diff(["render", "netlify", "github"], dry_run=True)
    
    # Convert to dict
    report = diff.model_dump()
    
    # Save to file
    with open("drift_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Show summary
    print(f"Missing in Render: {len(report['missing_in_render'])}")
    print(f"Missing in Netlify: {len(report['missing_in_netlify'])}")
    print(f"Missing in GitHub: {len(report['missing_in_github'])}")
    
    return report

# Run
asyncio.run(get_drift_report())
```

### Shell Script

```bash
#!/bin/bash

# Get drift report via API
curl -X POST "http://localhost:8000/api/steward/diff?dry_run=true" \
  -H "Content-Type: application/json" \
  > drift_report.json

# Extract missing variables for each platform
echo "Missing in Render:"
jq -r '.missing_in_render[]' drift_report.json

echo -e "\nMissing in Netlify:"
jq -r '.missing_in_netlify[]' drift_report.json

echo -e "\nMissing in GitHub:"
jq -r '.missing_in_github[]' drift_report.json
```

## Benefits

1. **Single Command**: Get comprehensive drift report with one API call
2. **JSON Format**: Machine-readable, easy to parse and automate
3. **Per-Platform Breakdown**: See exactly what's missing where
4. **Secret Detection**: Automatically identifies sensitive variables
5. **Summary Statistics**: Quick overview of environment health
6. **Read-Only Safe**: No changes made, just reporting
7. **Integration Ready**: Works with existing Steward security model

## Configuration

### Required Environment Variables

```bash
# Enable Steward
STEWARD_ENABLED=true
STEWARD_OWNER_HANDLE=kswhitlock9493-jpg

# Optional: Provider credentials for live data
RENDER_API_KEY=<your-key>
RENDER_SERVICE_ID=<your-service-id>
NETLIFY_AUTH_TOKEN=<your-token>
NETLIFY_SITE_ID=<your-site-id>
GITHUB_TOKEN=<your-token>
GITHUB_REPO=owner/repo
```

**Note**: If provider credentials are not configured, the report will show 0 variables for that provider and list all local variables as missing.

## Next Steps

1. **Get the report**: Run `POST /api/steward/diff` to see what's missing
2. **Review the JSON**: Analyze which variables need to be added to each platform
3. **Manual fix** (for now): Add missing variables through platform dashboards
4. **Future**: Use Steward's write mode to automatically sync environments

## See Also

- [STEWARD_QUICK_REF.md](STEWARD_QUICK_REF.md) - Full Steward API reference
- [ENVRECON_QUICK_REF.md](ENVRECON_QUICK_REF.md) - EnvRecon engine details
- [V196L_STEWARD_SUMMARY.md](V196L_STEWARD_SUMMARY.md) - Steward implementation summary
