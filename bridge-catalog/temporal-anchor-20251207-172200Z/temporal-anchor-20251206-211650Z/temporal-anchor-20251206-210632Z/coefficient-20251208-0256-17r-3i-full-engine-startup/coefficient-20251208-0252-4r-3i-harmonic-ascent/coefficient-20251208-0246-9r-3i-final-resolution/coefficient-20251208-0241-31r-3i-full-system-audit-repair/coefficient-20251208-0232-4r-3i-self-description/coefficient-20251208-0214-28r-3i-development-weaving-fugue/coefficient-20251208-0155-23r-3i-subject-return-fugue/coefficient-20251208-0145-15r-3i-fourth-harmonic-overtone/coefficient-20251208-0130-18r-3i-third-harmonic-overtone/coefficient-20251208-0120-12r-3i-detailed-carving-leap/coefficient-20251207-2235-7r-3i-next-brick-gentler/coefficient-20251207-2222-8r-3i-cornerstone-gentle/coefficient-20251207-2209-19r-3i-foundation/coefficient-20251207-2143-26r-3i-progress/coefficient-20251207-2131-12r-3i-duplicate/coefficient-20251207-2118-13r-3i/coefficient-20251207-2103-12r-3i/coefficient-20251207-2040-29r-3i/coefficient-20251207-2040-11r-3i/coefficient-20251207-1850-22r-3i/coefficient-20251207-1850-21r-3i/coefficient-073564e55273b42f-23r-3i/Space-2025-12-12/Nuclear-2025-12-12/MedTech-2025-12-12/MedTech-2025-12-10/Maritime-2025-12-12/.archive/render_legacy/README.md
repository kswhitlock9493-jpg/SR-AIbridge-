# Render Legacy Files Archive

This directory contains archived files from the legacy Render.com deployment system.

**Archived on:** 2025-11-05
**Reason:** Migration to native SDTF and BRH (Bridge Runtime Handler) for sovereign deployment

## What was Render?

Render.com was a cloud platform previously used for deploying the SR-AIbridge backend.
The system has been migrated to use:
- **BRH (Bridge Runtime Handler)**: Self-hosted Docker-based runtime
- **SDTF (Sovereign Dominion Token Forge)**: Token management system

## Files Archived

1. `render.yaml` - Render deployment configuration
2. `render_quantum_security.sh` - Render security checks script
3. `render.py` (webhook) - Render webhook handler
4. `render.py` (provider) - EnvSync Render provider
5. `render_adapter.py` - Steward Render adapter
6. `render_fallback_adapter.py` - Chimera Render fallback
7. `test_render_fallback.py` - Render fallback tests

## Migration Path

Old: GitHub → Render.com → Production
New: GitHub → BRH (self-hosted) → Production

For current deployment instructions, see:
- `/docs/BRH_DEPLOYMENT_GUIDE.md`
- `/docs/BRH_GUIDE.md`
- `/brh/README.md`
