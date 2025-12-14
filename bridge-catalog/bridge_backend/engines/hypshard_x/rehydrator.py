"""
HXO Rehydrator
Resume incomplete plans after redeploys
"""

import logging
from typing import List, Optional
from pathlib import Path

from .models import HXOPlan, ShardSpec, ShardPhase
from .checkpointer import HXOCheckpointer

logger = logging.getLogger(__name__)


class HXORehydrator:
    """
    Rehydrates incomplete plans from checkpoints.
    Enables resumable execution across redeploys.
    """
    
    def __init__(self, checkpointer: HXOCheckpointer):
        self.checkpointer = checkpointer
    
    async def find_incomplete_plans(self) -> List[str]:
        """
        Find plans that have incomplete shards.
        
        Returns:
            List of plan IDs
        """
        # In a real implementation, this would query the database
        # For now, return empty list
        return []
    
    async def rehydrate_plan(self, plan_id: str) -> Optional[HXOPlan]:
        """
        Rehydrate a plan from checkpoints.
        
        Args:
            plan_id: Plan ID to rehydrate
            
        Returns:
            Rehydrated plan or None if not found
        """
        plan = await self.checkpointer.get_plan(plan_id)
        if not plan:
            logger.warning(f"[Rehydrator] Plan {plan_id} not found in checkpoints")
            return None
        
        logger.info(f"[Rehydrator] Rehydrated plan {plan_id}")
        return plan
    
    async def get_incomplete_shards(self, plan: HXOPlan) -> List[ShardSpec]:
        """
        Get incomplete shards for a plan.
        
        Args:
            plan: Plan to check
            
        Returns:
            List of incomplete shards
        """
        incomplete = []
        
        for stage in plan.stages:
            shards = await self.checkpointer.get_shards_by_stage(stage.id)
            
            for shard in shards:
                if shard.phase in [ShardPhase.PENDING, ShardPhase.CLAIMED, ShardPhase.RUNNING]:
                    incomplete.append(shard)
        
        logger.info(f"[Rehydrator] Found {len(incomplete)} incomplete shards for plan {plan.plan_id}")
        return incomplete
    
    async def resume_plan(self, plan_id: str) -> bool:
        """
        Resume execution of an incomplete plan.
        
        Args:
            plan_id: Plan ID to resume
            
        Returns:
            True if plan was resumed
        """
        plan = await self.rehydrate_plan(plan_id)
        if not plan:
            return False
        
        incomplete = await self.get_incomplete_shards(plan)
        
        if not incomplete:
            logger.info(f"[Rehydrator] No incomplete shards for plan {plan_id}")
            return False
        
        # Reset incomplete shards to pending
        for shard in incomplete:
            shard.phase = ShardPhase.PENDING
            await self.checkpointer.save_shard(shard)
        
        logger.info(f"[Rehydrator] Resumed plan {plan_id} with {len(incomplete)} shards")
        return True
