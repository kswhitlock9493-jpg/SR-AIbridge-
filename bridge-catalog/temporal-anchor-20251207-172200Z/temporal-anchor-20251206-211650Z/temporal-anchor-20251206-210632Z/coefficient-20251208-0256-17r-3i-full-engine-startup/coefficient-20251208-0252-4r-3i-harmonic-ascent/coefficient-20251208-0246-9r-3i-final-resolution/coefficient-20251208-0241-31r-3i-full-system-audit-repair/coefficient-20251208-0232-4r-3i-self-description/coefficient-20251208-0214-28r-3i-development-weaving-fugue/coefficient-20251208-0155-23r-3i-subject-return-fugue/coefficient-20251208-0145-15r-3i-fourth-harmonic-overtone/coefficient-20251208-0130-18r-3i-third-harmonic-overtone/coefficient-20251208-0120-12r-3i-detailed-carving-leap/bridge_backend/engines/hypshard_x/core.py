"""
HXO Core Orchestration Engine
Manages plan execution, shard lifecycle, and coordination
"""

from __future__ import annotations
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, UTC
from pathlib import Path

from .models import (
    HXOPlan, ShardSpec, ShardResult, ShardPhase, PlanStatus,
    AutotuneSignal, MerkleNode, MerkleProof
)
from .checkpointer import HXOCheckpointer
from .merkle import MerkleTree
from .schedulers import get_scheduler
from .executors import get_executor
from .partitioners import get_partitioner

logger = logging.getLogger(__name__)


class HXOCore:
    """
    Hypshard-X Orchestrator Core Engine
    
    Capabilities:
    - Adaptive sharding (1 -> 1M+ shards)
    - Content-addressed shard deduplication
    - Merkle aggregation for integrity
    - Idempotent execution with exactly-once semantics
    - Resumable across redeploys via checkpoints
    - Backpressure and rate control
    - Self-healing with Autonomy integration
    """
    
    def __init__(self, vault_dir: Path = None):
        self.vault = vault_dir or Path("bridge_backend/.hxo")
        self.vault.mkdir(parents=True, exist_ok=True)
        
        self.checkpointer = HXOCheckpointer(self.vault / "checkpoints.db")
        self.merkle_trees: Dict[str, MerkleTree] = {}
        
        # Runtime state
        self.active_plans: Dict[str, HXOPlan] = {}
        self.shard_registry: Dict[str, ShardSpec] = {}
        self.shard_results: Dict[str, ShardResult] = {}
        self.plan_status: Dict[str, PlanStatus] = {}
        
        # Concurrency control
        self.max_concurrency = int(os.getenv("HXO_MAX_CONCURRENCY", "64"))
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        
        logger.info(f"[HXO] Core initialized (vault={self.vault}, max_concurrency={self.max_concurrency})")
    
    async def submit_plan(self, plan: HXOPlan) -> str:
        """
        Submit a plan for execution.
        
        Returns:
            plan_id
        """
        plan.submitted_at = datetime.now(UTC)
        
        # Store plan
        self.active_plans[plan.plan_id] = plan
        await self.checkpointer.save_plan(plan)
        
        # Initialize Merkle tree
        self.merkle_trees[plan.plan_id] = MerkleTree(plan.plan_id)
        
        # Create shards for all stages
        await self._create_shards(plan)
        
        # Initialize status
        self.plan_status[plan.plan_id] = await self._compute_status(plan.plan_id)
        
        # Publish to Genesis
        try:
            await self._publish_genesis_event("hxo.plan", {
                "plan_id": plan.plan_id,
                "plan_name": plan.name,
                "stages": len(plan.stages),
                "submitted_by": plan.submitted_by
            })
        except Exception as e:
            logger.warning(f"[HXO] Genesis publish failed: {e}")
        
        # Start execution in background
        asyncio.create_task(self._execute_plan(plan.plan_id))
        
        logger.info(f"[HXO] Plan submitted: {plan.plan_id} ({plan.name})")
        return plan.plan_id
    
    async def _create_shards(self, plan: HXOPlan):
        """Create shards for all stages in a plan"""
        for stage in plan.stages:
            # Get partitioner for this stage
            partitioner = get_partitioner(stage.partitioner)
            
            # Partition the work
            partitions = await partitioner.partition(stage)
            
            # Create shard specs
            for partition_data in partitions:
                cas_id = ShardSpec.compute_cas_id(
                    stage.id,
                    stage.executor.value,
                    partition_data,
                    stage.dependencies
                )
                
                shard = ShardSpec(
                    cas_id=cas_id,
                    stage_id=stage.id,
                    executor=stage.executor,
                    inputs=partition_data,
                    dependencies=stage.dependencies,
                    phase=ShardPhase.PENDING
                )
                
                # Check if shard already exists (deduplication)
                existing = await self.checkpointer.get_shard(cas_id)
                if existing and existing.phase == ShardPhase.DONE:
                    logger.debug(f"[HXO] Shard {cas_id} already completed, reusing")
                    shard.phase = ShardPhase.DONE
                
                self.shard_registry[cas_id] = shard
                await self.checkpointer.save_shard(shard)
                
                # Publish shard created event
                try:
                    await self._publish_genesis_event("hxo.shard.created", {
                        "plan_id": plan.plan_id,
                        "stage_id": stage.id,
                        "cas_id": cas_id,
                        "phase": shard.phase.value
                    })
                except Exception:
                    pass
    
    async def _execute_plan(self, plan_id: str):
        """Execute all shards in a plan"""
        plan = self.active_plans.get(plan_id)
        if not plan:
            logger.error(f"[HXO] Plan {plan_id} not found")
            return
        
        # Update status
        status = self.plan_status[plan_id]
        status.started_at = datetime.now(UTC)
        
        # Execute stages in dependency order
        for stage in plan.stages:
            await self._execute_stage(plan_id, stage.id)
        
        # Finalize
        await self._finalize_plan(plan_id)
    
    async def _execute_stage(self, plan_id: str, stage_id: str):
        """Execute all shards in a stage"""
        # Get all shards for this stage
        stage_shards = [
            s for s in self.shard_registry.values()
            if s.stage_id == stage_id
        ]
        
        # Get scheduler
        plan = self.active_plans[plan_id]
        stage = next(s for s in plan.stages if s.id == stage_id)
        scheduler = get_scheduler(stage.scheduler)
        
        # Schedule and execute shards
        tasks = []
        for shard in stage_shards:
            if shard.phase == ShardPhase.DONE:
                continue  # Skip already completed shards
            
            task = asyncio.create_task(self._execute_shard(plan_id, shard))
            tasks.append(task)
        
        # Wait for all shards to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_shard(self, plan_id: str, shard: ShardSpec):
        """Execute a single shard"""
        async with self.semaphore:
            # Claim shard
            shard.phase = ShardPhase.CLAIMED
            await self.checkpointer.save_shard(shard)
            
            try:
                await self._publish_genesis_event("hxo.shard.claimed", {
                    "plan_id": plan_id,
                    "cas_id": shard.cas_id,
                    "stage_id": shard.stage_id
                })
            except Exception:
                pass
            
            # Execute
            shard.phase = ShardPhase.RUNNING
            await self.checkpointer.save_shard(shard)
            
            started_at = datetime.now(UTC)
            
            try:
                # Get executor
                executor = get_executor(shard.executor)
                
                # Execute (idempotent)
                output = await executor.execute(shard.inputs)
                
                # Compute output digest
                import json
                import hashlib
                output_digest = hashlib.sha256(
                    json.dumps(output, sort_keys=True).encode()
                ).hexdigest()
                
                # Create result
                result = ShardResult(
                    cas_id=shard.cas_id,
                    success=True,
                    output_digest=output_digest,
                    started_at=started_at,
                    finished_at=datetime.now(UTC),
                    attempt=shard.attempt,
                    metadata=output
                )
                
                # Save result
                self.shard_results[shard.cas_id] = result
                await self.checkpointer.save_result(result)
                
                # Update shard status
                shard.phase = ShardPhase.DONE
                await self.checkpointer.save_shard(shard)
                
                # Add to Merkle tree
                merkle_tree = self.merkle_trees.get(plan_id)
                if merkle_tree:
                    merkle_tree.add_leaf(result)
                
                # Publish success
                try:
                    await self._publish_genesis_event("hxo.shard.done", {
                        "plan_id": plan_id,
                        "cas_id": shard.cas_id,
                        "stage_id": shard.stage_id,
                        "output_digest": output_digest
                    })
                except Exception:
                    pass
                
                logger.debug(f"[HXO] Shard {shard.cas_id} completed successfully")
                
            except Exception as e:
                logger.error(f"[HXO] Shard {shard.cas_id} failed: {e}")
                
                # Create failure result
                result = ShardResult(
                    cas_id=shard.cas_id,
                    success=False,
                    output_digest="",
                    started_at=started_at,
                    finished_at=datetime.now(UTC),
                    attempt=shard.attempt,
                    error=str(e)
                )
                
                self.shard_results[shard.cas_id] = result
                await self.checkpointer.save_result(result)
                
                shard.phase = ShardPhase.FAILED
                await self.checkpointer.save_shard(shard)
                
                # Publish failure
                try:
                    await self._publish_genesis_event("hxo.shard.failed", {
                        "plan_id": plan_id,
                        "cas_id": shard.cas_id,
                        "stage_id": shard.stage_id,
                        "error": str(e)
                    })
                except Exception:
                    pass
    
    async def _finalize_plan(self, plan_id: str):
        """Finalize plan execution"""
        # Compute final Merkle root
        merkle_tree = self.merkle_trees.get(plan_id)
        if merkle_tree:
            root_hash = merkle_tree.compute_root()
            
            # Update status
            status = self.plan_status[plan_id]
            status.merkle_root = root_hash
            status.finished_at = datetime.now(UTC)
            
            # Publish for Truth certification
            try:
                await self._publish_genesis_event("hxo.aggregate.certify", {
                    "plan_id": plan_id,
                    "merkle_root": root_hash,
                    "total_shards": status.total_shards
                })
            except Exception as e:
                logger.warning(f"[HXO] Failed to publish for certification: {e}")
            
            logger.info(f"[HXO] Plan {plan_id} finalized (root={root_hash})")
    
    async def _compute_status(self, plan_id: str) -> PlanStatus:
        """Compute current status of a plan"""
        plan = self.active_plans.get(plan_id)
        if not plan:
            return PlanStatus(
                plan_id=plan_id,
                plan_name="unknown",
                total_shards=0,
                pending_shards=0,
                claimed_shards=0,
                running_shards=0,
                done_shards=0,
                failed_shards=0
            )
        
        # Count shards by phase
        plan_shards = [s for s in self.shard_registry.values() if any(
            stage.id == s.stage_id for stage in plan.stages
        )]
        
        phase_counts = {
            ShardPhase.PENDING: 0,
            ShardPhase.CLAIMED: 0,
            ShardPhase.RUNNING: 0,
            ShardPhase.DONE: 0,
            ShardPhase.FAILED: 0
        }
        
        for shard in plan_shards:
            phase_counts[shard.phase] += 1
        
        return PlanStatus(
            plan_id=plan_id,
            plan_name=plan.name,
            total_shards=len(plan_shards),
            pending_shards=phase_counts[ShardPhase.PENDING],
            claimed_shards=phase_counts[ShardPhase.CLAIMED],
            running_shards=phase_counts[ShardPhase.RUNNING],
            done_shards=phase_counts[ShardPhase.DONE],
            failed_shards=phase_counts[ShardPhase.FAILED]
        )
    
    async def get_status(self, plan_id: str) -> Optional[PlanStatus]:
        """Get current status of a plan"""
        if plan_id in self.plan_status:
            # Recompute for latest data
            self.plan_status[plan_id] = await self._compute_status(plan_id)
        return self.plan_status.get(plan_id)
    
    async def abort_plan(self, plan_id: str) -> bool:
        """Abort a running plan"""
        if plan_id not in self.active_plans:
            return False
        
        # Mark all pending/running shards as failed
        plan = self.active_plans[plan_id]
        for stage in plan.stages:
            stage_shards = [
                s for s in self.shard_registry.values()
                if s.stage_id == stage.id
            ]
            for shard in stage_shards:
                if shard.phase in [ShardPhase.PENDING, ShardPhase.CLAIMED, ShardPhase.RUNNING]:
                    shard.phase = ShardPhase.FAILED
                    await self.checkpointer.save_shard(shard)
        
        logger.info(f"[HXO] Plan {plan_id} aborted")
        return True
    
    async def _publish_genesis_event(self, topic: str, event: Dict[str, Any]):
        """Publish event to Genesis bus"""
        try:
            from bridge_backend.genesis.bus import genesis_bus
            if genesis_bus.is_enabled():
                await genesis_bus.publish(topic, event)
        except ImportError:
            logger.debug("[HXO] Genesis bus not available")


# Global singleton
import os
_hxo_core: Optional[HXOCore] = None


def get_hxo_core() -> HXOCore:
    """Get or create global HXO core instance"""
    global _hxo_core
    if _hxo_core is None:
        _hxo_core = HXOCore()
    return _hxo_core
