-- ===== SR-AIbridge • PostgreSQL Monthly Maintenance =====
-- Run this monthly to create next partition and prune old ones.
-- Can be automated via GitHub Actions, cron job, or manual execution.

-- Create next month partitions & drop ones older than 18 months

DO $$
DECLARE
  next_month DATE := (date_trunc('month', now()) + interval '1 month')::date;
  drop_before DATE := (date_trunc('month', now()) - interval '18 months')::date;
  p RECORD;
BEGIN
  -- Create next month partitions if missing
  EXECUTE format(
    'CREATE TABLE IF NOT EXISTS sra.vault_logs_%s PARTITION OF sra.vault_logs
       FOR VALUES FROM (%L) TO (%L);',
    to_char(next_month, 'YYYYMM'), next_month, next_month + interval '1 month'
  );
  EXECUTE format(
    'CREATE TABLE IF NOT EXISTS sra.brain_memories_%s PARTITION OF sra.brain_memories
       FOR VALUES FROM (%L) TO (%L);',
    to_char(next_month, 'YYYYMM'), next_month, next_month + interval '1 month'
  );

  -- Re-apply key indexes on new vault_logs partition
  EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON sra.vault_logs_%s (level);',
                 'idx_sra_vault_logs_'||to_char(next_month,'YYYYMM')||'_level',
                 to_char(next_month,'YYYYMM'));
  EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON sra.vault_logs_%s USING GIN (metadata jsonb_path_ops);',
                 'idx_sra_vault_logs_'||to_char(next_month,'YYYYMM')||'_meta_gin',
                 to_char(next_month,'YYYYMM'));
  EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON sra.vault_logs_%s USING GIN (message gin_trgm_ops);',
                 'idx_sra_vault_logs_'||to_char(next_month,'YYYYMM')||'_msg_trgm',
                 to_char(next_month,'YYYYMM'));
  EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON sra.vault_logs_%s (captain_id, created_at DESC);',
                 'idx_sra_vault_logs_'||to_char(next_month,'YYYYMM')||'_captain_time',
                 to_char(next_month,'YYYYMM'));
  EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON sra.vault_logs_%s (agent_id, created_at DESC);',
                 'idx_sra_vault_logs_'||to_char(next_month,'YYYYMM')||'_agent_time',
                 to_char(next_month,'YYYYMM'));

  -- Re-apply key indexes on new brain_memories partition
  EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON sra.brain_memories_%s (captain_id, created_at DESC);',
                 'idx_sra_brain_memories_'||to_char(next_month,'YYYYMM')||'_captain_time',
                 to_char(next_month,'YYYYMM'));
  EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON sra.brain_memories_%s USING GIN (content gin_trgm_ops);',
                 'idx_sra_brain_memories_'||to_char(next_month,'YYYYMM')||'_content_trgm',
                 to_char(next_month,'YYYYMM'));
  EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON sra.brain_memories_%s (category);',
                 'idx_sra_brain_memories_'||to_char(next_month,'YYYYMM')||'_category',
                 to_char(next_month,'YYYYMM'));

  -- Drop very old partitions (logs & memories)
  FOR p IN
    SELECT inhrelid::regclass AS child, pg_get_expr(relpartbound, inhrelid) AS bound
    FROM pg_inherits i
    JOIN pg_class c ON c.oid = i.inhrelid
    JOIN pg_class p2 ON p2.oid = i.inhparent
    WHERE p2.relname IN ('vault_logs','brain_memories') AND p2.relnamespace = 'sra'::regnamespace
  LOOP
    -- crude parse: if partition end < drop_before, drop it
    IF to_date(substring(p.child::text from '.*_(\d{6})$'), 'YYYYMM') < to_date(to_char(drop_before,'YYYYMM'),'YYYYMM') THEN
      EXECUTE format('DROP TABLE IF EXISTS %s;', p.child);
      RAISE NOTICE 'Dropped old partition: %', p.child;
    END IF;
  END LOOP;
END $$;
