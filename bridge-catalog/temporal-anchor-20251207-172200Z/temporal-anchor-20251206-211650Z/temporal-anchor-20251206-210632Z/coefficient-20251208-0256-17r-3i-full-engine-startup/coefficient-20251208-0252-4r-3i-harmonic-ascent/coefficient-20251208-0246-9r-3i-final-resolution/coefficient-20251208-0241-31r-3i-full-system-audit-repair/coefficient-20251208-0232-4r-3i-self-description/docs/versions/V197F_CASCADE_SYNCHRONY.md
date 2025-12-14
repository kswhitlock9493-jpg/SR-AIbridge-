# v1.9.7f Cascade Synchrony - Environment Variables

## Forge System Environment Variables

The Cascade Synchrony protocol introduces several new environment variables to control the GitHub Forge integration and cross-platform healing system.

### Core Forge Variables

#### FORGE_MODE
- **Type:** String (`enabled` or `disabled`)
- **Default:** `disabled`
- **Description:** Enables the GitHub Forge introspection and engine integration system. When enabled, the Forge scans the repository structure and automatically integrates engines from their source paths.
- **Example:** `FORGE_MODE=enabled`

#### FORGE_SELF_HEAL
- **Type:** Boolean (`true` or `false`)
- **Default:** `false`
- **Description:** Enables automatic self-healing capabilities at the Forge level. When enabled, the Forge can automatically detect and repair configuration drift.
- **Example:** `FORGE_SELF_HEAL=true`

### Synchrony Protocol Variables

#### CASCADE_SYNC
- **Type:** Boolean (`true` or `false`)
- **Default:** `false`
- **Description:** Enables Cascade Synchrony cross-system healing protocol. When enabled, Cascade can detect errors and trigger coordinated healing across all systems.
- **Example:** `CASCADE_SYNC=true`

#### ARIE_PROPAGATION
- **Type:** Boolean (`true` or `false`)
- **Default:** `false`
- **Description:** Enables ARIE (Autonomous Repository Integrity Engine) propagation through the Forge. When enabled, ARIE can apply patches and propagate fixes across the repository.
- **Example:** `ARIE_PROPAGATION=true`

#### UMBRA_MEMORY_SYNC
- **Type:** Boolean (`true` or `false`)
- **Default:** `false`
- **Description:** Enables Umbra memory synchronization for learning from healing events. When enabled, Umbra stores and recalls successful healing patterns.
- **Example:** `UMBRA_MEMORY_SYNC=true`

### Existing Variables (Enhanced)

#### TRUTH_CERTIFICATION
- **Type:** Boolean (`true` or `false`)
- **Default:** `true`
- **Description:** Enables Truth certification for all Forge operations. When enabled, all engine integrations and healing events are certified through the Truth engine for RBAC compliance.
- **Example:** `TRUTH_CERTIFICATION=true`

## Complete v1.9.7f Configuration

To enable the full Cascade Synchrony protocol, add these variables to your `.env` file:

```env
# Forge Core
FORGE_MODE=enabled
FORGE_SELF_HEAL=true

# Cascade Synchrony Protocol
CASCADE_SYNC=true
ARIE_PROPAGATION=true
UMBRA_MEMORY_SYNC=true

# Truth Certification (already enabled by default)
TRUTH_CERTIFICATION=true

# Existing Engine Flags (ensure these are enabled)
CASCADE_ENABLED=true
ARIE_ENABLED=true
UMBRA_ENABLED=true
TRUTH_ENABLED=true
GENESIS_MODE=enabled
```

## Architecture Overview

### Healing Flow

```
┌──────────────────────────────────────────────┐
│ Cascade Healing Engine                       │
│   ↳ detects subsystem error                  │
│   ↳ triggers ARIE predictive fix             │
│   ↳ reports patch status to Truth            │
├──────────────────────────────────────────────┤
│ ARIE Learning Core                           │
│   ↳ mirrors fix → Forge                      │
│   ↳ Forge commits patch to GitHub repo       │
│   ↳ Umbra learns from patch metadata         │
└──────────────────────────────────────────────┘
```

### Platform Recovery Matrix

| Engine | Repair Action | Trigger | Result |
|--------|--------------|---------|--------|
| Umbra | Learns and replays successful deploys | Netlify fail/pass | Memory recall activated |
| Cascade | Restores lost engine state | Exception → Healing event | Restart + certify |
| ARIE | Applies Forge-level patch | Git diff anomaly | Fix committed |
| Truth | Certifies fix, validates RBAC | Every engine | Ensures safe merge |
| Forge | Self-registers new engines | New folder detected | Adds to .github/bridge_forge.json |

## API Endpoints

When `FORGE_MODE=enabled`, the following endpoints become available:

- `GET /api/forge/status` - Get Forge and Synchrony status
- `GET /api/forge/registry` - Get engine registry mappings
- `GET /api/forge/topology` - Get topology visualization
- `POST /api/forge/integrate` - Manually trigger engine integration
- `POST /api/forge/heal/{subsystem}` - Trigger healing for a subsystem
- `POST /api/forge/recover/{platform}` - Trigger platform-specific recovery

## Security Notes

- All Forge operations require Admiral-level permissions (enforced by RBAC)
- Truth certification is mandatory for all healing events
- Immutable Forge writes unless Truth-certified
- Engine-level authentication maintained across all operations

## Version Summary

- **Version:** v1.9.7f
- **Codename:** Cascade Synchrony
- **Status:** Ready for Deployment
- **Autonomy Level:** Full
- **Healing Mode:** Cross-System (Render ↔ GitHub ↔ Netlify ↔ Bridge)

## Admiral Directive

> "The Forge remembers, the Bridge learns, the Truth certifies.
> No engine sleeps, no system fails unseen." ⚙️✨
