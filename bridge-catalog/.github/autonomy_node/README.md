# Embedded Autonomy Node (EAN)

**Version**: v1.9.7n  
**Codename**: Embedded Autonomy Node  
**Type**: GitHub Internal Mini-Bridge Engine

## Overview

This directory contains the Embedded Autonomy Node - a self-contained micro-Bridge that operates entirely within GitHub Actions. It provides autonomous monitoring, repair, and certification capabilities without relying on external services.

## Architecture

```
.github/autonomy_node/
├── __init__.py         # Package initialization
├── core.py             # Main orchestration engine
├── truth.py            # Truth Micro-Certifier
├── parser.py           # Repository scanner
├── cascade.py          # Cascade Mini-Orchestrator
├── blueprint.py        # Blueprint Micro-Forge
├── node_config.json    # Configuration
└── reports/            # Generated audit reports (gitignored)
```

## Quick Start

### Run Manually

```bash
python3 .github/autonomy_node/core.py
```

### Run via Workflow

The node runs automatically on:
- Push to main branch
- Every 6 hours (scheduled)
- Manual workflow dispatch

### Configuration

Edit `node_config.json` to customize behavior:

```json
{
  "autonomy_interval_hours": 6,
  "max_report_backups": 10,
  "truth_certification": true,
  "self_heal_enabled": true,
  "genesis_registration": true
}
```

## Components

### Core Orchestrator (`core.py`)

Main entry point that coordinates:
- Repository scanning
- Safe repairs
- Truth certification
- Cascade synchronization
- Report generation

### Truth Micro-Certifier (`truth.py`)

Validates repair results and ensures:
- Changes meet quality standards
- No infinite repair loops
- All modifications are certified

### Parser Sentinel (`parser.py`)

Scans repository for:
- Debug print statements
- Code patterns
- Potential issues
- Files needing review

### Blueprint Micro-Forge (`blueprint.py`)

Applies safe repairs using:
- Pre-approved patterns
- Deterministic rules
- Non-destructive changes

### Cascade Mini-Orchestrator (`cascade.py`)

Synchronizes state with:
- Main Cascade engine (when online)
- Genesis Bus
- Change history

## Reports

Audit reports are generated in `reports/` directory:

```
reports/
├── summary_20251013.json
├── summary_20251014.json
└── summary_20251015.json
```

Reports are automatically pruned when exceeding `max_report_backups`.

## Genesis Integration

The node registers with Genesis Bus when online:

- **Topic**: `genesis.node.register`
- **Type**: `micro_bridge`
- **Status**: `active`
- **Certified**: `true`

Published events:
- `genesis.autonomy_node.report` - Audit reports
- `autonomy_node.scan.complete` - Scan results
- `autonomy_node.repair.applied` - Repairs
- `autonomy_node.truth.verified` - Certifications

## Offline Mode

When Genesis Bus is unavailable:
- Continues autonomous operation
- Stores reports locally only
- Queues events for later sync
- Maintains full functionality

## Testing

Run unit tests:
```bash
python3 -m unittest tests.test_autonomy_node -v
```

Run verification:
```bash
python3 scripts/verify_autonomy_node.py
```

## Documentation

See `docs/` for complete documentation:
- [EMBEDDED_AUTONOMY_NODE.md](../../docs/EMBEDDED_AUTONOMY_NODE.md)
- [GITHUB_MINI_BRIDGE_OVERVIEW.md](../../docs/GITHUB_MINI_BRIDGE_OVERVIEW.md)
- [NODE_FAILSAFE_GUIDE.md](../../docs/NODE_FAILSAFE_GUIDE.md)
- [GENESIS_REGISTRATION_OVERVIEW.md](../../docs/GENESIS_REGISTRATION_OVERVIEW.md)

## Troubleshooting

**Node not running?**
- Check `.github/workflows/autonomy_node.yml`
- Verify Python version (3.12+)
- Review workflow run logs

**Reports not generated?**
- Check `reports/` directory exists
- Verify write permissions
- Review node execution logs

**Genesis connection fails?**
- Normal in offline mode
- Check external Bridge status
- Verify `genesis_registration` config

## Support

For issues or questions:
1. Review documentation in `docs/`
2. Check workflow run logs
3. Review recent reports
4. Contact Admiral-level users

## Version History

- **v1.9.7n** - Initial release of Embedded Autonomy Node
