"""
HXO Schedulers
Scheduling strategies for shard execution
"""

from abc import ABC, abstractmethod
from typing import List
import logging

from .models import ShardSpec, SchedulerType

logger = logging.getLogger(__name__)


class Scheduler(ABC):
    """Base class for scheduling strategies"""
    
    @abstractmethod
    async def schedule(self, shards: List[ShardSpec]) -> List[ShardSpec]:
        """
        Schedule shards for execution.
        
        Args:
            shards: List of shards to schedule
            
        Returns:
            Ordered list of shards
        """
        pass


class FairRoundRobinScheduler(Scheduler):
    """Fair round-robin scheduling across executors"""
    
    async def schedule(self, shards: List[ShardSpec]) -> List[ShardSpec]:
        # Group by executor type
        by_executor = {}
        for shard in shards:
            executor_name = shard.executor.value
            if executor_name not in by_executor:
                by_executor[executor_name] = []
            by_executor[executor_name].append(shard)
        
        # Interleave shards from different executors
        scheduled = []
        while any(by_executor.values()):
            for executor_name in list(by_executor.keys()):
                if by_executor[executor_name]:
                    scheduled.append(by_executor[executor_name].pop(0))
                if not by_executor[executor_name]:
                    del by_executor[executor_name]
        
        logger.debug(f"[Scheduler] FairRoundRobin: scheduled {len(scheduled)} shards")
        return scheduled


class HotShardSplitterScheduler(Scheduler):
    """Split hot shards that exceed p95 latency"""
    
    async def schedule(self, shards: List[ShardSpec]) -> List[ShardSpec]:
        # In a real implementation, this would monitor shard execution times
        # and split shards that exceed thresholds
        # For now, just return shards as-is
        logger.debug(f"[Scheduler] HotShardSplitter: scheduled {len(shards)} shards")
        return shards


class BackpressureAwareScheduler(Scheduler):
    """Dampen fan-out based on queue depth and CPU"""
    
    async def schedule(self, shards: List[ShardSpec]) -> List[ShardSpec]:
        # In a real implementation, this would check system metrics
        # and throttle shard execution accordingly
        # For now, just return shards as-is
        logger.debug(f"[Scheduler] BackpressureAware: scheduled {len(shards)} shards")
        return shards


# Registry
_schedulers = {
    SchedulerType.FAIR_ROUND_ROBIN: FairRoundRobinScheduler(),
    SchedulerType.HOT_SHARD_SPLITTER: HotShardSplitterScheduler(),
    SchedulerType.BACKPRESSURE_AWARE: BackpressureAwareScheduler(),
}


def get_scheduler(scheduler_type: SchedulerType) -> Scheduler:
    """Get scheduler by type"""
    return _schedulers[scheduler_type]
