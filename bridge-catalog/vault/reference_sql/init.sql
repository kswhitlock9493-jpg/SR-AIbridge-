-- ===== SR-AIbridge • PostgreSQL bootstrap =====
-- Safe to run multiple times (IF NOT EXISTS everywhere).

-- 1) Extensions (all available on managed Postgres)
CREATE EXTENSION IF NOT EXISTS pgcrypto;         -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- uuid_generate_v4()
CREATE EXTENSION IF NOT EXISTS pg_trgm;          -- fast LIKE/ILIKE/%% search
CREATE EXTENSION IF NOT EXISTS btree_gin;        -- GIN on scalars
-- (Optional) CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 2) Roles (adjust passwords if you want DB-native auth instead of Render env)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'sr_admin') THEN
    CREATE ROLE sr_admin LOGIN;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'sr_app') THEN
    CREATE ROLE sr_app LOGIN;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'sr_ro') THEN
    CREATE ROLE sr_ro LOGIN;
  END IF;
END $$;

-- 3) Namespace
CREATE SCHEMA IF NOT EXISTS sra;
GRANT USAGE ON SCHEMA sra TO sr_app, sr_ro;
ALTER ROLE sr_app IN DATABASE current_database() SET search_path = sra, public;
ALTER ROLE sr_ro  IN DATABASE current_database() SET search_path = sra, public;

-- 4) Enumerations
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='role_enum') THEN
    CREATE TYPE sra.role_enum AS ENUM ('admiral','captain','agent');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='mission_status_enum') THEN
    CREATE TYPE sra.mission_status_enum AS ENUM ('pending','active','completed','failed');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='mission_priority_enum') THEN
    CREATE TYPE sra.mission_priority_enum AS ENUM ('low','medium','high','critical');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='log_level_enum') THEN
    CREATE TYPE sra.log_level_enum AS ENUM ('debug','info','warning','error','critical','security');
  END IF;
END $$;

-- 5) Core identities
CREATE TABLE IF NOT EXISTS sra.users (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  handle           TEXT NOT NULL UNIQUE,         -- "Captain-Alpha" etc.
  display_name     TEXT,
  email            TEXT UNIQUE,
  role             sra.role_enum NOT NULL,       -- admiral|captain|agent
  status           TEXT DEFAULT 'online',
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_users_role ON sra.users(role);
CREATE INDEX IF NOT EXISTS idx_users_email_trgm ON sra.users USING GIN (email gin_trgm_ops);

-- 6) Agents (separate record even if some captains act as agents)
CREATE TABLE IF NOT EXISTS sra.agents (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name             TEXT NOT NULL,
  owner_captain_id UUID REFERENCES sra.users(id) ON DELETE SET NULL, -- captain who owns/dispatches
  role             sra.role_enum NOT NULL DEFAULT 'agent',
  status           TEXT NOT NULL DEFAULT 'offline',
  capabilities     JSONB NOT NULL DEFAULT '{}'::jsonb,
  last_heartbeat   TIMESTAMPTZ,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT agents_role_agent CHECK (role = 'agent')
);
CREATE INDEX IF NOT EXISTS idx_agents_owner ON sra.agents(owner_captain_id);
CREATE INDEX IF NOT EXISTS idx_agents_caps_gin ON sra.agents USING GIN (capabilities jsonb_path_ops);

-- 7) Missions + assignment map
CREATE TABLE IF NOT EXISTS sra.missions (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title            TEXT NOT NULL,
  description      TEXT,
  priority         sra.mission_priority_enum NOT NULL DEFAULT 'medium',
  status           sra.mission_status_enum NOT NULL DEFAULT 'pending',
  captain_id       UUID REFERENCES sra.users(id) ON DELETE SET NULL,
  role             sra.role_enum NOT NULL DEFAULT 'captain',  -- captain|agent stream origin
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at     TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_missions_captain ON sra.missions(captain_id);
CREATE INDEX IF NOT EXISTS idx_missions_status  ON sra.missions(status);
CREATE INDEX IF NOT EXISTS idx_missions_role    ON sra.missions(role);
CREATE INDEX IF NOT EXISTS idx_missions_title_trgm ON sra.missions USING GIN (title gin_trgm_ops);

CREATE TABLE IF NOT EXISTS sra.mission_agents (
  mission_id UUID NOT NULL REFERENCES sra.missions(id) ON DELETE CASCADE,
  agent_id   UUID NOT NULL REFERENCES sra.agents(id)   ON DELETE CASCADE,
  assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (mission_id, agent_id)
);

-- 8) Vault logs (MONTHLY PARTITIONED)
CREATE TABLE IF NOT EXISTS sra.vault_logs (
  id          BIGSERIAL,
  level       sra.log_level_enum NOT NULL DEFAULT 'info',
  message     TEXT NOT NULL,
  source      TEXT,                         -- module/engine
  metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,
  captain_id  UUID REFERENCES sra.users(id) ON DELETE SET NULL,
  agent_id    UUID REFERENCES sra.agents(id) ON DELETE SET NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Current + next 12 months partitions
DO $$
DECLARE
  start_month DATE := date_trunc('month', now())::date;
  d DATE;
BEGIN
  FOR d IN 0..12 LOOP
    EXECUTE format(
      'CREATE TABLE IF NOT EXISTS sra.vault_logs_%s PARTITION OF sra.vault_logs
         FOR VALUES FROM (%L) TO (%L)
         WITH (autovacuum_vacuum_scale_factor=0.05, autovacuum_analyze_scale_factor=0.02);',
      to_char(start_month + (d || ' month')::interval, 'YYYYMM'),
      (start_month + (d || ' month')::interval),
      (start_month + ((d+1) || ' month')::interval)
    );
  END LOOP;
END $$;

-- High-value indexes on each partition (inheritance doesn't propagate GIN)
DO $$
DECLARE
  part regclass;
BEGIN
  FOR part IN SELECT inhrelid::regclass
              FROM pg_inherits
              WHERE inhparent = 'sra.vault_logs'::regclass
  LOOP
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %s (level);',
                   'idx_'||part::text||'_level', part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %s USING GIN (metadata jsonb_path_ops);',
                   'idx_'||part::text||'_meta_gin', part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %s USING GIN (message gin_trgm_ops);',
                   'idx_'||part::text||'_msg_trgm', part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %s (captain_id, created_at DESC);',
                   'idx_'||part::text||'_captain_time', part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %s (agent_id, created_at DESC);',
                   'idx_'||part::text||'_agent_time', part);
  END LOOP;
END $$;

-- 9) Brain memories (also monthly partitioned; cryptographically attestable)
CREATE TABLE IF NOT EXISTS sra.brain_memories (
  id            UUID DEFAULT gen_random_uuid(),
  captain_id    UUID REFERENCES sra.users(id) ON DELETE SET NULL,
  agent_id      UUID REFERENCES sra.agents(id) ON DELETE SET NULL,
  category      TEXT NOT NULL DEFAULT 'general',
  content       TEXT NOT NULL,
  signature     TEXT,           -- detached signature (Ed25519)
  signer        TEXT,           -- key id / fingerprint
  retained_until TIMESTAMPTZ,   -- tier-based TTL
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

DO $$
DECLARE
  start_month DATE := date_trunc('month', now())::date;
  d DATE;
BEGIN
  FOR d IN 0..12 LOOP
    EXECUTE format(
      'CREATE TABLE IF NOT EXISTS sra.brain_memories_%s PARTITION OF sra.brain_memories
         FOR VALUES FROM (%L) TO (%L)
         WITH (autovacuum_vacuum_scale_factor=0.05, autovacuum_analyze_scale_factor=0.02);',
      to_char(start_month + (d || ' month')::interval, 'YYYYMM'),
      (start_month + (d || ' month')::interval),
      (start_month + ((d+1) || ' month')::interval)
    );
  END LOOP;
END $$;

DO $$
DECLARE
  part regclass;
BEGIN
  FOR part IN SELECT inhrelid::regclass
              FROM pg_inherits
              WHERE inhparent = 'sra.brain_memories'::regclass
  LOOP
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %s (captain_id, created_at DESC);',
                   'idx_'||part::text||'_captain_time', part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %s USING GIN (content gin_trgm_ops);',
                   'idx_'||part::text||'_content_trgm', part);
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %s (category);',
                   'idx_'||part::text||'_category', part);
  END LOOP;
END $$;

-- 10) Captain messaging (captain↔captain) and captain↔agent chat
CREATE TABLE IF NOT EXISTS sra.messages (
  id            BIGSERIAL PRIMARY KEY,
  from_user_id  UUID REFERENCES sra.users(id) ON DELETE SET NULL,
  to_user_id    UUID REFERENCES sra.users(id) ON DELETE SET NULL,
  channel       TEXT DEFAULT 'direct',  -- 'direct' | 'broadcast'
  body          TEXT NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_messages_to_time ON sra.messages(to_user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_body_trgm ON sra.messages USING GIN (body gin_trgm_ops);

-- 11) Fleet (Armada)
CREATE TABLE IF NOT EXISTS sra.vessels (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          TEXT NOT NULL,
  role          sra.role_enum NOT NULL DEFAULT 'captain',
  owner_id      UUID REFERENCES sra.users(id) ON DELETE SET NULL, -- captain owner / admiral
  status        TEXT NOT NULL DEFAULT 'docked',
  location      JSONB NOT NULL DEFAULT '{}'::jsonb,               -- {lat,lon,region}
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_vessels_owner ON sra.vessels(owner_id);
CREATE INDEX IF NOT EXISTS idx_vessels_loc_gin ON sra.vessels USING GIN (location jsonb_path_ops);

-- 12) Guardians & custody keys
CREATE TABLE IF NOT EXISTS sra.guardians (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          TEXT NOT NULL,
  status        TEXT NOT NULL DEFAULT 'active',
  last_heartbeat TIMESTAMPTZ,
  capabilities  JSONB NOT NULL DEFAULT '{}'::jsonb,
  health_score  NUMERIC(5,2),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sra.admiral_keys (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key_name           TEXT NOT NULL UNIQUE,
  public_key         TEXT NOT NULL,
  private_key_encrypted TEXT NOT NULL,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_used          TIMESTAMPTZ
);

-- 13) Autovacuum tuning for hot tables
ALTER TABLE sra.messages      SET (autovacuum_vacuum_scale_factor = 0.2, autovacuum_analyze_scale_factor = 0.1);
ALTER TABLE sra.missions      SET (autovacuum_vacuum_scale_factor = 0.2, autovacuum_analyze_scale_factor = 0.1);
ALTER TABLE sra.agents        SET (autovacuum_vacuum_scale_factor = 0.2, autovacuum_analyze_scale_factor = 0.1);

-- 14) Grants (tighten as needed)
GRANT USAGE ON SCHEMA sra TO sr_app, sr_ro;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sra TO sr_app;
GRANT SELECT ON ALL TABLES IN SCHEMA sra TO sr_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA sra GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sr_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA sra GRANT SELECT ON TABLES TO sr_ro;

-- 15) Helpful views for the API layer
CREATE OR REPLACE VIEW sra.v_captain_missions AS
  SELECT m.*, u.handle AS captain_handle
  FROM sra.missions m LEFT JOIN sra.users u ON u.id = m.captain_id
  WHERE m.role = 'captain';

CREATE OR REPLACE VIEW sra.v_agent_jobs AS
  SELECT m.*, array_agg(ma.agent_id) AS agents
  FROM sra.missions m
  LEFT JOIN sra.mission_agents ma ON ma.mission_id = m.id
  WHERE m.role = 'agent'
  GROUP BY m.id;

-- Done.