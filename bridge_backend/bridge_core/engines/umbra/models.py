"""
Umbra Lattice Memory Models
Graph-based memory structure for causal tracking
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Any, Union
from datetime import datetime, timezone


# Node and Edge type definitions
NodeKind = Literal[
    "engine",
    "change",
    "deploy",
    "heal",
    "drift",
    "var",
    "commit",
    "cert",
    "role"
]

EdgeKind = Literal[
    "caused_by",
    "fixes",
    "certified_by",
    "approved_by",
    "emitted",
    "touches",
    "supersedes"
]


class LatticeNode(BaseModel):
    """Lattice graph node representing an entity in the system"""
    id: str = Field(..., description="Unique node identifier")
    kind: NodeKind = Field(..., description="Node type")
    ts: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Node creation timestamp"
    )
    attrs: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional node attributes"
    )


class LatticeEdge(BaseModel):
    """Lattice graph edge representing a relationship between nodes"""
    src: str = Field(..., description="Source node ID")
    dst: str = Field(..., description="Destination node ID")
    kind: EdgeKind = Field(..., description="Edge type/relationship")
    ts: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Edge creation timestamp"
    )
    attrs: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional edge attributes"
    )


class LatticeSnapshot(BaseModel):
    """Complete snapshot of the Lattice graph"""
    nodes: List[LatticeNode] = Field(
        default_factory=list,
        description="All nodes in the graph"
    )
    edges: List[LatticeEdge] = Field(
        default_factory=list,
        description="All edges in the graph"
    )
    summary: Dict[str, Union[int, Dict[str, int]]] = Field(
        default_factory=dict,
        description="Summary statistics (supports both flat counts and nested dictionaries)"
    )
    ts: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Snapshot timestamp"
    )


class LatticeQuery(BaseModel):
    """Query parameters for Lattice operations"""
    since: Optional[str] = Field(
        None,
        description="Time window (e.g., '7d', '24h', '1w')"
    )
    node_kind: Optional[NodeKind] = Field(
        None,
        description="Filter by node type"
    )
    edge_kind: Optional[EdgeKind] = Field(
        None,
        description="Filter by edge type"
    )
    limit: int = Field(
        default=100,
        description="Maximum results to return"
    )
