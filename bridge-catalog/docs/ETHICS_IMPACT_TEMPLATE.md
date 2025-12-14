# Ethics Impact Statement (template) — include in PRs for major features

**PR / Feature:**  
**Author:**  
**Date:**

## 1) Description
Short summary of the feature and its intended use.

## 2) Potential Misuses
List realistic misuse scenarios (data exfiltration, stealth forwarding, evading audits, etc).

## 3) Mitigations & Controls
List technical and process controls that reduce risk (RBAC, archival-before-delete, audit trail, feature toggles, test environment restrictions).

## 4) Data Sensitivity
Which data types are impacted? (PII, secrets, keys, system artifacts, telemetry)

## 5) Federation / External Dependencies
Does this feature forward data across federation? If so, list contract/peer expectations.

## 6) Approval
- Security reviewer: (name)
- Admiral sign-off: (name)
- Date of approval:
