-- ===== SR-AIbridge • System Confidence Table =====
-- Schema update for infrastructure stabilization framework
-- Adds real-time health state tracking for the Bridge system

CREATE TABLE IF NOT EXISTS system_confidence (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(32) NOT NULL,
  source VARCHAR(64),
  details JSONB
);

-- Add index for faster timestamp queries
CREATE INDEX IF NOT EXISTS idx_system_confidence_timestamp ON system_confidence(timestamp DESC);

-- Add index for status queries
CREATE INDEX IF NOT EXISTS idx_system_confidence_status ON system_confidence(status);

-- Grant permissions to application roles
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sr_app') THEN
    GRANT SELECT, INSERT, UPDATE ON system_confidence TO sr_app;
    GRANT USAGE, SELECT ON SEQUENCE system_confidence_id_seq TO sr_app;
  END IF;
  
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sr_ro') THEN
    GRANT SELECT ON system_confidence TO sr_ro;
  END IF;
END $$;
