"""
HXO Data Models
Content-addressed shards, plans, and execution metadata
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime, UTC
from pydantic import BaseModel, Field
from enum import Enum
import hashlib
import json


class ShardPhase(str, Enum):
    """Shard execution phases"""
    PENDING = "pending"
    CLAIMED = "claimed"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    RETRYING = "retrying"


class PartitionerType(str, Enum):
    """Available partitioner strategies"""
    BY_FILESIZE = "by_filesize"
    BY_MODULE = "by_module"
    BY_DAG_DEPTH = "by_dag_depth"
    BY_ROUTE_MAP = "by_route_map"
    BY_ASSET_BUCKET = "by_asset_bucket"
    BY_SQL_BATCH = "by_sql_batch"


class ExecutorType(str, Enum):
    """Available executor types"""
    PACK_BACKEND = "pack_backend"
    WARM_REGISTRY = "warm_registry"
    INDEX_ASSETS = "index_assets"
    PRIME_CACHES = "prime_caches"
    DOCS_INDEX = "docs_index"
    SQL_MIGRATE = "sql_migrate"


class SchedulerType(str, Enum):
    """Available scheduler types"""
    FAIR_ROUND_ROBIN = "fair_round_robin"
    HOT_SHARD_SPLITTER = "hot_shard_splitter"
    BACKPRESSURE_AWARE = "backpressure_aware"


class HXOStage(BaseModel):
    """A stage in an HXO plan"""
    id: str
    kind: str  # e.g., "deploy.pack", "deploy.migrate"
    slo_ms: int = 120000
    partitioner: PartitionerType = PartitionerType.BY_FILESIZE
    executor: ExecutorType = ExecutorType.PACK_BACKEND
    scheduler: SchedulerType = SchedulerType.FAIR_ROUND_ROBIN
    dependencies: List[str] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)


class HXOPlan(BaseModel):
    """HXO execution plan with stages and constraints"""
    plan_id: str
    name: str
    stages: List[HXOStage]
    constraints: Dict[str, Any] = Field(default_factory=dict)
    submitted_at: Optional[datetime] = None
    submitted_by: str = "system"
    
    def get_max_shards(self) -> int:
        """Get max shards constraint"""
        return self.constraints.get("max_shards", 1000000)
    
    def get_timebox_ms(self) -> int:
        """Get overall timebox constraint"""
        return self.constraints.get("timebox_ms", 600000)  # 10 min default


class ShardSpec(BaseModel):
    """Content-addressed shard specification"""
    cas_id: str  # hash(task_spec + inputs + deps)
    stage_id: str
    executor: ExecutorType
    inputs: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    attempt: int = 0
    phase: ShardPhase = ShardPhase.PENDING
    
    @staticmethod
    def compute_cas_id(stage_id: str, executor: str, inputs: Dict[str, Any], deps: List[str]) -> str:
        """Compute content-addressed shard ID"""
        # Create deterministic hash from inputs
        data = {
            "stage_id": stage_id,
            "executor": executor,
            "inputs": inputs,
            "dependencies": sorted(deps)
        }
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class ShardResult(BaseModel):
    """Result of shard execution"""
    cas_id: str
    success: bool
    output_digest: str  # hash of output
    started_at: datetime
    finished_at: datetime
    attempt: int
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MerkleNode(BaseModel):
    """Node in Merkle tree for result aggregation"""
    node_id: str
    left: Optional[str] = None  # child node IDs
    right: Optional[str] = None
    hash_value: str
    is_leaf: bool = True
    
    @staticmethod
    def leaf_hash(shard_result: ShardResult) -> str:
        """Compute leaf hash for a shard result"""
        data = f"{shard_result.cas_id}|{shard_result.output_digest}|{shard_result.attempt}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def branch_hash(left_hash: str, right_hash: str) -> str:
        """Compute branch hash from children"""
        data = f"{left_hash}|{right_hash}"
        return hashlib.sha256(data.encode()).hexdigest()


class MerkleProof(BaseModel):
    """Merkle proof for verification"""
    leaf_cas_id: str
    leaf_hash: str
    path: List[Dict[str, str]]  # [{"side": "left"|"right", "hash": "..."}]
    root_hash: str


class PlanStatus(BaseModel):
    """Status of an HXO plan execution"""
    plan_id: str
    plan_name: str
    total_shards: int
    pending_shards: int
    claimed_shards: int
    running_shards: int
    done_shards: int
    failed_shards: int
    merkle_root: Optional[str] = None
    truth_certified: bool = False
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    eta_seconds: Optional[float] = None


class AutotuneSignal(BaseModel):
    """Signal for autonomy-driven auto-tuning"""
    plan_id: str
    stage_id: str
    signal_type: Literal["high_latency", "hotspot", "timeout_risk", "queue_depth"]
    metric_value: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    suggested_action: Optional[str] = None
