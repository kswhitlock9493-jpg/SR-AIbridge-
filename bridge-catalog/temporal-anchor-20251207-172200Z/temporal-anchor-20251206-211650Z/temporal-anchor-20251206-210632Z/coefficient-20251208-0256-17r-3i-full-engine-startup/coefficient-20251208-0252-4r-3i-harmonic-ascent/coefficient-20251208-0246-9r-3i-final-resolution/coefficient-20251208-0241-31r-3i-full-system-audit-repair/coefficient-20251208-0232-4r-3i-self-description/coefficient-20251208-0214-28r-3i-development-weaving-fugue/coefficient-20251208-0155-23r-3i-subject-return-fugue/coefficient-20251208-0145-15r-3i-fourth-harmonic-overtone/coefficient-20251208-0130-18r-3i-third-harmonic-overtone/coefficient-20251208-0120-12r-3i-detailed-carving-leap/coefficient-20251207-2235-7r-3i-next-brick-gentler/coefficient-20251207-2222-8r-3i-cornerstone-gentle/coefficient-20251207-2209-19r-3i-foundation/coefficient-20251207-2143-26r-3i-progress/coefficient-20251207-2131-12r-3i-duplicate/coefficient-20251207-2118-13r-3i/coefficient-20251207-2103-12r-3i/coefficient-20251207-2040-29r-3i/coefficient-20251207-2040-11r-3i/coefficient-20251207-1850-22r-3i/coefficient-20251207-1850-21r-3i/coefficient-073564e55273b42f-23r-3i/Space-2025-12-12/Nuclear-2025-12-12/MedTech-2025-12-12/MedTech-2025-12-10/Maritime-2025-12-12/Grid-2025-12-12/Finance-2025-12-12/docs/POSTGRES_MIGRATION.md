# PostgreSQL Migration Guide for SR-AIbridge

This guide covers the complete migration from SQLite to PostgreSQL for production deployments.

## Overview

SR-AIbridge now includes production-grade PostgreSQL support with:
- Monthly partitioned tables for logs and memories
- Role-based access control (Admiral, Captain, Agent)
- Automatic indexing and query optimization
- Secure Data Relay Protocol for zero data loss

---

## Quick Start

### 1. Create PostgreSQL Database on Render

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **PostgreSQL**
3. Configure:
   - **Name**: `sr-aibridge-db`
   - **Database**: `sr_aibridge`
   - **User**: `sr_app`
   - **Region**: Choose closest to your web service
   - **Plan**: Pro ($55/mo, 50 GB recommended)
4. Click **Create Database**
5. Copy the **Internal Database URL** from the database info page

### 2. Initialize PostgreSQL Schema

**Option A: Via Render psql Console**
1. Open your database in Render Dashboard
2. Click **Shell** tab
3. Copy and paste the entire contents of `init.sql`
4. Press Enter to execute

**Option B: From Local Machine**
```bash
# Using the DATABASE_URL from Render
psql "postgresql://sr_app:password@hostname.render.com:5432/sr_aibridge" \
  -v ON_ERROR_STOP=1 \
  -f init.sql
```

### 3. Update Environment Variables

Update your `.env` file (or Render environment variables):

```bash
# Change from SQLite
DATABASE_TYPE=postgres
DATABASE_URL=postgresql+asyncpg://sr_app:password@hostname.render.com:5432/sr_aibridge
```

**For Render Web Service:**
1. Go to your web service in Render Dashboard
2. Navigate to **Environment** tab
3. Update or add:
   - `DATABASE_TYPE` = `postgres`
   - `DATABASE_URL` = (use the Internal Database URL, but change `postgresql://` to `postgresql+asyncpg://`)

### 4. Deploy and Verify

```bash
# Redeploy your service (Render will auto-deploy on git push)
git add .
git commit -m "Enable PostgreSQL"
git push origin main

# Verify connection
curl https://your-service.onrender.com/health
```

---

## Schema Details

### Tables Created

The `init.sql` script creates the following schema in the `sra` namespace:

#### Core Tables
- **sra.users** - Admiral/Captain/Agent identities
- **sra.agents** - Agent records with capabilities
- **sra.missions** - Mission tracking with assignments
- **sra.mission_agents** - Mission-to-agent mapping

#### Partitioned Tables (Monthly)
- **sra.vault_logs** - System logs (auto-partitioned by month)
- **sra.brain_memories** - AI memory storage (auto-partitioned by month)

#### Supporting Tables
- **sra.messages** - Captain ↔ Captain and Captain ↔ Agent messaging
- **sra.vessels** - Fleet/Armada management
- **sra.guardians** - Guardian system monitoring
- **sra.admiral_keys** - Cryptographic custody keys

#### Views
- **sra.v_captain_missions** - Captain-specific mission view
- **sra.v_agent_jobs** - Agent job assignments

### Automatic Features

1. **Monthly Partitions**: Creates 13 months of partitions (current + next 12)
2. **Auto-Indexes**: GIN indexes for JSONB, trigram for text search
3. **Optimized Vacuum**: Tuned autovacuum for high-write tables
4. **Role-Based Access**: `sr_admin`, `sr_app`, `sr_ro` roles with appropriate grants

---

## Monthly Maintenance

To keep your database optimized and manage partition growth:

### Automated Maintenance (Recommended)

**Option 1: GitHub Actions** (add to `.github/workflows/db-maintenance.yml`):
```yaml
name: PostgreSQL Monthly Maintenance
on:
  schedule:
    - cron: '0 2 1 * *'  # 2 AM on the 1st of each month
  workflow_dispatch:

jobs:
  maintenance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run maintenance script
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f maintenance.sql
```

**Option 2: Render Cron Job**:
1. Create a new Background Worker in Render
2. Set command: `psql $DATABASE_URL -f maintenance.sql`
3. Schedule: `0 2 1 * *` (monthly on the 1st)

### Manual Maintenance

Run whenever you want to create next month's partition or clean old data:

```bash
psql "$DATABASE_URL" -f maintenance.sql
```

This script:
- Creates next month's partitions for `vault_logs` and `brain_memories`
- Drops partitions older than 18 months
- Re-applies indexes on new partitions

---

## Secure Data Relay Protocol

### Overview

The Secure Data Relay Protocol ensures **zero data loss** by automatically archiving data to `sraibridge@gmail.com` before any deletion.

### Setup

1. **Enable in `.env`:**
```bash
RELAY_ENABLED=true
RELAY_EMAIL=sraibridge@gmail.com
RELAY_MODE=pre_delete
RELAY_BACKUP_PATH=/var/srbridge/tmp/relay_queue

# SMTP Configuration (Gmail with App Password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=sraibridge@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
```

2. **Create Gmail App Password:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification (if not already enabled)
   - Go to **App Passwords**
   - Generate a new app password for "SR-AIbridge"
   - Use this password in `SMTP_PASSWORD`

### Usage in Code

```python
from utils.relay_mailer import relay_mailer

# Before deleting data
await relay_mailer.archive_before_delete(
    component="vault",
    user_id="captain_alpha",
    role="captain",
    record={"id": 123, "data": "mission logs"}
)

# Then perform deletion
await delete_record(123)
```

### Role-Based Retention

- **Admiral**: Permanent archival (no expiration)
- **Captain**: 14-hour memory buffer
- **Agent**: 7-hour memory buffer

### Verify Archives

Check `sraibridge@gmail.com` inbox with labels:
- `missions/deleted`
- `vault/archive`
- `brain/memory-dump`
- `system/errors`

---

## Migration from SQLite

### Export Existing Data

```bash
# Export SQLite data
sqlite3 bridge.db .dump > backup.sql

# Or use Python script
python bridge_backend/seed.py --export
```

### Import to PostgreSQL

```bash
# After running init.sql, import data
# Note: You may need to adjust column mappings

# For simple data migration
psql "$DATABASE_URL" -f backup.sql
```

**Note:** The PostgreSQL schema uses UUIDs and different column names than the current SQLite schema. You may need to write a custom migration script to map:
- `missions.id` (int) → `sra.missions.id` (uuid)
- `agents.id` (int) → `sra.agents.id` (uuid)
- etc.

---

## Performance Tuning

### Connection Pooling

The backend uses SQLAlchemy's async connection pooling. For high-traffic deployments:

```python
# In bridge_backend/bridge_core/db/db_manager.py
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,          # Increase pool size
    max_overflow=10,       # Allow overflow connections
    pool_pre_ping=True     # Verify connections before use
)
```

### Monitoring Queries

```sql
-- Enable pg_stat_statements (one-time setup)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- View slow queries
SELECT 
  mean_exec_time,
  calls,
  query
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- queries taking > 100ms
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### Index Analysis

```sql
-- Check index usage
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read
FROM pg_stat_user_indexes
WHERE schemaname = 'sra'
ORDER BY idx_scan;

-- Find missing indexes
SELECT 
  schemaname,
  tablename,
  seq_scan,
  seq_tup_read
FROM pg_stat_user_tables
WHERE schemaname = 'sra'
  AND seq_scan > 1000  -- tables with many sequential scans
ORDER BY seq_scan DESC;
```

---

## Troubleshooting

### Connection Refused

**Problem**: `connection refused` or `timeout`

**Solution**:
- Verify `DATABASE_URL` is correct
- Ensure database allows connections from your IP (Render handles this automatically)
- Check that database is running (not paused)

### Permission Denied

**Problem**: `permission denied for schema sra`

**Solution**:
```sql
-- Grant schema access
GRANT USAGE ON SCHEMA sra TO sr_app;
GRANT ALL ON ALL TABLES IN SCHEMA sra TO sr_app;
```

### Extension Not Available

**Problem**: `extension "pg_trgm" is not available`

**Solution**:
- Most managed PostgreSQL providers (Render, AWS RDS, etc.) support these extensions
- Contact your provider if extensions are blocked
- For self-hosted: `apt-get install postgresql-contrib`

### Partition Not Found

**Problem**: `no partition found for row with created_at = ...`

**Solution**:
- Partition may not exist for that date range
- Run `maintenance.sql` to create future partitions
- For historical data, manually create partition:
```sql
CREATE TABLE sra.vault_logs_202410 PARTITION OF sra.vault_logs
  FOR VALUES FROM ('2024-10-01') TO ('2024-11-01');
```

---

## Backup and Recovery

### Automated Backups (Render)

Render PostgreSQL Pro plan includes:
- Daily automatic backups
- 7-day retention
- Point-in-time recovery
- Available in Dashboard → Database → Backups

### Manual Backup

```bash
# Full database dump
pg_dump "$DATABASE_URL" > backup_$(date +%Y%m%d).sql

# Schema only
pg_dump "$DATABASE_URL" --schema-only > schema_backup.sql

# Data only
pg_dump "$DATABASE_URL" --data-only > data_backup.sql
```

### Restore

```bash
# Restore full backup
psql "$DATABASE_URL" < backup_20241004.sql

# Restore specific table
pg_restore -d "$DATABASE_URL" -t sra.missions backup.dump
```

---

## Next Steps

1. ✅ Initialize PostgreSQL with `init.sql`
2. ✅ Update environment variables
3. ✅ Deploy and verify connection
4. ⬜ Configure Secure Data Relay (optional)
5. ⬜ Set up automated monthly maintenance
6. ⬜ Migrate existing SQLite data (if needed)
7. ⬜ Monitor performance and optimize

---

## Support

For issues or questions:
- Check the [README.md](../README.md) troubleshooting section
- Review [DEPLOYMENT.md](../DEPLOYMENT.md) for Render-specific guidance
- Open an issue on GitHub

---

**SR-AIbridge PostgreSQL Migration Guide v1.0**
