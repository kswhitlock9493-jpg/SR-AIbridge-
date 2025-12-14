"""
HXO Partitioners
Strategies for splitting work into shards
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

from .models import HXOStage, PartitionerType

logger = logging.getLogger(__name__)


class Partitioner(ABC):
    """Base class for partitioning strategies"""
    
    @abstractmethod
    async def partition(self, stage: HXOStage) -> List[Dict[str, Any]]:
        """
        Partition work into shard inputs.
        
        Args:
            stage: Stage configuration
            
        Returns:
            List of input dictionaries, one per shard
        """
        pass


class ByFilesizePartitioner(Partitioner):
    """Partition by file size (e.g., for asset processing)"""
    
    async def partition(self, stage: HXOStage) -> List[Dict[str, Any]]:
        # Mock implementation - in reality would scan files
        chunk_size_mb = stage.config.get("chunk_size_mb", 10)
        total_files = stage.config.get("total_files", 100)
        
        # Simple partitioning: one shard per file group
        num_shards = max(1, total_files // 10)
        
        partitions = []
        for i in range(num_shards):
            partitions.append({
                "partition_id": i,
                "file_range_start": i * 10,
                "file_range_end": min((i + 1) * 10, total_files),
                "chunk_size_mb": chunk_size_mb
            })
        
        logger.debug(f"[Partitioner] ByFilesize: {len(partitions)} shards")
        return partitions


class ByModulePartitioner(Partitioner):
    """Partition by module/package structure"""
    
    async def partition(self, stage: HXOStage) -> List[Dict[str, Any]]:
        modules = stage.config.get("modules", ["module_a", "module_b", "module_c"])
        
        partitions = []
        for module in modules:
            partitions.append({
                "module": module,
                "stage_kind": stage.kind
            })
        
        logger.debug(f"[Partitioner] ByModule: {len(partitions)} shards")
        return partitions


class ByDagDepthPartitioner(Partitioner):
    """Partition by DAG depth (for dependency-aware work)"""
    
    async def partition(self, stage: HXOStage) -> List[Dict[str, Any]]:
        max_depth = stage.config.get("max_depth", 5)
        
        partitions = []
        for depth in range(max_depth):
            partitions.append({
                "depth": depth,
                "dependencies": stage.dependencies
            })
        
        logger.debug(f"[Partitioner] ByDagDepth: {len(partitions)} shards")
        return partitions


class ByRouteMapPartitioner(Partitioner):
    """Partition by route/endpoint mapping"""
    
    async def partition(self, stage: HXOStage) -> List[Dict[str, Any]]:
        routes = stage.config.get("routes", ["/api/a", "/api/b", "/api/c"])
        
        partitions = []
        for route in routes:
            partitions.append({
                "route": route,
                "stage_kind": stage.kind
            })
        
        logger.debug(f"[Partitioner] ByRouteMap: {len(partitions)} shards")
        return partitions


class ByAssetBucketPartitioner(Partitioner):
    """Partition by asset bucket/category"""
    
    async def partition(self, stage: HXOStage) -> List[Dict[str, Any]]:
        buckets = stage.config.get("buckets", ["images", "scripts", "styles", "fonts"])
        
        partitions = []
        for bucket in buckets:
            partitions.append({
                "bucket": bucket,
                "stage_kind": stage.kind
            })
        
        logger.debug(f"[Partitioner] ByAssetBucket: {len(partitions)} shards")
        return partitions


class BySqlBatchPartitioner(Partitioner):
    """Partition SQL operations into batches"""
    
    async def partition(self, stage: HXOStage) -> List[Dict[str, Any]]:
        batch_size = stage.config.get("batch_size", 1000)
        total_rows = stage.config.get("total_rows", 10000)
        
        num_batches = (total_rows + batch_size - 1) // batch_size
        
        partitions = []
        for i in range(num_batches):
            partitions.append({
                "batch_id": i,
                "offset": i * batch_size,
                "limit": batch_size,
                "stage_kind": stage.kind
            })
        
        logger.debug(f"[Partitioner] BySqlBatch: {len(partitions)} shards")
        return partitions


# Registry
_partitioners: Dict[PartitionerType, Partitioner] = {
    PartitionerType.BY_FILESIZE: ByFilesizePartitioner(),
    PartitionerType.BY_MODULE: ByModulePartitioner(),
    PartitionerType.BY_DAG_DEPTH: ByDagDepthPartitioner(),
    PartitionerType.BY_ROUTE_MAP: ByRouteMapPartitioner(),
    PartitionerType.BY_ASSET_BUCKET: ByAssetBucketPartitioner(),
    PartitionerType.BY_SQL_BATCH: BySqlBatchPartitioner(),
}


def get_partitioner(partitioner_type: PartitionerType) -> Partitioner:
    """Get partitioner by type"""
    return _partitioners[partitioner_type]
