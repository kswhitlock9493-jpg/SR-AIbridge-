# Firewall Watchdog - Copilot Accountability & Audit Logger

## Overview

The Firewall Watchdog is a comprehensive accountability and audit logging system for the SR-AIbridge Copilot environment. It monitors all network access attempts, logs blocked/unknown hosts, and reports events to the Bridge diagnostics API.

## Features

- **DNS Connection Testing**: Verifies connectivity to critical hosts
- **Allowlist Enforcement**: Checks if hosts are in the approved allowlist
- **Event Logging**: Records all firewall events with timestamps
- **Bridge Integration**: Reports events to Bridge diagnostics API
- **Automatic Execution**: Runs as part of Copilot preflight workflow

## Architecture

### Components

1. **`scripts/firewall_watchdog.py`**: Core monitoring script
2. **`.github/workflows/copilot-preflight.yml`**: Workflow integration
3. **`.github/copilot_agent_settings.yml`**: Configuration settings
4. **`logs/copilot_firewall.log`**: Event log file (auto-generated)

### Event Flow

```
Copilot PreFlight Workflow
    ↓
Create Allowlist (.github/allowlist/hosts.txt)
    ↓
Run Firewall Watchdog
    ↓
Test DNS Resolution for Monitored Hosts
    ↓
Log Event (logs/copilot_firewall.log)
    ↓
Report to Bridge (/api/diagnostics)
```

## Configuration

### Monitored Hosts

The following hosts are monitored by default:
- `bridge.sr-aibridge.com`
- `diagnostics.sr-aibridge.com`
- `render.com`
- `api.netlify.com`
- `pypi.org`
- `registry.npmjs.org`

### Allowlist

The allowlist is created during the preflight workflow in `.github/allowlist/hosts.txt`. This file contains approved hosts that Copilot is allowed to access.

### Log Format

Events are logged as JSON objects with the following schema:

```json
{
  "timestamp": "2025-01-15T12:00:00+00:00",
  "host": "example.com",
  "resolved": true,
  "allowed": true,
  "trigger": "preflight-scan"
}
```

**Fields:**
- `timestamp`: ISO 8601 timestamp with timezone
- `host`: The hostname being checked
- `resolved`: Whether DNS resolution succeeded
- `allowed`: Whether the host is in the allowlist
- `trigger`: What triggered the check (e.g., "preflight-scan")

## Usage

### Automatic Execution

The watchdog runs automatically as part of the Copilot preflight workflow on:
- Push to `main` branch
- Pull requests
- Manual workflow dispatch

### Manual Execution

To run the watchdog manually:

```bash
# Ensure allowlist exists
mkdir -p .github/allowlist
echo "example.com" >> .github/allowlist/hosts.txt

# Run watchdog
python3 scripts/firewall_watchdog.py
```

### Environment Variables

- `BRIDGE_URL`: Bridge API base URL (default: `https://sr-aibridge.onrender.com`)

## Bridge API Integration

The watchdog reports events to the Bridge diagnostics API at `/api/diagnostics` with the following payload:

```json
{
  "type": "FIREWALL_EVENT",
  "status": "resolved|blocked",
  "meta": {
    "timestamp": "...",
    "host": "...",
    "resolved": true|false,
    "allowed": true|false,
    "trigger": "..."
  }
}
```

## Output Example

```
======================================================================
🛡️ Running Firewall Watchdog...
📋 Loaded 6 hosts from allowlist
🔍 Monitoring 6 critical hosts

✅ bridge.sr-aibridge.com                   (allowed)
✅ render.com                               (allowed)
✅ api.netlify.com                          (allowed)
✅ pypi.org                                 (allowed)
✅ registry.npmjs.org                       (allowed)
❌ blocked-host.com                         (blocked)
======================================================================
📡 Audit complete. Logs saved to: logs/copilot_firewall.log
```

**Icons:**
- ✅ DNS resolution successful
- ❌ DNS resolution failed

## Testing

Run the test suite:

```bash
python3 bridge_backend/tests/test_firewall_watchdog.py
```

The test suite covers:
- Allowlist loading (empty and with hosts)
- Event logging
- Bridge API reporting
- DNS connection testing
- Full integration test

## Troubleshooting

### No allowlist file

If the allowlist file doesn't exist, the watchdog will continue with an empty allowlist. All hosts will be marked as "blocked".

### Bridge API unavailable

If the Bridge API is unavailable, the watchdog will silently continue without reporting. This prevents workflow failures due to external dependencies.

### DNS resolution failures

DNS resolution failures are normal for hosts that aren't publicly accessible. The watchdog logs these events but continues execution.

## Files Modified/Created

**New Files:**
- `scripts/firewall_watchdog.py`
- `bridge_backend/tests/test_firewall_watchdog.py`
- `docs/FIREWALL_WATCHDOG.md` (this file)

**Modified Files:**
- `.github/workflows/copilot-preflight.yml`
- `.github/copilot_agent_settings.yml`
- `.gitignore`

## Version History

- **v1.1** (2025-01-15): Initial implementation
  - DNS monitoring and logging
  - Bridge API integration
  - Allowlist enforcement
  - Comprehensive test coverage
