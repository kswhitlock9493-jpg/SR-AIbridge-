# Reflex Loop Protocol (RLP)
## v1.9.7o - Complete Architecture & Lifecycle

---

## 🚀 Overview

The **Reflex Loop Protocol (RLP)** is a self-PR system that enables the Embedded Autonomy Node (EAN) to achieve recursive autonomy through:

1. **Detection** - Identifying code, configuration, or documentation issues
2. **Correction** - Safely patching detected problems
3. **Publication** - Creating and filing pull requests autonomously
4. **Verification** - Truth Engine certification and RBAC validation
5. **Integration** - Automatic merge after successful verification

This closes the loop between detection, correction, and publication without requiring human intervention.

---

## 🧠 Core Components

### 1. Reflex Engine (`.github/autonomy_node/reflex.py`)

The main orchestration module that:
- Scans the reports directory for autonomy reports
- Filters reports ready for PR generation
- Builds PR bodies with complete metadata
- Coordinates signing and submission

**Key Functions:**
- `reflex_loop()` - Main entry point for PR generation cycle
- `build_pr_body(report)` - Formats PR description from report data
- `submit(pr_data)` - Handles GitHub API submission or offline queuing
- `queue_offline(pr_data)` - Stores PRs when GitHub API is unavailable

### 2. Truth Signer (`.github/autonomy_node/signer.py`)

Cryptographic signing and RBAC validation:
- Generates SHA256 hash signatures for PR bodies
- Verifies RBAC permissions (Admiral/Captain roles)
- Validates existing signatures for integrity

**Key Functions:**
- `sign(pr_body)` - Creates signed PR envelope with Truth signature
- `verify_rbac(role)` - Checks RBAC permissions
- `verify_signature(signed_data)` - Validates signature integrity

### 3. Merge Verifier (`.github/autonomy_node/verifier.py`)

Determines merge readiness:
- Checks if reports have fixes applied
- Validates Truth certification status
- Performs comprehensive merge readiness audits

**Key Functions:**
- `ready_to_pr(report)` - Determines if report should generate PR
- `check_merge_readiness(pr_data)` - Complete merge validation

### 4. Offline Queue (`.github/autonomy_node/pending_prs/`)

Storage for PRs when GitHub API is unavailable:
- JSON files with timestamp-based filenames
- Preserves PR data for later submission
- Enables operation in isolated environments

---

## 🔄 Protocol Lifecycle

### Phase 1: Detection & Reporting
1. EAN detects an issue (code smell, config drift, documentation gap)
2. EAN generates a report with:
   - Summary of the issue
   - Safe fixes applied
   - Truth verification status
   - Additional context
3. Report saved to `.github/autonomy_node/reports/`

### Phase 2: Reflex Activation
1. Reflex Loop workflow triggers (every 12h or on-demand)
2. `reflex.py` scans reports directory
3. For each report:
   - Calls `verifier.ready_to_pr()` to check eligibility
   - If ready, proceeds to Phase 3
   - If not ready, logs and skips

### Phase 3: PR Generation
1. `build_pr_body()` creates formatted PR description
2. Includes:
   - Timestamp
   - Report summary
   - Files changed count
   - Verification status
   - EAN attribution

### Phase 4: Truth Certification
1. `signer.sign()` generates SHA256 signature
2. Signature appended to PR body
3. RBAC verification performed
4. Signed envelope created with:
   - Title (includes signature hash)
   - Body (with signature footer)
   - Signature hash

### Phase 5: Submission
1. Check for `GITHUB_TOKEN` environment variable
2. If available:
   - Prepare GitHub API request
   - Target repository from `GITHUB_REPOSITORY`
   - Create PR against `main` from `autonomy/reflex` branch
3. If not available:
   - Queue PR offline in `pending_prs/`
   - Wait for connectivity restoration

### Phase 6: Verification & Merge
1. Automated checks run on PR:
   - Truth signature validation
   - RBAC approval verification
   - Code quality checks
2. If all checks pass:
   - Cascade coordinates merge
   - Genesis Bus notified
   - Loop completes

---

## 📊 Data Flow

```
┌─────────────────┐
│  Issue Detected │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generate Report│
│ (.json in       │
│  reports/)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Reflex Loop    │
│  Scans Reports  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Verify Ready   │
│  (verifier.py)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Build PR Body  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Truth Sign     │
│  (signer.py)    │
└────────┬────────┘
         │
         ▼
    ┌───┴────┐
    │ Token? │
    └───┬────┘
        │
   ┌────┴────┐
   │         │
   ▼         ▼
┌──────┐  ┌──────────┐
│Submit│  │Queue     │
│to GH │  │Offline   │
└──────┘  └──────────┘
```

---

## ⚙️ Configuration

### Environment Variables

- `GITHUB_TOKEN` - GitHub API token for PR creation
- `GITHUB_REPOSITORY` - Target repository (owner/repo)
- `RBAC_ENABLED` - Enable/disable RBAC checks (default: true)

### Workflow Schedule

Default: Every 12 hours + manual dispatch + on push to main

Configure in `.github/workflows/reflex_loop.yml`:
```yaml
schedule:
  - cron: "0 */12 * * *"   # Adjust frequency here
```

---

## 🔒 Security

### Truth Signature
- SHA256 hash of PR body (first 16 characters)
- Appended to PR body for verification
- Prevents tampering with PR content

### RBAC Validation
- Only Admiral and Captain roles can approve
- Checked before PR submission
- Enforced at multiple layers

### Offline Queue Safety
- PRs stored locally if GitHub unavailable
- No sensitive data in queue files
- Automatic cleanup after submission

---

## 📈 Monitoring

### Logs
All reflex operations logged with:
- Timestamp
- Operation type
- Success/failure status
- Error details (if any)

### Genesis Bus Events
- `autonomy.reflex.startup` - Reflex protocol activation
- `autonomy.reflex.pr_created` - PR successfully created
- `autonomy.reflex.pr_queued` - PR queued offline

---

## 🧪 Testing

See `bridge_backend/tests/test_reflex_loop.py` for:
- Report processing tests
- Signature generation and validation
- Merge readiness checks
- Offline queue operations
- End-to-end reflex loop simulation

---

## 🔄 Integration Points

### Genesis Bus
- Publishes startup events
- Coordinates with other engines
- Enables ecosystem awareness

### Truth Engine
- Provides signature validation
- Certifies changes
- Ensures integrity

### Cascade
- Coordinates merge operations
- Orchestrates verification
- Manages workflow state

### Steward
- Monitors configuration drift
- Triggers reflex fixes
- Validates environment state

---

## 📝 Best Practices

1. **Report Quality**: Ensure reports have clear summaries and fix counts
2. **Signature Verification**: Always verify signatures before merge
3. **Offline Handling**: Monitor pending_prs/ directory for queued PRs
4. **RBAC Compliance**: Keep role assignments current and minimal
5. **Workflow Frequency**: Adjust cron schedule based on issue frequency

---

## 🚨 Troubleshooting

### No PRs Generated
- Check reports directory has valid JSON files
- Verify reports have `safe_fixes > 0`
- Confirm `truth_verified: true` in reports

### PRs Queued Offline
- Verify `GITHUB_TOKEN` is set
- Check `GITHUB_REPOSITORY` format (owner/repo)
- Ensure network connectivity to GitHub API

### Signature Validation Fails
- Verify PR body hasn't been modified
- Check signature hash matches original
- Confirm Truth Engine is operational

---

**Version:** v1.9.7o  
**Status:** ✅ Production Ready  
**Scope:** Embedded Autonomy Node + Truth + Cascade + Genesis  
**Goal:** Achieve recursive autonomy through self-PR capability
