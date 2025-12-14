# Offline Queue Handling
## Resilient PR Submission in Isolated Environments

---

## Overview

The Offline Queue system enables the Reflex Loop Protocol to operate in environments where:
- GitHub API is temporarily unavailable
- Network connectivity is restricted
- Token authentication is not configured
- Emergency offline operation is required

PRs are stored locally and automatically submitted when connectivity is restored.

---

## 📁 Queue Structure

### Directory Layout

```
.github/autonomy_node/
├── pending_prs/
│   ├── 1697234567.890.json    # Queued PR #1
│   ├── 1697234890.123.json    # Queued PR #2
│   └── 1697235123.456.json    # Queued PR #3
└── reports/
    ├── issue_001.json          # Source report
    └── issue_002.json          # Source report
```

### File Naming

Format: `{unix_timestamp}.json`

Example: `1697234567.890.json`
- Unix timestamp with millisecond precision
- Ensures unique filenames
- Natural chronological sorting
- Easy to parse for age/cleanup

---

## 📝 Queue File Format

### Structure

```json
{
  "title": "EAN Reflex Update [a1b2c3d4e5f6g7h8]",
  "body": "## 🤖 EAN Reflex PR — Auto-Generated\n\n**Timestamp:** 2025-10-13T03:12:14Z\n**Report:** Config drift detected\n**Truth Signature:** pending\n\n### Changes\n- 3 files cleaned\n- true verification status\n\n---\n\n**Truth Signature:** `a1b2c3d4e5f6g7h8`",
  "sig": "a1b2c3d4e5f6g7h8"
}
```

### Required Fields

- `title` (string): PR title with signature hash
- `body` (string): Full PR body with signature footer
- `sig` (string): 16-character signature hash

### Optional Fields

- `created_at` (timestamp): When PR was queued
- `priority` (string): `high|normal|low`
- `attempts` (integer): Submission retry count
- `last_error` (string): Most recent error message

---

## 🔄 Queue Operations

### 1. Enqueue (Add to Queue)

**Trigger:** GitHub API unavailable during PR submission

**Process:**
```python
def queue_offline(pr_data: Dict[str, Any]):
    pending_dir = ".github/autonomy_node/pending_prs"
    os.makedirs(pending_dir, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).timestamp()
    filename = f"{pending_dir}/{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(pr_data, f, indent=2)
    
    logger.info(f"💾 [REFLEX] PR queued offline: {filename}")
```

**Result:**
- PR stored as JSON file
- No data loss
- Ready for later submission

### 2. Process Queue (Submit Queued PRs)

**Trigger:** 
- GitHub API becomes available
- Manual queue processing
- Scheduled queue check

**Process:**
```python
def process_queue():
    pending_dir = ".github/autonomy_node/pending_prs"
    
    if not os.path.exists(pending_dir):
        return
    
    queued_files = sorted([
        f for f in os.listdir(pending_dir)
        if f.endswith(".json")
    ])
    
    for filename in queued_files:
        filepath = os.path.join(pending_dir, filename)
        
        with open(filepath, 'r') as f:
            pr_data = json.load(f)
        
        # Attempt submission
        if submit_to_github(pr_data):
            # Success - remove from queue
            os.remove(filepath)
            logger.info(f"✅ [QUEUE] Submitted: {filename}")
        else:
            # Failed - leave in queue
            logger.warning(f"⚠️ [QUEUE] Failed: {filename}")
```

**Result:**
- Successful submissions removed from queue
- Failed attempts remain for retry
- Maintains FIFO order

### 3. Cleanup (Remove Old Entries)

**Trigger:**
- Queue age threshold exceeded (default: 7 days)
- Manual cleanup
- Queue size limit reached

**Process:**
```python
def cleanup_queue(max_age_days=7):
    pending_dir = ".github/autonomy_node/pending_prs"
    cutoff = time.time() - (max_age_days * 86400)
    
    for filename in os.listdir(pending_dir):
        if not filename.endswith(".json"):
            continue
        
        # Extract timestamp from filename
        timestamp = float(filename.replace(".json", ""))
        
        if timestamp < cutoff:
            filepath = os.path.join(pending_dir, filename)
            os.remove(filepath)
            logger.info(f"🧹 [QUEUE] Cleaned up: {filename}")
```

**Result:**
- Stale queue entries removed
- Prevents unbounded growth
- Configurable retention period

---

## 🔍 Queue Monitoring

### Status Check

```python
def queue_status():
    pending_dir = ".github/autonomy_node/pending_prs"
    
    if not os.path.exists(pending_dir):
        return {"queued": 0, "oldest": None, "newest": None}
    
    files = [f for f in os.listdir(pending_dir) if f.endswith(".json")]
    
    if not files:
        return {"queued": 0, "oldest": None, "newest": None}
    
    timestamps = [float(f.replace(".json", "")) for f in files]
    
    return {
        "queued": len(files),
        "oldest": datetime.fromtimestamp(min(timestamps)),
        "newest": datetime.fromtimestamp(max(timestamps))
    }
```

### Health Metrics

- **Queue Size** - Number of pending PRs
- **Oldest Entry** - Age of first queued PR
- **Submission Rate** - PRs submitted per hour
- **Failure Rate** - Submission failures per hour

---

## ⚙️ Configuration

### Environment Variables

- `REFLEX_QUEUE_ENABLED` - Enable offline queue (default: `true`)
- `REFLEX_QUEUE_MAX_AGE_DAYS` - Max queue retention (default: `7`)
- `REFLEX_QUEUE_MAX_SIZE` - Max queue entries (default: `100`)
- `REFLEX_QUEUE_RETRY_INTERVAL` - Minutes between retries (default: `60`)

### Queue Limits

```python
MAX_QUEUE_SIZE = int(os.getenv("REFLEX_QUEUE_MAX_SIZE", "100"))
MAX_QUEUE_AGE_DAYS = int(os.getenv("REFLEX_QUEUE_MAX_AGE_DAYS", "7"))
RETRY_INTERVAL_MINUTES = int(os.getenv("REFLEX_QUEUE_RETRY_INTERVAL", "60"))
```

---

## 🚨 Error Handling

### Common Scenarios

#### 1. Disk Full

**Symptom:** Cannot write queue file

**Handling:**
```python
try:
    with open(filename, 'w') as f:
        json.dump(pr_data, f, indent=2)
except IOError as e:
    logger.error(f"❌ [QUEUE] Disk full: {e}")
    # Fall back to memory cache or alert
```

#### 2. Corrupted Queue File

**Symptom:** JSON parse error

**Handling:**
```python
try:
    pr_data = json.load(f)
except json.JSONDecodeError:
    logger.error(f"❌ [QUEUE] Corrupted: {filename}")
    # Move to quarantine directory
    shutil.move(filepath, quarantine_path)
```

#### 3. GitHub API Rate Limited

**Symptom:** 429 response from GitHub

**Handling:**
```python
if response.status_code == 429:
    retry_after = response.headers.get("Retry-After", 3600)
    logger.warning(f"⏳ [QUEUE] Rate limited, retry in {retry_after}s")
    # Leave in queue, respect rate limit
    return False
```

---

## 🔄 Queue Processing Workflow

### Automatic Processing

```
┌─────────────────┐
│ Reflex Loop     │
│ Runs            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check GitHub    │
│ Token Available │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Token?  │
    └────┬────┘
         │
   ┌─────┴─────┐
   │           │
   ▼           ▼
┌──────┐    ┌──────────┐
│Submit│    │Queue     │
│New PR│    │Offline   │
└──────┘    └──────────┘
   │           │
   └─────┬─────┘
         │
         ▼
┌─────────────────┐
│ Process Existing│
│ Queue           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ For Each Queued │
│ PR: Attempt     │
│ Submission      │
└────────┬────────┘
         │
    ┌────┴────┐
    │Success? │
    └────┬────┘
         │
   ┌─────┴─────┐
   │           │
   ▼           ▼
┌──────┐    ┌──────┐
│Remove│    │Keep  │
│from  │    │in    │
│Queue │    │Queue │
└──────┘    └──────┘
```

### Manual Processing

```bash
# Check queue status
python3 .github/autonomy_node/reflex.py --queue-status

# Process queue manually
python3 .github/autonomy_node/reflex.py --process-queue

# Clean up old entries
python3 .github/autonomy_node/reflex.py --cleanup-queue
```

---

## 📊 Queue Analytics

### Metrics to Track

1. **Queue Depth Over Time**
   - Track queue size hourly
   - Alert on sustained growth
   - Identify connectivity issues

2. **Submission Success Rate**
   - Percentage of successful submissions
   - Track failures by error type
   - Optimize retry logic

3. **Queue Age Distribution**
   - Histogram of entry ages
   - Identify stuck entries
   - Adjust cleanup policies

### Sample Query

```python
def queue_analytics():
    metrics = {
        "current_size": 0,
        "avg_age_hours": 0,
        "oldest_age_hours": 0,
        "submission_rate_24h": 0
    }
    
    # Calculate metrics from queue files
    # and submission logs
    
    return metrics
```

---

## 🧪 Testing Queue Operations

### Test Cases

1. **Enqueue Test**
   - Verify file created correctly
   - Check JSON format valid
   - Confirm timestamp accuracy

2. **Dequeue Test**
   - Submit queued PR successfully
   - Verify file removed
   - Check no data loss

3. **Retry Test**
   - Fail submission
   - Verify PR stays in queue
   - Confirm retry logic works

4. **Cleanup Test**
   - Create old queue entries
   - Run cleanup
   - Verify old entries removed

---

## 📝 Best Practices

1. **Monitor Queue Size**
   - Set alerts for queue > 10
   - Investigate sustained growth
   - Address connectivity issues promptly

2. **Regular Cleanup**
   - Run cleanup weekly minimum
   - Archive before deleting
   - Document cleanup rationale

3. **Handle Errors Gracefully**
   - Log all queue operations
   - Never lose PR data
   - Quarantine corrupted files

4. **Test Offline Mode**
   - Regularly test without token
   - Verify queue works as expected
   - Practice queue recovery

---

## 🔒 Security Considerations

### Queue File Permissions

```bash
# Ensure queue files are not world-readable
chmod 600 .github/autonomy_node/pending_prs/*.json
```

### Sensitive Data

- Queue files may contain PR details
- Don't commit queue directory to git
- Add to `.gitignore`
- Encrypt if storing sensitive info

---

**Version:** v1.9.7o  
**Status:** ✅ Production Ready  
**Scope:** Reflex Loop + Queue Management  
**Goal:** Enable resilient operation in isolated environments
