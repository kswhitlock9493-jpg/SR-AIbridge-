# SR-AIbridge — Security & Responsible Disclosure

## Purpose
This document explains SR-AIbridge's security posture, how to report vulnerabilities, and the safeguards we have in place to protect data, users, and federated nodes. It also outlines accepted practices for contributors and operators.

## Responsible Disclosure
If you discover a potential security issue, report it privately to the Admiral on the Bridge (preferred) or use the repo security contact listed in `SECURITY_CONTACT`.

When reporting, include:
- Short description
- Reproduction steps (if safe)
- Proof-of-concept (only if non-destructive)
- Contact information

We will:
1. Acknowledge within 48 hours.
2. Triage and propose a remediation timeline.
3. Coordinate disclosure with the reporter.

**Do not** exploit vulnerabilities for data exfiltration, service disruption, or unauthorized access.

## Key Security Principles
- **Least privilege:** components run with the minimum permissions required.
- **Separation of duties:** roles are separated (Admiral / Captain / Agent) and enforced by RBAC.
- **Cryptographic audit trails:** custody, archival and deletion events are crypto-signed (SHA256) and recorded.
- **Immutable audit logs:** vault and event logs are append-only and preserved for forensic review.
- **No secrets in repo:** credentials must be supplied via environment variables or a secrets manager. `.env` files must not be committed.

## Data Protection & Vaulting
- Archival-before-delete is enforced: data is archived (relay_mailer) before deletion; if archival fails deletion is postponed and queued for retry.
- Vault entries and brain items must be stored encrypted at rest (AES-256 or equivalent). Key management handled by `bridge_backend/src/keys.py`.
- Key creation endpoints are gated behind Admiral-managed flags in production.

## Federation Security
- Federation uses TLS (wss/https).
- Peers must be authenticated; federation capabilities and peer IDs validated during handshake.
- Forwarding only to registered, consented peers and only for declared capabilities.

## Fault Injection & Testing Safety
- Fault-injection tests run in controlled/test environments and are disabled by default in production.
- Chaos flags are admin-controlled and are auditable.

## Secrets & Keys
- Use a secrets manager (e.g., Render secrets, AWS Secrets Manager, HashiCorp Vault).
- Example env vars (do NOT place values in the repo):
  - `DATABASE_URL`
  - `SMTP_USER`
  - `SMTP_PASSWORD`
  - `ADMIRAL_KEY_PATH`
  - `RELAY_ENABLED=true|false`
- Rotate keys regularly and after any suspected compromise.

## Incident Response (high-level)
Triggers:
- Identity hash mismatches
- Repeated relay/archive failures
- Large anomaly spikes in telemetry

Triage:
1. Isolate impacted services (disable federation if needed).
2. Preserve logs and vault snapshots.
3. Notify Admiral and security contacts.
4. Follow applicable disclosure laws.

## CI/CD & Dependency Management
- Enable dependency scanning (Dependabot, Snyk, etc.)
- Pin production dependencies in `requirements.txt` / lockfiles.
- Exclude build artifacts from reports and LOC counters.

## Contributors & Pre-commit
- Use pre-commit hooks to detect secrets and run basic linters.
- Run tests: `pytest` for backend tests; run demo scripts only in isolated environments.

## Contact & Escalation
- Primary contact: Admiral (via Bridge)
- Fallback repo contact: see `SECURITY_CONTACT` in repo root
