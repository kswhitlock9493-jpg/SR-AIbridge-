"""
Genesis Event Persistence
Idempotency, deduplication, DLQ (Dead Letter Queue), and event store
"""

import os
import json
import logging
import sqlite3
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
GENESIS_PERSIST_BACKEND = os.getenv("GENESIS_PERSIST_BACKEND", "sqlite")
GENESIS_DB_PATH = os.getenv("GENESIS_DB_PATH", "bridge_backend/genesis/events.db")
GENESIS_DEDUP_TTL_SECS = int(os.getenv("GENESIS_DEDUP_TTL_SECS", "86400"))
GENESIS_DLQ_MAX_RETRIES = int(os.getenv("GENESIS_DLQ_MAX_RETRIES", "3"))

# Ensure persistence directory exists
Path(GENESIS_DB_PATH).parent.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------
# GenesisPersistence Class
# ---------------------------------------------------------------------
class GenesisPersistence:
    """
    Handles event persistence, deduplication, and DLQ.
    Supports both SQLite and PostgreSQL backends.
    """

    def __init__(self):
        self._db_path = GENESIS_DB_PATH
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self):
        """Initialize database schema."""
        async with self._lock:
            if self._initialized:
                return

            try:
                conn = sqlite3.connect(self._db_path)
                cursor = conn.cursor()

                # Enable Write-Ahead Logging
                cursor.execute("PRAGMA journal_mode=WAL;")

                # ---------------- Event store ----------------
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id TEXT PRIMARY KEY,
                        ts TIMESTAMP NOT NULL,
                        topic TEXT NOT NULL,
                        source TEXT NOT NULL,
                        kind TEXT NOT NULL,
                        correlation_id TEXT,
                        causation_id TEXT,
                        schema TEXT,
                        payload TEXT NOT NULL,
                        watermark INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # ---------------- Deduplication ----------------
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dedupe (
                        dedupe_key TEXT PRIMARY KEY,
                        event_id TEXT NOT NULL,
                        first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP
                    );
                """)

                # ---------------- DLQ ----------------
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS dlq (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id TEXT NOT NULL,
                        topic TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        error TEXT NOT NULL,
                        retry_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_retry TIMESTAMP
                    );
                """)

                # Indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_topic ON events(topic);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_dedupe_expires_at ON dedupe(expires_at);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_dlq_event_id ON dlq(event_id);")

                conn.commit()
                conn.close()
                self._initialized = True
                logger.info("✅ Genesis persistence initialized")

            except Exception as e:
                logger.error(f"❌ Failed to initialize Genesis persistence: {e}")
                raise

    # -----------------------------------------------------------------
    # Duplicate Check
    # -----------------------------------------------------------------
    async def is_duplicate(self, dedupe_key: str) -> bool:
        """Check if event is a duplicate."""
        async with self._lock:
            try:
                conn = sqlite3.connect(self._db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT event_id FROM dedupe WHERE dedupe_key=?;", (dedupe_key,))
                result = cursor.fetchone()
                conn.close()
                return result is not None
            except Exception as e:
                logger.error(f"❌ Failed to check duplicate: {e}")
                return False

    # -----------------------------------------------------------------
    # Record Event
    # -----------------------------------------------------------------
    async def record_event(self, event: Optional[Dict[str, Any]] = None, **kwargs):
        """Record an event in the store and dedupe table."""
        if event is None:
            event = kwargs

        async with self._lock:
            try:
                conn = sqlite3.connect(self._db_path)
                cursor = conn.cursor()

                # Extract event fields safely
                event_id = event.get("id") or event.get("event_id")
                dedupe_key = event.get("dedupe_key", event_id)
                expires_at = datetime.now(timezone.utc) + timedelta(seconds=GENESIS_DEDUP_TTL_SECS)

                cursor.execute("""
                    INSERT OR IGNORE INTO events (
                        id, ts, topic, source, kind, correlation_id,
                        causation_id, schema, payload, watermark
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    event_id,
                    event.get("ts"),
                    event.get("topic"),
                    event.get("source"),
                    event.get("kind"),
                    event.get("correlation_id"),
                    event.get("causation_id"),
                    event.get("schema"),
                    json.dumps(event.get("payload")),
                    event.get("watermark", 0),
                ))

                cursor.execute("""
                    INSERT OR REPLACE INTO dedupe (dedupe_key, event_id, expires_at)
                    VALUES (?, ?, ?);
                """, (dedupe_key, event_id, expires_at))

                conn.commit()
                conn.close()
                logger.debug(f"✅ Event {event_id} recorded successfully")

            except Exception as e:
                logger.error(f"❌ Failed to record event: {e}")
                raise

    # -----------------------------------------------------------------
    # Ensure Ready
    # -----------------------------------------------------------------
    async def ensure_ready(self):
        """Auto-create schema if database is empty."""
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events';")
            exists = cursor.fetchone()
            conn.close()
            if not exists:
                logger.info("🧱 Events table missing — initializing persistence schema...")
                await self.initialize()
        except Exception as e:
            logger.error(f"❌ Failed to verify persistence readiness: {e}")
            raise

    # -----------------------------------------------------------------
    # DLQ Management
    # -----------------------------------------------------------------
    async def add_to_dlq(self, event_id: str, topic: str, payload: str, error: str):
        """Store failed events in the DLQ."""
        async with self._lock:
            try:
                conn = sqlite3.connect(self._db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO dlq (event_id, topic, payload, error)
                    VALUES (?, ?, ?, ?);
                """, (event_id, topic, payload, error))
                conn.commit()
                conn.close()
                logger.warning(f"⚠️ Event {event_id} added to DLQ")
            except Exception as e:
                logger.error(f"❌ Failed to insert into DLQ: {e}")
                raise


# ---------------------------------------------------------------------
# Initialize global persistence instance
# ---------------------------------------------------------------------
genesis_persistence = GenesisPersistence()
