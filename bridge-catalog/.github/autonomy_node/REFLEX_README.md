# 🧠 Reflex Loop Protocol v1.9.7o

## The Self-PR Engine

The **Reflex Loop Protocol (RLP)** gives the Embedded Autonomy Node (EAN) the power to file, describe, sign, and close its own pull requests when it detects or fixes issues — completing the loop between detection, correction, and publication.

---

## 🚀 Quick Start

### Running the Reflex Loop

```bash
# Manually trigger reflex loop
python3 .github/autonomy_node/reflex.py

# Or use GitHub Actions workflow dispatch
# Navigate to Actions → EAN Reflex Loop → Run workflow
```

### Creating a Report for Reflex Processing

Create a JSON report in `.github/autonomy_node/reports/`:

```json
{
  "summary": "Configuration drift detected",
  "safe_fixes": 3,
  "truth_verified": true,
  "details": "Fixed environment variables:\n- Updated DATABASE_URL\n- Corrected API_ENDPOINT"
}
```

The reflex loop will automatically:
1. Detect the report
2. Generate a PR body
3. Sign it with Truth Engine
4. Submit to GitHub or queue offline

---

## 📊 Architecture Overview

```
┌─────────────────┐
│ Issue Detected  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate Report │
│ (JSON)          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Reflex Loop     │
│ (Every 12h)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Truth Sign      │
│ (SHA256)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Submit PR       │
│ or Queue        │
└─────────────────┘
```

---

## 🔑 Key Components

### 1. Reflex Engine (`reflex.py`)
- Scans reports directory
- Builds PR bodies
- Coordinates signing and submission

### 2. Truth Signer (`signer.py`)
- Generates SHA256 signatures
- Validates RBAC permissions
- Verifies signature integrity

### 3. Merge Verifier (`verifier.py`)
- Checks report readiness
- Validates merge requirements
- Performs comprehensive audits

### 4. Offline Queue (`pending_prs/`)
- Stores PRs when GitHub API unavailable
- Automatic submission when connectivity restored
- Resilient operation in isolation

---

## 📚 Documentation

- **[Reflex Loop Protocol](../../docs/REFLEX_LOOP_PROTOCOL.md)** - Complete architecture & lifecycle
- **[Autonomy PR Verification](../../docs/AUTONOMY_PR_VERIFICATION.md)** - Truth signing + merge logic
- **[Offline Queue Handling](../../docs/OFFLINE_QUEUE_HANDLING.md)** - Offline PR queue specs

---

## 🔒 Security

### Truth Signature
Every PR is signed with a SHA256 hash (truncated to 16 characters) that verifies:
- PR body hasn't been tampered with
- Changes are certified by Truth Engine
- Integrity maintained throughout lifecycle

### RBAC Validation
Only Admiral and Captain roles can approve PRs:
- Admiral: Full authority
- Captain: Limited authority
- All others: No approval rights

### Offline Queue Safety
PRs queued offline are:
- Stored locally in `.github/autonomy_node/pending_prs/`
- Excluded from git via `.gitignore`
- Automatically submitted when GitHub API available

---

## ⚙️ Configuration

### Environment Variables

```bash
# GitHub API access (required for PR submission)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx

# Repository (automatically set in GitHub Actions)
GITHUB_REPOSITORY=owner/repo

# RBAC control (default: true)
RBAC_ENABLED=true

# Reflex queue settings
REFLEX_QUEUE_ENABLED=true
REFLEX_QUEUE_MAX_AGE_DAYS=7
REFLEX_QUEUE_MAX_SIZE=100
```

### Workflow Schedule

Default: Every 12 hours + manual dispatch + on push to main

Configure in `.github/workflows/reflex_loop.yml`:
```yaml
on:
  schedule:
    - cron: "0 */12 * * *"   # Adjust frequency here
  workflow_dispatch:
  push:
    branches: [main]
```

---

## 🧪 Testing

### Verification Script

```bash
# Run comprehensive verification
python3 scripts/verify_reflex_loop.py
```

### Manual Testing

```bash
# Test signer module
python3 -c "
import sys
sys.path.insert(0, '.github/autonomy_node')
import signer
signed = signer.sign('Test')
print(f'Signature: {signed[\"sig\"]}')
print(f'Valid: {signer.verify_signature(signed)}')
"

# Test verifier module
python3 -c "
import sys
sys.path.insert(0, '.github/autonomy_node')
import verifier
report = {'safe_fixes': 3, 'truth_verified': True}
print(f'Ready: {verifier.ready_to_pr(report)}')
"
```

### Unit Tests

```bash
# Run test suite (requires pytest)
python3 -m pytest bridge_backend/tests/test_reflex_loop.py -v
```

---

## 📈 Monitoring

### Check Queue Status

```bash
# List queued PRs
ls -lh .github/autonomy_node/pending_prs/

# View queued PR content
cat .github/autonomy_node/pending_prs/*.json | jq .
```

### Genesis Bus Events

The Reflex Loop publishes events to Genesis Bus:
- `autonomy.reflex.startup` - Reflex protocol activation
- `autonomy.reflex.pr_created` - PR successfully created
- `autonomy.reflex.pr_queued` - PR queued offline

---

## 🔧 Troubleshooting

### No PRs Generated

**Symptoms:** Reflex loop runs but no PRs created

**Solutions:**
1. Check reports directory has valid JSON files
2. Verify reports have `safe_fixes > 0`
3. Confirm `truth_verified: true` in reports
4. Review reflex loop logs

### PRs Queued Offline

**Symptoms:** PRs appear in `pending_prs/` directory

**Solutions:**
1. Verify `GITHUB_TOKEN` is set
2. Check `GITHUB_REPOSITORY` format (owner/repo)
3. Ensure network connectivity to GitHub API
4. Manually process queue when connectivity restored

### Signature Validation Fails

**Symptoms:** PR merge blocked due to invalid signature

**Solutions:**
1. Verify PR body hasn't been manually edited
2. Check signature hash matches original
3. Confirm Truth Engine is operational
4. Re-generate PR if necessary

---

## 🎯 Best Practices

1. **Report Quality**: Ensure reports have clear summaries and accurate fix counts
2. **Signature Verification**: Always verify signatures before merge
3. **Offline Handling**: Monitor `pending_prs/` directory regularly
4. **RBAC Compliance**: Keep role assignments current and minimal
5. **Workflow Frequency**: Adjust cron schedule based on issue frequency

---

## 🌌 Integration Points

### Genesis Bus
Publishes startup and operation events for ecosystem coordination

### Truth Engine
Provides signature validation and change certification

### Cascade
Coordinates merge operations and workflow orchestration

### Steward
Monitors configuration drift and triggers reflex fixes

---

## 📊 Expected Behavior

| Step | Trigger | Result |
|------|---------|--------|
| Scan | Every 6h | EAN creates new report |
| Reflex | Every 12h | Checks latest report |
| Sign | If fixes found | Truth signs |
| Submit | Online | Opens PR via GitHub API |
| Merge | After verify | Cascade finalizes merge |

---

## 🚀 Version Information

- **Version:** v1.9.7o
- **Codename:** Reflex Loop Protocol
- **Status:** ✅ Production Ready
- **Scope:** Embedded Autonomy Node + Truth + Cascade + Genesis
- **Goal:** Achieve recursive autonomy through self-PR capability

---

## 📝 Changelog

### v1.9.7o (Initial Release)
- ✅ Core reflex loop implementation
- ✅ Truth Engine signing system
- ✅ RBAC validation
- ✅ Offline queue handling
- ✅ Genesis Bus integration
- ✅ Comprehensive documentation
- ✅ Test suite
- ✅ Verification script

---

**The Bridge can now detect, patch, document, sign, and publish its own PRs — maintaining its integrity in isolation and coordinating with Genesis Bus once connection restores.**
