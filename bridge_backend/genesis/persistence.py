"""
Genesis Event Persistence
Idempotency, deduplication, DLQ, and event store
"""
import os
import json
import logging
import sqlite3
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Configuration
GENESIS_PERSIST_BACKEND = os.getenv("GENESIS_PERSIST_BACKEND", "sqlite")
GENESIS_DEDUP_TTL_SECS = int(os.getenv("GENESIS_DEDUP_TTL_SECS", "86400"))  # 24 hours
GENESIS_DB_PATH = os.getenv("GENESIS_DB_PATH", "bridge_backend/.genesis/events.db")
GENESIS_DLQ_MAX_RETRIES = int(os.getenv("GENESIS_DLQ_MAX_RETRIES", "3"))

# Ensure persistence directory exists
Path(GENESIS_DB_PATH).parent.mkdir(parents=True, exist_ok=True)


class GenesisPersistence:
    """
    Genesis event persistence with idempotency and DLQ
    
    Features:
    - Event store with watermark for replay
    - Dedupe tracking for idempotency
    - Dead Letter Queue (DLQ) for failed events
    - TTL-based cleanup
    """
    
    def __init__(self):
        self._db_path = GENESIS_DB_PATH
        self._lock = asyncio.Lock()
        self._initialized = False
    
    async def initialize(self):
        """Initialize database schema"""
        if self._initialized:
            return
        
        async with self._lock:
            if self._initialized:
                return
            
            try:
                conn = sqlite3.connect(self._db_path)
                cursor = conn.cursor()
                
                # Event store table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS genesis_events (
                        id TEXT PRIMARY KEY,
                        ts TIMESTAMP NOT NULL,
                        topic TEXT NOT NULL,
                        source TEXT NOT NULL,
                        kind TEXT NOT NULL,
                        correlation_id TEXT,
                        causation_id TEXT,
                        schema TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        watermark INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Dedupe tracking table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS genesis_dedupe (
                        dedupe_key TEXT PRIMARY KEY,
                        event_id TEXT NOT NULL,
                        first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL
                    )
                """)
                
                # DLQ table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS genesis_dlq (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id TEXT NOT NULL,
                        topic TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        error TEXT NOT NULL,
                        retry_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_retry TIMESTAMP
                    )
                """)
                
                # Indices for performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON genesis_events(ts)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_topic ON genesis_events(topic)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_watermark ON genesis_events(watermark)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_dedupe_expires ON genesis_dedupe(expires_at)")
                
                conn.commit()
                conn.close()
                
                self._initialized = True
                logger.info(f"✅ Genesis persistence initialized: {self._db_path}")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize Genesis persistence: {e}")
                raise
    
    async def is_duplicate(self, dedupe_key: str) -> bool:
        """
        Check if event is a duplicate based on dedupe_key
        
        Args:
            dedupe_key: Idempotency key
        
        Returns:
            True if duplicate, False otherwise
        """
        if not dedupe_key:
            return False
        
        await self.initialize()
        
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            # Clean up expired entries first
            cursor.execute("DELETE FROM genesis_dedupe WHERE expires_at < datetime('now')")
            
            # Check for existing key
            cursor.execute(
                "SELECT event_id FROM genesis_dedupe WHERE dedupe_key = ?",
                (dedupe_key,)
            )
            result = cursor.fetchone()
            
            conn.commit()
            conn.close()
            
            return result is not None
            
        except Exception as e:
            logger.error(f"❌ Failed to check duplicate: {e}")
            return False
    
    async def record_event(
        self,
        event_id: str,
        topic: str,
        source: str,
        kind: str,
        payload: Dict[str, Any],
        dedupe_key: Optional[str] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        schema: str = "genesis.event.v1",
        ts: Optional[datetime] = None
    ) -> bool:
        """
        Record event in persistent store
        
        Returns:
            True if recorded, False if duplicate or error
        """
        await self.initialize()
        
        # Check for duplicate
        if dedupe_key and await self.is_duplicate(dedupe_key):
            logger.debug(f"⏭️ Skipping duplicate event: {dedupe_key}")
            return False
        
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            # Get next watermark
            cursor.execute("SELECT COALESCE(MAX(watermark), 0) + 1 FROM genesis_events")
            watermark = cursor.fetchone()[0]
            
            # Store event
            cursor.execute(
                """
                INSERT INTO genesis_events 
                (id, ts, topic, source, kind, correlation_id, causation_id, schema, payload, watermark)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    (ts or datetime.utcnow()).isoformat(),
                    topic,
                    source,
                    kind,
                    correlation_id,
                    causation_id,
                    schema,
                    json.dumps(payload),
                    watermark
                )
            )
            
            # Record dedupe key if provided
            if dedupe_key:
                expires_at = datetime.utcnow() + timedelta(seconds=GENESIS_DEDUP_TTL_SECS)
                cursor.execute(
                    "INSERT OR REPLACE INTO genesis_dedupe (dedupe_key, event_id, expires_at) VALUES (?, ?, ?)",
                    (dedupe_key, event_id, expires_at.isoformat())
                )
            
            conn.commit()
            conn.close()
            
            logger.debug(f"📝 Recorded event {event_id} at watermark {watermark}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to record event: {e}")
            return False
    
    async def get_events(
        self,
        topic_pattern: Optional[str] = None,
        from_watermark: Optional[int] = None,
        to_watermark: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve events from store
        
        Args:
            topic_pattern: SQL LIKE pattern for topic filtering (e.g. "engine.truth%")
            from_watermark: Start watermark (inclusive)
            to_watermark: End watermark (inclusive)
            limit: Maximum events to return
        
        Returns:
            List of event dictionaries
        """
        await self.initialize()
        
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            query = "SELECT id, ts, topic, source, kind, payload, watermark FROM genesis_events WHERE 1=1"
            params = []
            
            if topic_pattern:
                query += " AND topic LIKE ?"
                params.append(topic_pattern)
            
            if from_watermark is not None:
                query += " AND watermark >= ?"
                params.append(from_watermark)
            
            if to_watermark is not None:
                query += " AND watermark <= ?"
                params.append(to_watermark)
            
            query += " ORDER BY watermark ASC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            conn.close()
            
            events = []
            for row in rows:
                events.append({
                    "id": row[0],
                    "ts": row[1],
                    "topic": row[2],
                    "source": row[3],
                    "kind": row[4],
                    "payload": json.loads(row[5]),
                    "watermark": row[6]
                })
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve events: {e}")
            return []
    
    async def add_to_dlq(self, event_id: str, topic: str, payload: Dict[str, Any], error: str):
        """Add failed event to Dead Letter Queue"""
        await self.initialize()
        
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO genesis_dlq (event_id, topic, payload, error)
                VALUES (?, ?, ?, ?)
                """,
                (event_id, topic, json.dumps(payload), str(error))
            )
            
            conn.commit()
            conn.close()
            
            logger.warning(f"⚠️ Added event {event_id} to DLQ: {error}")
            
        except Exception as e:
            logger.error(f"❌ Failed to add to DLQ: {e}")
    
    async def get_watermark(self) -> int:
        """Get current watermark (highest event sequence number)"""
        await self.initialize()
        
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COALESCE(MAX(watermark), 0) FROM genesis_events")
            watermark = cursor.fetchone()[0]
            
            conn.close()
            
            return watermark
            
        except Exception as e:
            logger.error(f"❌ Failed to get watermark: {e}")
            return 0


# Global persistence instance
genesis_persistence = GenesisPersistence()
