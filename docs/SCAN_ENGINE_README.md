# Compliance Scan Engine README

## Overview

The SR-AIbridge Compliance Scan Engine provides automated license checking and counterfeit/clone detection for all code changes. This system helps maintain legal compliance and code integrity.

## Features

- **License Detection**: Automatically identifies licenses in code files via SPDX tags and signature matching
- **Counterfeit Detection**: Uses shingling-based similarity analysis to detect potential code clones
- **Policy Enforcement**: Configurable thresholds for blocking or flagging PRs
- **Signed Reports**: Tamper-evident scan results with HMAC signatures
- **UI Dashboard**: Real-time compliance scan panel in the Command Deck

## Policy States

Scan results can have three states:

- **ok**: No policy violations detected
- **flagged**: Potential issues requiring review (based on thresholds)
- **blocked**: Policy violations that prevent merging

## Configuration

Edit `scan_policy.yaml` in the repository root:

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

### License Scanning

The license scanner:
1. Searches for SPDX-License-Identifier tags
2. Matches against known license text signatures
3. Reports findings per file with counts by license type

### Counterfeit Detection

The counterfeit detector:
1. Tokenizes and normalizes code
2. Creates 6-token shingles for similarity hashing
3. Compares against internal corpus using Jaccard similarity
4. Reports matches above threshold

## CI Integration

The GitHub workflow `.github/workflows/scan_pr.yml` runs on:
- Pull request events (opened, synchronize, reopened)
- Pushes to main branch

Set the `SCAN_SIGNING_KEY` secret in your repository settings for production use.

## API Endpoints

- `GET /scans` - List recent scans
- `GET /scans/{scan_id}` - Get detailed scan report

## Security

- Scan reports are cryptographically signed using HMAC-SHA256
- Reports are stored in `bridge_backend/scan_reports/` (excluded from git)
- Signatures can be verified to detect tampering

## Future Enhancements

- Triage endpoint for marking false positives
- Full repository scans (not just changed files)
- LSH indexing for performance at scale
- Integration with relay_mailer for notifications
