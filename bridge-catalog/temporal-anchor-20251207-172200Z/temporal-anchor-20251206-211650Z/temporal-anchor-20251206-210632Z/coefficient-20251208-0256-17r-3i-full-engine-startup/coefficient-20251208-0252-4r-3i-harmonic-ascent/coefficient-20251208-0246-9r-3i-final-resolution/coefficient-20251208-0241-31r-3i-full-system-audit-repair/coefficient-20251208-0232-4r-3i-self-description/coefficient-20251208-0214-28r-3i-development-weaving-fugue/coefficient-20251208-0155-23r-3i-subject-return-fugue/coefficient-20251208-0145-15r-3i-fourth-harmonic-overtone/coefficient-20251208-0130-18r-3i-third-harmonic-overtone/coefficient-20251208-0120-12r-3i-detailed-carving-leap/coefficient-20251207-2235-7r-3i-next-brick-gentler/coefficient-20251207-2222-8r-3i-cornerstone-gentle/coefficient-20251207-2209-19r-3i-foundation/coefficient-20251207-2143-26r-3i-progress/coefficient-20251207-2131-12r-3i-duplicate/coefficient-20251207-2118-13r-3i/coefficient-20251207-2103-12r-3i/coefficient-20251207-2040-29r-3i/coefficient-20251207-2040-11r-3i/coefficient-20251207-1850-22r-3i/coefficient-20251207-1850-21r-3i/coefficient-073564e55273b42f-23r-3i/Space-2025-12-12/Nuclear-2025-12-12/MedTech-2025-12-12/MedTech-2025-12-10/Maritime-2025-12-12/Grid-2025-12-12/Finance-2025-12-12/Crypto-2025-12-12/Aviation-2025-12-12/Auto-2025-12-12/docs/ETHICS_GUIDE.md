# SR-AIbridge — Ethics & Operational Policy

## Introduction
SR-AIbridge is a sovereign, federated AI orchestration platform. This document clarifies acceptable use, governance, privacy commitments, and operational constraints to keep the project lawful, ethical, and auditable.

## Commitments
- **Privacy & Consent:** Operate only on data we own or for which we have explicit permission.
- **Accountability & Auditability:** All actions that change data have cryptographic audit trails and vault snapshots.
- **Transparency to Admins:** Admiral-level access for governance; high-impact actions require explicit approval.
- **Safety-first Automation:** Autonomous behaviors reaching beyond operator domain require human approval by default.

## Allowed Uses
- Internal R&D, resilience testing, federation among consenting peers.
- Agent orchestration and data processing with explicit authorization.
- Research with institutional approvals when required.

## Prohibited Uses
- Unconsented access, modification, or reclamation of systems/data not explicitly authorized.
- Concealment of activity to evade lawful audits or investigations.
- Deploying stealth or unregistered integrations to third-party systems without explicit written permission.
- Creation, distribution, or deployment of malware or offensive capabilities.

## Autonomy & "Stealth" Features
- Diagnostic features (incl. stealth modes for testing) must be internal-only, auditable, and disabled in production unless approved and logged.
- Any feature that could appear to provide "invisibility" must be classified and controlled by governance.

## Federation Policy
- Federation requires a signed, lightweight peer agreement specifying:
  - Allowed capabilities
  - Data handling and retention
  - Liability and responsibility
- Only configured with trusted peer IDs and explicit capability agreements.

## Data Retention & Deletion
- Role-aware retention:
  - Admiral: long-term archival for critical artifacts.
  - Captain: configurable medium-term windows.
  - Agent/Guest: limited windows.
- No deletion without successful archival and cryptographic verification.

## Fault Injection Governance
- Chaos tests are permitted only in test scopes or maintenance windows.
- Tests must be logged and results uploaded to the Telemetry Vault.
- No tests that impact external third-party endpoints without clear consent.

## Compliance & Legal
- This is not legal advice. Consult counsel for jurisdictional obligations.
- Keep copies of agreements for federation / external data sources.

## Reporting & Ethics Escalation
- If the platform is used outside these principles, contact Admiral on the Bridge and `security@` as listed in `SECURITY_CONTACT`.
- Provide artifact IDs, timestamps, and a short description for triage.

## Governance
- Quarterly security & ethics reviews are required.
- Any new engine or feature must include an Ethics Impact Statement (use template in `ETHICS_IMPACT_TEMPLATE.md`).

## Final Word
SR-AIbridge is built to be sovereign, auditable, and defensible. Keep the audit, vault, and relay systems enabled and documented to maintain ethical operation.
