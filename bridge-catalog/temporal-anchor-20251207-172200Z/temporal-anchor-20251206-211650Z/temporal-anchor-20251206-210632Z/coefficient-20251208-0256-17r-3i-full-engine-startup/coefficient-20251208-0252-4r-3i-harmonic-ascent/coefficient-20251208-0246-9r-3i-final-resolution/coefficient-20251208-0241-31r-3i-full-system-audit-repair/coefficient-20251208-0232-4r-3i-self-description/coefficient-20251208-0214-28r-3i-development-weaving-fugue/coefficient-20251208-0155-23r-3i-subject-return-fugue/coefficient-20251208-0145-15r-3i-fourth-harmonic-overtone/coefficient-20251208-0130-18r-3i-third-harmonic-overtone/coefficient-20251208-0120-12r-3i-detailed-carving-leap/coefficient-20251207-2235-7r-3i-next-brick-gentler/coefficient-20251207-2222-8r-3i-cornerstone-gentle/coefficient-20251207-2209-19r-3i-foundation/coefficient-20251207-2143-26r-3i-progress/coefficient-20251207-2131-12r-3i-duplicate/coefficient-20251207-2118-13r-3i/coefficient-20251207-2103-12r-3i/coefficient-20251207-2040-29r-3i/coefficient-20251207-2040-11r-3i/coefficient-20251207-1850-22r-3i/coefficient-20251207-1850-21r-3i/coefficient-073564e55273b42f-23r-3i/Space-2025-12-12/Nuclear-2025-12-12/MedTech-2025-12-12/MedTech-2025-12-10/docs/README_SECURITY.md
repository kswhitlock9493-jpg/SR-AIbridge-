# README_SECURITY.md — quick developer guide

This short doc points contributors to the security-relevant places in SR-AIbridge.

## Archival-before-delete (relay_mailer)
- The relay mailer check is the canonical guard before any deletion:
  - `bridge_backend/utils/relay_mailer.py` exposes `archive_before_delete(...)`.
- Deletion flow must only proceed when `archive_before_delete` returns success (and checksum verification passes).
- If relay is disabled (`RELAY_ENABLED=false`), deletions of sensitive data are blocked except by Admiral overrides (logged and audited).

## Key generation & vault access
- Key creation is gated; in production run the keys utility under Admiral supervision.
- Local dev: use sample keys in `bridge_backend/keys/` or generate ephemeral keys with `bridge_backend/src/keys.py` helper.
- Never commit private keys or production `.env` values.

## Fault injection tests
- Fault injector file: `bridge_backend/bridge_core/fault_injector.py`
- Chaos flags are disabled in production by default. To run locally:
  - Set `ENABLE_FAULTS=true` in a dev-only `.env`
  - Run tests or the demo scripts in an isolated environment.

## Where to look in the codebase
- Relay mailer: `bridge_backend/utils/relay_mailer.py`
- Vault protocols: `bridge_backend/bridge_core/protocols/vaulting.py`
- Keys manager: `bridge_backend/src/keys.py`
- RBAC & permissions: `bridge_backend/bridge_core/middleware/permissions.py`
- Federation: `bridge_backend/bridge_core/federation_client.py`

## Quick safety checks before merging
- No secrets in diffs (`git diff --staged`).
- Tests pass: `pytest -q`.
- New risky features include an `Ethics Impact Statement` in their PR (see template).
