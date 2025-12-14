"""
HypShard v3 - Quantum Adaptive Shard Manager
Manages dynamic sharding with adaptive capacity scaling
"""

import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, UTC
import asyncio
import os

logger = logging.getLogger(__name__)


class HypShardV3Manager:
    """
    HypShard v3 - Quantum Adaptive Shard Manager
    
    Manages up to 1,000,000 concurrent shards with:
    - Expand on load
    - Collapse post-execute
    - Auto-balance
    
    Control channels: HXO_CORE, FEDERATION_ENGINE, LEVIATHAN_ENGINE, CASCADE_ENGINE
    """
    
    def __init__(self):
        self.role = "quantum_adaptive_shard_manager"
        self.max_capacity = 1_000_000  # 1,000,000 concurrent shards
        self.active_shards: Dict[str, Dict[str, Any]] = {}
        self.shard_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Policies from specification
        self.policies = {
            "expand_on_load": True,
            "collapse_post_execute": True,
            "auto_balance": True
        }
        
        # Control channels
        self.control_channels = [
            "HXO_CORE",
            "FEDERATION_ENGINE",
            "LEVIATHAN_ENGINE",
            "CASCADE_ENGINE"
        ]
        
        # Configuration
        self._enabled = os.getenv("HYPSHARD_ENABLED", "true").lower() == "true"
        self._auto_balance_interval = int(os.getenv("HYPSHARD_BALANCE_INTERVAL", "60"))
        self._min_shard_threshold = int(os.getenv("HYPSHARD_MIN_THRESHOLD", "1000"))
        self._max_shard_threshold = int(os.getenv("HYPSHARD_MAX_THRESHOLD", "900000"))
        
        self._balance_task: Optional[asyncio.Task] = None
        
        logger.info(f"✅ HypShard v3 initialized - capacity: {self.max_capacity:,}")
    
    async def start(self):
        """Start the HypShard manager"""
        if not self._enabled:
            logger.warning("HypShard v3 is disabled")
            return
        
        # Start auto-balance task if enabled
        if self.policies["auto_balance"]:
            self._balance_task = asyncio.create_task(self._auto_balance_loop())
        
        logger.info("✅ HypShard v3 started")
    
    async def stop(self):
        """Stop the HypShard manager"""
        if self._balance_task and not self._balance_task.done():
            self._balance_task.cancel()
            try:
                await self._balance_task
            except asyncio.CancelledError:
                pass
        
        logger.info("HypShard v3 stopped")
    
    async def create_shard(self, shard_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new shard"""
        if len(self.active_shards) >= self.max_capacity:
            logger.warning(f"Shard capacity reached: {self.max_capacity:,}")
            return {"status": "error", "reason": "capacity_exceeded"}
        
        shard = {
            "id": shard_id,
            "config": config,
            "created_at": datetime.now(UTC).isoformat(),
            "status": "active",
            "load": 0,
            "executions": 0
        }
        
        self.active_shards[shard_id] = shard
        self.shard_metrics[shard_id] = {
            "created_at": shard["created_at"],
            "total_executions": 0,
            "avg_load": 0.0,
            "peak_load": 0
        }
        
        logger.info(f"Shard created: {shard_id} ({len(self.active_shards):,}/{self.max_capacity:,})")
        
        return {"status": "created", "shard": shard}
    
    async def expand_shard(self, shard_id: str, reason: str = "load") -> Dict[str, Any]:
        """Expand a shard (create additional capacity)"""
        if not self.policies["expand_on_load"]:
            return {"status": "disabled", "reason": "expand_on_load_disabled"}
        
        if shard_id not in self.active_shards:
            return {"status": "error", "reason": "shard_not_found"}
        
        # Create expansion shard
        expansion_id = f"{shard_id}_expansion_{len(self.active_shards)}"
        expansion_config = {
            **self.active_shards[shard_id]["config"],
            "parent_shard": shard_id,
            "expansion_reason": reason
        }
        
        result = await self.create_shard(expansion_id, expansion_config)
        
        if result["status"] == "created":
            logger.info(f"Shard expanded: {shard_id} → {expansion_id}")
        
        return result
    
    async def collapse_shard(self, shard_id: str) -> Dict[str, Any]:
        """Collapse a shard after execution"""
        if not self.policies["collapse_post_execute"]:
            return {"status": "disabled", "reason": "collapse_post_execute_disabled"}
        
        if shard_id not in self.active_shards:
            return {"status": "error", "reason": "shard_not_found"}
        
        shard = self.active_shards[shard_id]
        
        # Only collapse if executions are complete and load is low
        if shard["load"] > 0:
            return {"status": "deferred", "reason": "shard_still_active"}
        
        # Archive metrics before removal
        final_metrics = self.shard_metrics.get(shard_id, {})
        final_metrics["collapsed_at"] = datetime.now(UTC).isoformat()
        
        del self.active_shards[shard_id]
        if shard_id in self.shard_metrics:
            del self.shard_metrics[shard_id]
        
        logger.info(f"Shard collapsed: {shard_id} ({len(self.active_shards):,} remaining)")
        
        return {"status": "collapsed", "final_metrics": final_metrics}
    
    async def update_shard_load(self, shard_id: str, load: int):
        """Update the load for a shard"""
        if shard_id not in self.active_shards:
            return
        
        shard = self.active_shards[shard_id]
        old_load = shard["load"]
        shard["load"] = load
        
        # Update metrics
        metrics = self.shard_metrics.get(shard_id, {})
        metrics["peak_load"] = max(metrics.get("peak_load", 0), load)
        
        # Check if expansion is needed
        if self.policies["expand_on_load"] and load > old_load * 1.5:
            await self.expand_shard(shard_id, reason="high_load")
    
    async def execute_on_shard(self, shard_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task on a shard"""
        if shard_id not in self.active_shards:
            return {"status": "error", "reason": "shard_not_found"}
        
        shard = self.active_shards[shard_id]
        
        # Update shard state
        shard["executions"] += 1
        shard["load"] += 1
        
        # Update metrics
        metrics = self.shard_metrics.get(shard_id, {})
        metrics["total_executions"] = metrics.get("total_executions", 0) + 1
        
        try:
            # Simulate execution
            result = {
                "status": "executed",
                "shard_id": shard_id,
                "task_id": task.get("id"),
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            return result
            
        finally:
            # Reduce load after execution
            shard["load"] = max(0, shard["load"] - 1)
            
            # Check if shard should be collapsed
            if shard["load"] == 0 and shard["executions"] > 0:
                if self.policies["collapse_post_execute"]:
                    # Don't await to avoid blocking
                    asyncio.create_task(self.collapse_shard(shard_id))
    
    async def _auto_balance_loop(self):
        """Auto-balance shards periodically"""
        while True:
            try:
                await asyncio.sleep(self._auto_balance_interval)
                await self._balance_shards()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-balance error: {e}")
    
    async def _balance_shards(self):
        """Balance shard distribution"""
        if not self.policies["auto_balance"]:
            return
        
        total_shards = len(self.active_shards)
        
        if total_shards == 0:
            return
        
        # Calculate total load
        total_load = sum(s["load"] for s in self.active_shards.values())
        avg_load = total_load / total_shards if total_shards > 0 else 0
        
        # Find overloaded and underloaded shards
        overloaded = []
        underloaded = []
        
        for shard_id, shard in self.active_shards.items():
            if shard["load"] > avg_load * 1.5:
                overloaded.append(shard_id)
            elif shard["load"] < avg_load * 0.5 and shard["load"] > 0:
                underloaded.append(shard_id)
        
        # Expand overloaded shards
        for shard_id in overloaded[:10]:  # Limit to 10 per cycle
            await self.expand_shard(shard_id, reason="auto_balance")
        
        logger.debug(f"Auto-balance: {total_shards:,} shards, avg_load={avg_load:.2f}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get HypShard statistics"""
        total_shards = len(self.active_shards)
        total_load = sum(s["load"] for s in self.active_shards.values())
        total_executions = sum(s["executions"] for s in self.active_shards.values())
        
        return {
            "role": self.role,
            "capacity": self.max_capacity,
            "active_shards": total_shards,
            "utilization": (total_shards / self.max_capacity) * 100,
            "total_load": total_load,
            "total_executions": total_executions,
            "avg_load": total_load / total_shards if total_shards > 0 else 0,
            "policies": self.policies,
            "control_channels": self.control_channels,
            "timestamp": datetime.now(UTC).isoformat()
        }
