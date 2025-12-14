-- ===== SR-AIbridge Blueprint + AgentJobs Postgres Partition Patch =====
-- Monthly partitioning for agent_jobs table to handle high-volume job tracking
-- Run this after the base init.sql if you want partitioned agent_jobs

-- 1) Create agent_jobs table (partitioned by created_at)
CREATE TABLE IF NOT EXISTS sra.agent_jobs (
  id               BIGSERIAL,
  mission_id       UUID REFERENCES sra.missions(id) ON DELETE CASCADE,
  blueprint_id     BIGINT,  -- FK to blueprints table (not in base schema)
  captain_id       UUID REFERENCES sra.users(id) ON DELETE SET NULL,
  agent_name       TEXT,
  role             sra.role_enum NOT NULL DEFAULT 'agent',
  task_key         TEXT NOT NULL,  -- e.g., "T2.1"
  task_desc        TEXT NOT NULL,
  status           TEXT NOT NULL DEFAULT 'queued',  -- queued|running|done|failed|skipped
  inputs           JSONB NOT NULL DEFAULT '{}'::jsonb,
  outputs          JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- 2) Create monthly partitions (current + next 12 months)
DO $$
DECLARE
  start_month DATE := date_trunc('month', now())::date;
  d DATE;
BEGIN
  FOR d IN 0..12 LOOP
    EXECUTE format(
      'CREATE TABLE IF NOT EXISTS sra.agent_jobs_%s PARTITION OF sra.agent_jobs
         FOR VALUES FROM (%L) TO (%L)
         WITH (autovacuum_vacuum_scale_factor=0.05, autovacuum_analyze_scale_factor=0.02);',
      to_char(start_month + (d || ' month')::interval, 'YYYYMM'),
      (start_month + (d || ' month')::interval),
      (start_month + ((d+1) || ' month')::interval)
    );
  END LOOP;
END $$;

-- 3) Create indexes on each partition
DO $$
DECLARE
  part regclass;
BEGIN
  FOR part IN SELECT inhrelid::regclass
              FROM pg_inherits
              WHERE inhparent = 'sra.agent_jobs'::regclass
  LOOP
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %s (mission_id);',
                   'idx_'||part::text||'_mission', part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %s (captain_id);',
                   'idx_'||part::text||'_captain', part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %s (task_key);',
                   'idx_'||part::text||'_task_key', part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %s (status);',
                   'idx_'||part::text||'_status', part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %s USING GIN (inputs jsonb_path_ops);',
                   'idx_'||part::text||'_inputs_gin', part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %s USING GIN (outputs jsonb_path_ops);',
                   'idx_'||part::text||'_outputs_gin', part);
  END LOOP;
END $$;

-- 4) Create blueprints table (not partitioned, lower volume)
CREATE TABLE IF NOT EXISTS sra.blueprints (
  id               BIGSERIAL PRIMARY KEY,
  mission_id       UUID REFERENCES sra.missions(id) ON DELETE SET NULL,
  captain_id       UUID REFERENCES sra.users(id) ON DELETE SET NULL,
  title            TEXT NOT NULL,
  brief            TEXT NOT NULL,
  plan             JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_blueprints_mission ON sra.blueprints(mission_id);
CREATE INDEX IF NOT EXISTS idx_blueprints_captain ON sra.blueprints(captain_id);
CREATE INDEX IF NOT EXISTS idx_blueprints_plan_gin ON sra.blueprints USING GIN (plan jsonb_path_ops);

-- 5) Add foreign key from agent_jobs to blueprints
-- Note: This needs to be added AFTER partitions are created
DO $$
BEGIN
  -- Check if constraint doesn't exist
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE constraint_name = 'fk_agent_jobs_blueprint'
  ) THEN
    -- We can't add FK to parent partition table in Postgres
    -- Instead, document that blueprint_id references blueprints.id
    -- Application-level enforcement required
    COMMENT ON COLUMN sra.agent_jobs.blueprint_id IS 'References sra.blueprints(id) - application-enforced FK';
  END IF;
END $$;

-- 6) Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON sra.agent_jobs TO sr_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON sra.blueprints TO sr_app;
GRANT SELECT ON sra.agent_jobs TO sr_ro;
GRANT SELECT ON sra.blueprints TO sr_ro;

-- 7) Create view for easy job querying
CREATE OR REPLACE VIEW sra.v_agent_job_summary AS
SELECT 
  aj.id,
  aj.mission_id,
  aj.blueprint_id,
  aj.task_key,
  aj.task_desc,
  aj.status,
  aj.agent_name,
  aj.created_at,
  aj.updated_at,
  m.title as mission_title,
  b.title as blueprint_title,
  u.handle as captain_handle
FROM sra.agent_jobs aj
LEFT JOIN sra.missions m ON aj.mission_id = m.id
LEFT JOIN sra.blueprints b ON aj.blueprint_id = b.id
LEFT JOIN sra.users u ON aj.captain_id = u.id;

GRANT SELECT ON sra.v_agent_job_summary TO sr_app, sr_ro;

-- 8) Maintenance note
COMMENT ON TABLE sra.agent_jobs IS 'Monthly partitioned job tracking. Run maintenance.sql monthly to create future partitions.';
