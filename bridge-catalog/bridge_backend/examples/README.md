# SR-AIbridge Backend Examples

This directory contains example scripts demonstrating key features of SR-AIbridge.

## Available Examples

### relay_mailer_example.py

Demonstrates the **Secure Data Relay Protocol** for zero data loss:

```bash
cd bridge_backend
python examples/relay_mailer_example.py
```

**What it demonstrates:**
- Archiving data before deletion
- Role-based retention policies (Admiral/Captain/Agent)
- Checksum verification for data integrity
- Queue-based retry mechanism
- Archive verification

**Sample Output:**
```
🚀 SR-AIbridge Secure Data Relay Protocol Examples
============================================================

⚙️  Relay Status: ❌ DISABLED
📧 Relay Email: sraibridge@gmail.com

=== Example: Vault Data Deletion ===
📧 Archiving data before deletion...
✅ Data archived successfully
🗑️  Proceeding with deletion...

=== Example: Role-Based Retention Policies ===
👑 Admiral retention: -1 hours (permanent)
👨‍✈️ Captain retention: 14 hours
🤖 Agent retention: 7 hours
```

## Configuration

To enable actual email sending in examples:

1. Copy `.env.example` to `.env` in the project root
2. Set the following variables:

```bash
RELAY_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

For Gmail, create an App Password:
1. Enable 2-Step Verification
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Generate a password for "SR-AIbridge"
4. Use that in `SMTP_PASSWORD`

## Adding New Examples

When creating new examples:

1. Add import path fix at the top:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

2. Use clear section headers with emojis for readability
3. Include error handling and success/failure messages
4. Document configuration requirements
5. Add the example to this README

## Related Documentation

- [POSTGRES_MIGRATION.md](../../POSTGRES_MIGRATION.md) - PostgreSQL setup guide
- [README.md](../../README.md) - Main project documentation
- [.env.example](../../.env.example) - Environment variable template
