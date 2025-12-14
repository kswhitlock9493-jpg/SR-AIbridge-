"""
HXO Checkpointer
SQLite-backed persistence for plans, shards, and results
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .models import HXOPlan, ShardSpec, ShardResult, ShardPhase

logger = logging.getLogger(__name__)


class HXOCheckpointer:
    """
    Checkpoint store for HXO state persistence.
    Enables resumption across redeploys.
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                plan_id TEXT PRIMARY KEY,
                plan_data TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Shards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shards (
                cas_id TEXT PRIMARY KEY,
                stage_id TEXT NOT NULL,
                shard_data TEXT NOT NULL,
                phase TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                cas_id TEXT PRIMARY KEY,
                result_data TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shards_stage ON shards(stage_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shards_phase ON shards(phase)")
        
        conn.commit()
        conn.close()
        
        logger.info(f"[HXO Checkpointer] Initialized at {self.db_path}")
    
    async def save_plan(self, plan: HXOPlan):
        """Save plan to checkpoint store"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        plan_data = plan.model_dump_json()
        created_at = datetime.utcnow().isoformat()
        
        cursor.execute(
            "INSERT OR REPLACE INTO plans (plan_id, plan_data, created_at) VALUES (?, ?, ?)",
            (plan.plan_id, plan_data, created_at)
        )
        
        conn.commit()
        conn.close()
    
    async def get_plan(self, plan_id: str) -> Optional[HXOPlan]:
        """Retrieve plan from checkpoint store"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT plan_data FROM plans WHERE plan_id = ?", (plan_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return HXOPlan.model_validate_json(row[0])
        return None
    
    async def save_shard(self, shard: ShardSpec):
        """Save shard to checkpoint store"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        shard_data = shard.model_dump_json()
        updated_at = datetime.utcnow().isoformat()
        
        cursor.execute(
            """INSERT OR REPLACE INTO shards 
               (cas_id, stage_id, shard_data, phase, updated_at) 
               VALUES (?, ?, ?, ?, ?)""",
            (shard.cas_id, shard.stage_id, shard_data, shard.phase.value, updated_at)
        )
        
        conn.commit()
        conn.close()
    
    async def get_shard(self, cas_id: str) -> Optional[ShardSpec]:
        """Retrieve shard from checkpoint store"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT shard_data FROM shards WHERE cas_id = ?", (cas_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return ShardSpec.model_validate_json(row[0])
        return None
    
    async def save_result(self, result: ShardResult):
        """Save shard result to checkpoint store"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        result_data = result.model_dump_json()
        created_at = datetime.utcnow().isoformat()
        
        cursor.execute(
            "INSERT OR REPLACE INTO results (cas_id, result_data, created_at) VALUES (?, ?, ?)",
            (result.cas_id, result_data, created_at)
        )
        
        conn.commit()
        conn.close()
    
    async def get_result(self, cas_id: str) -> Optional[ShardResult]:
        """Retrieve result from checkpoint store"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT result_data FROM results WHERE cas_id = ?", (cas_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return ShardResult.model_validate_json(row[0])
        return None
    
    async def get_shards_by_stage(self, stage_id: str) -> list[ShardSpec]:
        """Get all shards for a stage"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT shard_data FROM shards WHERE stage_id = ?", (stage_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [ShardSpec.model_validate_json(row[0]) for row in rows]
    
    async def compact(self):
        """Compact database (garbage collection)"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("VACUUM")
        conn.commit()
        conn.close()
        
        logger.info("[HXO Checkpointer] Compacted database")
