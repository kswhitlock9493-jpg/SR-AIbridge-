-- 1. Formal Doctrine Table
CREATE TABLE doctrine_logs (
    id SERIAL PRIMARY KEY,
    doctrine TEXT NOT NULL,
    ratified BOOLEAN DEFAULT FALSE,
    ratified_by VARCHAR(100),
    ratified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Mission Logs Table
CREATE TABLE mission_logs (
    id SERIAL PRIMARY KEY,
    mission_name VARCHAR(150) NOT NULL,
    status VARCHAR(50) NOT NULL,         -- e.g. "active", "queued", "completed"
    assigned_agents TEXT[],              -- list of agents by name/id
    admiral VARCHAR(100),                -- mission owner
    details TEXT,                        -- mission description / orders
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 3. Agents Table
CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'offline',
    capabilities JSONB,                  -- flexible structure for AI abilities
    last_seen TIMESTAMPTZ DEFAULT NOW()
);