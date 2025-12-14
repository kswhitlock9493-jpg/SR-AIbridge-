# Secure Data Relay Protocol - Quick Reference

## Overview

The Secure Data Relay Protocol ensures zero data loss by automatically archiving data to `sraibridge@gmail.com` before any deletion or expiration.

## Quick Start

### 1. Enable the Relay

```bash
# In .env
RELAY_ENABLED=true
RELAY_EMAIL=sraibridge@gmail.com

# SMTP Configuration (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=sraibridge@gmail.com
SMTP_PASSWORD=your-app-password
```

### 2. Use in Code

```python
from utils.relay_mailer import relay_mailer

# Before deleting any data
success = await relay_mailer.archive_before_delete(
    component="vault",      # System component
    user_id="captain_alpha", # User ID
    role="captain",         # User role
    record=data_to_delete   # Data being deleted
)

if success:
    # Safe to delete
    delete_record(record_id)
else:
    # Archive failed - DO NOT delete
    postpone_deletion(record_id)
```

## Role-Based Retention

| Role    | Retention  | Use Case |
|---------|-----------|----------|
| Admiral | Permanent | Critical system data, mission archives |
| Captain | 14 hours  | Mission logs, vault entries |
| Agent   | 7 hours   | Temporary memory, agent context |

## Components

Common component identifiers:

- `vault` - Vault logs and storage
- `brain` - Brain memories and context
- `missions` - Mission data and assignments
- `system` - System errors and diagnostics
- `custody` - Cryptographic key operations

## Email Organization

Archives are sent with labels for organization:

- **Subject**: `[SR-AIbridge] Data Relay Event – {component}`
- **Suggested Labels**:
  - `missions/deleted`
  - `vault/archive`
  - `brain/memory-dump`
  - `system/errors`

## Metadata Envelope

Each archived email includes:

```json
{
  "timestamp": "2024-10-04T12:00:00+00:00",
  "user_id": "captain_alpha",
  "role": "captain",
  "component": "vault",
  "action": "DELETE",
  "payload_hash": "sha256...",
  "retention_hours": 14,
  "notes": "Archived automatically..."
}
```

## Queue Retry Mechanism

If email sending fails (network issues):

1. Data is queued locally: `vault/relay_queue/`
2. Deletion is postponed
3. Retry automatically on next check:

```python
# Manual retry
results = await relay_mailer.retry_queued_items(max_retries=3)
print(f"Retried: {results['success']} succeeded, {results['failed']} failed")
```

## Verification

Verify archive integrity:

```python
metadata = relay_mailer.format_relay_metadata(...)
is_valid = relay_mailer.verify_archive(metadata, original_data)
```

## Production Checklist

- [ ] `RELAY_ENABLED=true` in production `.env`
- [ ] Valid SMTP credentials configured
- [ ] Gmail App Password created (not regular password)
- [ ] Test with sample deletion
- [ ] Verify email received at `sraibridge@gmail.com`
- [ ] Check checksum matches in archive
- [ ] Set up monitoring for queue size

## Monitoring

Check relay status:

```python
from utils.relay_mailer import relay_mailer

print(f"Enabled: {relay_mailer.enabled}")
print(f"Queue size: {len(relay_mailer.get_queued_items())}")
```

## Troubleshooting

### "SMTP credentials not configured"

Set `SMTP_USER` and `SMTP_PASSWORD` in `.env`

### "Authentication failed"

For Gmail, use an **App Password**, not your regular password:
1. Enable 2FA on Google Account
2. Generate App Password
3. Use that in `SMTP_PASSWORD`

### "Permission denied: /var/srbridge"

The relay will automatically fall back to `/tmp/relay_queue`. To use a custom path:

```bash
RELAY_BACKUP_PATH=./vault/relay_queue
```

### Queued items not retrying

Manually trigger retry:

```python
from utils.relay_mailer import relay_mailer
results = await relay_mailer.retry_queued_items()
```

## Security Notes

1. **TLS/SSL**: All SMTP connections use TLS (enforced)
2. **Credentials**: Store SMTP password in `.env`, never commit
3. **Checksums**: SHA256 hashes verify data integrity
4. **No Third-Party**: Email stays within SR-AIbridge control

## API Reference

### `archive_before_delete(component, user_id, role, record)`

Main entry point for archiving before deletion.

**Returns**: `bool` - True if archived or relay disabled

### `format_relay_metadata(component, action, user_id, role, data)`

Create metadata envelope with checksum.

**Returns**: `dict` - Metadata with timestamp, hash, retention

### `verify_archive(metadata, data)`

Verify archive integrity using checksum.

**Returns**: `bool` - True if checksum matches

### `retry_queued_items(max_retries=3)`

Retry sending queued emails from failed attempts.

**Returns**: `dict` - Success/failure counts

### `get_queued_items()`

Get list of queued relay items.

**Returns**: `list[Path]` - Queue file paths

---

For complete documentation, see [POSTGRES_MIGRATION.md](../POSTGRES_MIGRATION.md#secure-data-relay-protocol)
