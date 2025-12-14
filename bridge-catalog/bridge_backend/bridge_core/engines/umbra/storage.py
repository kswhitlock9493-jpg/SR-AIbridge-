"""
Umbra Lattice Storage
SQLite-based persistence for graph memory
"""

import sqlite3
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import asyncio

from .models import LatticeNode, LatticeEdge, LatticeSnapshot

logger = logging.getLogger(__name__)

# Storage location
UMBRA_DIR = Path("/home/runner/work/SR-AIbridge-/SR-AIbridge-/.umbra")
LATTICE_DB = UMBRA_DIR / "lattice.db"
SNAPSHOTS_DIR = UMBRA_DIR / "snapshots"


class LatticeStorage:
    """
    SQLite-based storage for Umbra Lattice graph
    
    Features:
    - Node/edge persistence
    - Time-based queries
    - Snapshot management
    - Truth certification tracking
    """
    
    def __init__(self):
        self._db_path = LATTICE_DB
        self._lock = asyncio.Lock()
        self._initialized = False
        
        # Ensure directories exist
        UMBRA_DIR.mkdir(parents=True, exist_ok=True)
        SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize database schema"""
        if self._initialized:
            return
        
        async with self._lock:
            try:
                conn = sqlite3.connect(str(self._db_path))
                cursor = conn.cursor()
                
                # Nodes table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS lattice_nodes (
                        id TEXT PRIMARY KEY,
                        kind TEXT NOT NULL,
                        ts TIMESTAMP NOT NULL,
                        attrs TEXT,
                        certified INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Edges table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS lattice_edges (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        src TEXT NOT NULL,
                        dst TEXT NOT NULL,
                        kind TEXT NOT NULL,
                        ts TIMESTAMP NOT NULL,
                        attrs TEXT,
                        certified INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (src) REFERENCES lattice_nodes(id),
                        FOREIGN KEY (dst) REFERENCES lattice_nodes(id)
                    )
                """)
                
                # Pending certification queue
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS lattice_pending (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        entity_type TEXT NOT NULL,
                        entity_id TEXT NOT NULL,
                        data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Snapshots metadata
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS lattice_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts TIMESTAMP NOT NULL,
                        node_count INTEGER,
                        edge_count INTEGER,
                        certified_count INTEGER,
                        file_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Indices for performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_kind ON lattice_nodes(kind)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_ts ON lattice_nodes(ts)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_kind ON lattice_edges(kind)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_ts ON lattice_edges(ts)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_src ON lattice_edges(src)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_dst ON lattice_edges(dst)")
                
                conn.commit()
                conn.close()
                
                self._initialized = True
                logger.info(f"✅ Umbra Lattice storage initialized: {self._db_path}")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize Umbra Lattice storage: {e}")
                raise
    
    async def add_node(self, node: LatticeNode, certified: bool = False) -> bool:
        """
        Add or update a node in the lattice
        
        Args:
            node: Node to add
            certified: Whether node is truth-certified
            
        Returns:
            Success status
        """
        await self.initialize()
        
        async with self._lock:
            try:
                conn = sqlite3.connect(str(self._db_path))
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO lattice_nodes 
                    (id, kind, ts, attrs, certified)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    node.id,
                    node.kind,
                    node.ts.isoformat(),
                    json.dumps(node.attrs),
                    1 if certified else 0
                ))
                
                conn.commit()
                conn.close()
                
                logger.debug(f"🌑 Added node: {node.id} ({node.kind})")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to add node: {e}")
                return False
    
    async def add_edge(self, edge: LatticeEdge, certified: bool = False) -> bool:
        """
        Add an edge to the lattice
        
        Args:
            edge: Edge to add
            certified: Whether edge is truth-certified
            
        Returns:
            Success status
        """
        await self.initialize()
        
        async with self._lock:
            try:
                conn = sqlite3.connect(str(self._db_path))
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO lattice_edges 
                    (src, dst, kind, ts, attrs, certified)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    edge.src,
                    edge.dst,
                    edge.kind,
                    edge.ts.isoformat(),
                    json.dumps(edge.attrs),
                    1 if certified else 0
                ))
                
                conn.commit()
                conn.close()
                
                logger.debug(f"🌑 Added edge: {edge.src} --[{edge.kind}]--> {edge.dst}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to add edge: {e}")
                return False
    
    async def get_nodes(
        self,
        kind: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[LatticeNode]:
        """
        Query nodes from the lattice
        
        Args:
            kind: Filter by node kind
            since: Filter by timestamp
            limit: Maximum results
            
        Returns:
            List of nodes
        """
        await self.initialize()
        
        async with self._lock:
            try:
                conn = sqlite3.connect(str(self._db_path))
                cursor = conn.cursor()
                
                query = "SELECT id, kind, ts, attrs FROM lattice_nodes WHERE 1=1"
                params = []
                
                if kind:
                    query += " AND kind = ?"
                    params.append(kind)
                
                if since:
                    query += " AND ts >= ?"
                    params.append(since.isoformat())
                
                query += " ORDER BY ts DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                conn.close()
                
                nodes = []
                for row in rows:
                    nodes.append(LatticeNode(
                        id=row[0],
                        kind=row[1],
                        ts=datetime.fromisoformat(row[2]),
                        attrs=json.loads(row[3]) if row[3] else {}
                    ))
                
                return nodes
                
            except Exception as e:
                logger.error(f"❌ Failed to query nodes: {e}")
                return []
    
    async def get_edges(
        self,
        kind: Optional[str] = None,
        since: Optional[datetime] = None,
        src: Optional[str] = None,
        dst: Optional[str] = None,
        limit: int = 100
    ) -> List[LatticeEdge]:
        """
        Query edges from the lattice
        
        Args:
            kind: Filter by edge kind
            since: Filter by timestamp
            src: Filter by source node
            dst: Filter by destination node
            limit: Maximum results
            
        Returns:
            List of edges
        """
        await self.initialize()
        
        async with self._lock:
            try:
                conn = sqlite3.connect(str(self._db_path))
                cursor = conn.cursor()
                
                query = "SELECT src, dst, kind, ts, attrs FROM lattice_edges WHERE 1=1"
                params = []
                
                if kind:
                    query += " AND kind = ?"
                    params.append(kind)
                
                if since:
                    query += " AND ts >= ?"
                    params.append(since.isoformat())
                
                if src:
                    query += " AND src = ?"
                    params.append(src)
                
                if dst:
                    query += " AND dst = ?"
                    params.append(dst)
                
                query += " ORDER BY ts DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                conn.close()
                
                edges = []
                for row in rows:
                    edges.append(LatticeEdge(
                        src=row[0],
                        dst=row[1],
                        kind=row[2],
                        ts=datetime.fromisoformat(row[3]),
                        attrs=json.loads(row[4]) if row[4] else {}
                    ))
                
                return edges
                
            except Exception as e:
                logger.error(f"❌ Failed to query edges: {e}")
                return []
    
    async def create_snapshot(self, since: Optional[datetime] = None) -> LatticeSnapshot:
        """
        Create a snapshot of the lattice
        
        Args:
            since: Optional time filter
            
        Returns:
            Lattice snapshot
        """
        nodes = await self.get_nodes(since=since, limit=10000)
        edges = await self.get_edges(since=since, limit=10000)
        
        # Calculate summary
        summary = {
            "nodes": len(nodes),
            "edges": len(edges),
            "node_kinds": {},
            "edge_kinds": {}
        }
        
        for node in nodes:
            summary["node_kinds"][node.kind] = summary["node_kinds"].get(node.kind, 0) + 1
        
        for edge in edges:
            summary["edge_kinds"][edge.kind] = summary["edge_kinds"].get(edge.kind, 0) + 1
        
        snapshot = LatticeSnapshot(
            nodes=nodes,
            edges=edges,
            summary=summary
        )
        
        # Save snapshot to file
        await self._save_snapshot_file(snapshot)
        
        # Record metadata
        await self._record_snapshot_metadata(snapshot)
        
        return snapshot
    
    async def _save_snapshot_file(self, snapshot: LatticeSnapshot):
        """Save snapshot to JSON file"""
        try:
            ts_str = snapshot.ts.strftime("%Y%m%d_%H%M%S")
            file_path = SNAPSHOTS_DIR / f"snapshot_{ts_str}.json"
            
            with open(file_path, 'w') as f:
                json.dump(snapshot.model_dump(mode='json'), f, indent=2, default=str)
            
            logger.info(f"💾 Saved snapshot to {file_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save snapshot file: {e}")
    
    async def _record_snapshot_metadata(self, snapshot: LatticeSnapshot):
        """Record snapshot metadata in database"""
        async with self._lock:
            try:
                conn = sqlite3.connect(str(self._db_path))
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO lattice_snapshots 
                    (ts, node_count, edge_count, certified_count, file_path)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    snapshot.ts.isoformat(),
                    snapshot.summary.get("nodes", 0),
                    snapshot.summary.get("edges", 0),
                    0,  # TODO: track certified count
                    f"snapshot_{snapshot.ts.strftime('%Y%m%d_%H%M%S')}.json"
                ))
                
                conn.commit()
                conn.close()
                
            except Exception as e:
                logger.error(f"❌ Failed to record snapshot metadata: {e}")
    
    async def add_to_pending(self, entity_type: str, entity_id: str, data: Dict[str, Any]):
        """Add entity to pending certification queue"""
        await self.initialize()
        
        async with self._lock:
            try:
                conn = sqlite3.connect(str(self._db_path))
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO lattice_pending (entity_type, entity_id, data)
                    VALUES (?, ?, ?)
                """, (entity_type, entity_id, json.dumps(data)))
                
                conn.commit()
                conn.close()
                
                logger.debug(f"📝 Added to pending: {entity_type} {entity_id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to add to pending: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        await self.initialize()
        
        async with self._lock:
            try:
                conn = sqlite3.connect(str(self._db_path))
                cursor = conn.cursor()
                
                # Count nodes
                cursor.execute("SELECT COUNT(*), COUNT(*) FILTER (WHERE certified = 1) FROM lattice_nodes")
                node_count, certified_nodes = cursor.fetchone()
                
                # Count edges
                cursor.execute("SELECT COUNT(*), COUNT(*) FILTER (WHERE certified = 1) FROM lattice_edges")
                edge_count, certified_edges = cursor.fetchone()
                
                # Count pending
                cursor.execute("SELECT COUNT(*) FROM lattice_pending")
                pending_count = cursor.fetchone()[0]
                
                # Count snapshots
                cursor.execute("SELECT COUNT(*) FROM lattice_snapshots")
                snapshot_count = cursor.fetchone()[0]
                
                conn.close()
                
                return {
                    "nodes": node_count,
                    "edges": edge_count,
                    "certified_nodes": certified_nodes,
                    "certified_edges": certified_edges,
                    "pending": pending_count,
                    "snapshots": snapshot_count,
                    "db_path": str(self._db_path)
                }
                
            except Exception as e:
                logger.error(f"❌ Failed to get stats: {e}")
                return {}
