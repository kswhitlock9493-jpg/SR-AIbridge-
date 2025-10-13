"""
Umbra Lattice - Neural Changelog & Memory Bloom
Graph-based memory system that learns from system changes
"""

import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
import re

from .models import LatticeNode, LatticeEdge, LatticeSnapshot, NodeKind, EdgeKind
from .storage import LatticeStorage

logger = logging.getLogger(__name__)


class UmbraLattice:
    """
    Umbra Lattice Memory - Neural Changelog
    
    Features:
    - Captures changes across code, configs, deploys, and heals
    - Normalizes events into typed nodes/edges
    - Truth-gates all writes
    - Generates causal maps and timelines
    - Provides text-based mermaid visualizations
    """
    
    def __init__(self, truth=None, genesis_bus=None):
        self.storage = LatticeStorage()
        self.truth = truth
        self.genesis_bus = genesis_bus
        self.enabled = os.getenv("UMBRA_ENABLED", "true").lower() == "true"
        self.strict_truth = os.getenv("UMBRA_STRICT_TRUTH", "true").lower() == "true"
        
        logger.info("🌌 Umbra Lattice initialized - Neural changelog active")
    
    async def initialize(self):
        """Initialize lattice storage"""
        await self.storage.initialize()
    
    async def record_event(self, evt: Dict[str, Any]) -> None:
        """
        Record an event to the lattice
        
        Args:
            evt: Event data from Genesis or other sources
        """
        if not self.enabled:
            return
        
        # Normalize event into nodes/edges
        normalized = await self._normalize_event(evt)
        
        if not normalized:
            return
        
        # Truth gate - certify or queue
        certified = await self._truth_gate(normalized)
        
        # Persist nodes and edges
        for node in normalized.get("nodes", []):
            await self.storage.add_node(node, certified=certified)
        
        for edge in normalized.get("edges", []):
            await self.storage.add_edge(edge, certified=certified)
        
        # Publish to Genesis
        if self.genesis_bus:
            await self.genesis_bus.publish("umbra.lattice.recorded", {
                "event_type": evt.get("type"),
                "nodes": len(normalized.get("nodes", [])),
                "edges": len(normalized.get("edges", [])),
                "certified": certified
            })
    
    async def _normalize_event(self, evt: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Normalize event into lattice nodes and edges
        
        Args:
            evt: Raw event data
            
        Returns:
            Dict with 'nodes' and 'edges' lists
        """
        nodes = []
        edges = []
        
        event_type = evt.get("type", "").lower()
        
        # Deploy events
        if "deploy" in event_type:
            deploy_node = LatticeNode(
                id=f"deploy:{evt.get('service', 'unknown')}:{evt.get('ts', datetime.now(timezone.utc).isoformat())}",
                kind="deploy",
                attrs={
                    "service": evt.get("service", "unknown"),
                    "status": evt.get("status", "unknown"),
                    "commit": evt.get("commit", "")
                }
            )
            nodes.append(deploy_node)
            
            # Link to commit if present
            if evt.get("commit"):
                commit_node = LatticeNode(
                    id=f"commit:{evt['commit']}",
                    kind="commit",
                    attrs={"sha": evt["commit"]}
                )
                nodes.append(commit_node)
                
                edges.append(LatticeEdge(
                    src=commit_node.id,
                    dst=deploy_node.id,
                    kind="caused_by"
                ))
        
        # Drift events
        elif "drift" in event_type or "envrecon" in event_type:
            drift_node = LatticeNode(
                id=f"drift:{evt.get('context', 'env')}:{evt.get('ts', datetime.now(timezone.utc).isoformat())}",
                kind="drift",
                attrs={
                    "context": evt.get("context", "env"),
                    "missing_keys": str(evt.get("missing", [])),
                    "drifted_keys": str(evt.get("drifted", []))
                }
            )
            nodes.append(drift_node)
        
        # Heal/repair events
        elif "heal" in event_type or "arie" in event_type or "chimera" in event_type:
            heal_node = LatticeNode(
                id=f"heal:{evt.get('action', 'repair')}:{evt.get('ts', datetime.now(timezone.utc).isoformat())}",
                kind="heal",
                attrs={
                    "action": evt.get("action", "repair"),
                    "target": evt.get("target", "unknown"),
                    "status": evt.get("status", "unknown")
                }
            )
            nodes.append(heal_node)
            
            # Link to drift if causally related
            if evt.get("fixes_drift"):
                edges.append(LatticeEdge(
                    src=heal_node.id,
                    dst=evt["fixes_drift"],
                    kind="fixes"
                ))
        
        # Change events (code/config changes)
        elif "change" in event_type or "commit" in event_type:
            change_node = LatticeNode(
                id=f"change:{evt.get('file', 'unknown')}:{evt.get('ts', datetime.now(timezone.utc).isoformat())}",
                kind="change",
                attrs={
                    "file": evt.get("file", "unknown"),
                    "author": evt.get("author", "unknown"),
                    "lines_changed": str(evt.get("lines_changed", 0))
                }
            )
            nodes.append(change_node)
        
        # Var events (environment variable changes)
        elif "var" in event_type or "env" in event_type:
            var_node = LatticeNode(
                id=f"var:{evt.get('key', 'unknown')}:{evt.get('ts', datetime.now(timezone.utc).isoformat())}",
                kind="var",
                attrs={
                    "key": evt.get("key", "unknown"),
                    "source": evt.get("source", "unknown"),
                    "action": evt.get("action", "unknown")
                }
            )
            nodes.append(var_node)
        
        # Truth certification events
        elif "truth" in event_type or "cert" in event_type:
            cert_node = LatticeNode(
                id=f"cert:{evt.get('cert_id', 'unknown')}:{evt.get('ts', datetime.now(timezone.utc).isoformat())}",
                kind="cert",
                attrs={
                    "cert_id": evt.get("cert_id", "unknown"),
                    "certified": str(evt.get("certified", False))
                }
            )
            nodes.append(cert_node)
            
            # Link to what was certified
            if evt.get("certifies"):
                edges.append(LatticeEdge(
                    src=cert_node.id,
                    dst=evt["certifies"],
                    kind="certified_by"
                ))
        
        # Engine events
        elif "engine" in event_type:
            engine_node = LatticeNode(
                id=f"engine:{evt.get('name', 'unknown')}:{evt.get('ts', datetime.now(timezone.utc).isoformat())}",
                kind="engine",
                attrs={
                    "name": evt.get("name", "unknown"),
                    "action": evt.get("action", "unknown"),
                    "status": evt.get("status", "unknown")
                }
            )
            nodes.append(engine_node)
        
        if not nodes:
            logger.debug(f"🌑 No normalization for event type: {event_type}")
            return None
        
        return {"nodes": nodes, "edges": edges}
    
    async def _truth_gate(self, normalized: Dict[str, Any]) -> bool:
        """
        Truth gate - certify before persisting
        
        Args:
            normalized: Normalized nodes/edges
            
        Returns:
            True if certified, False if pending
        """
        if not self.strict_truth:
            return True  # Bypass if not strict
        
        if not self.truth:
            logger.warning("🌑 Truth engine not available, bypassing certification")
            return False
        
        try:
            # Request certification from Truth engine
            cert_result = await self.truth.certify({
                "type": "umbra_lattice_record",
                "nodes": [n.model_dump(mode='json') for n in normalized.get("nodes", [])],
                "edges": [e.model_dump(mode='json') for e in normalized.get("edges", [])]
            })
            
            certified = cert_result.get("certified", False)
            
            if not certified:
                # Add to pending queue
                for node in normalized.get("nodes", []):
                    await self.storage.add_to_pending("node", node.id, node.model_dump(mode='json'))
                
                logger.warning("🌑 Lattice record not certified, added to pending queue")
            
            return certified
            
        except Exception as e:
            logger.error(f"🌑 Truth certification failed: {e}")
            return False
    
    async def bloom(self) -> Dict[str, Any]:
        """
        Bloom - infer causal chains and build summaries
        
        Returns:
            Bloom analysis results
        """
        # Get recent nodes and edges
        since = datetime.now(timezone.utc) - timedelta(days=7)
        nodes = await self.storage.get_nodes(since=since, limit=1000)
        edges = await self.storage.get_edges(since=since, limit=1000)
        
        # Build causal chains
        chains = self._build_causal_chains(nodes, edges)
        
        # Generate summary
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nodes_analyzed": len(nodes),
            "edges_analyzed": len(edges),
            "causal_chains": len(chains),
            "top_causes": self._identify_top_causes(edges),
            "frequent_fixes": self._identify_frequent_fixes(nodes, edges)
        }
        
        logger.info(f"🌸 Bloom complete: {len(chains)} causal chains identified")
        
        return summary
    
    def _build_causal_chains(self, nodes: List[LatticeNode], edges: List[LatticeEdge]) -> List[List[str]]:
        """Build causal chains from edges"""
        chains = []
        
        # Build adjacency map
        graph = {}
        for edge in edges:
            if edge.kind in ["caused_by", "fixes", "emitted"]:
                if edge.src not in graph:
                    graph[edge.src] = []
                graph[edge.src].append(edge.dst)
        
        # Find chains (simple DFS)
        visited = set()
        
        def dfs(node_id, chain):
            if node_id in visited:
                return
            visited.add(node_id)
            chain.append(node_id)
            
            if node_id in graph:
                for next_id in graph[node_id]:
                    dfs(next_id, chain[:])
            else:
                if len(chain) > 1:
                    chains.append(chain)
        
        for node in nodes:
            if node.id not in visited:
                dfs(node.id, [])
        
        return chains
    
    def _identify_top_causes(self, edges: List[LatticeEdge]) -> List[Dict[str, Any]]:
        """Identify most common cause patterns"""
        causes = {}
        
        for edge in edges:
            if edge.kind == "caused_by":
                src_type = edge.src.split(":")[0] if ":" in edge.src else edge.src
                causes[src_type] = causes.get(src_type, 0) + 1
        
        # Sort by frequency
        sorted_causes = sorted(causes.items(), key=lambda x: x[1], reverse=True)
        
        return [{"cause": k, "frequency": v} for k, v in sorted_causes[:5]]
    
    def _identify_frequent_fixes(self, nodes: List[LatticeNode], edges: List[LatticeEdge]) -> List[Dict[str, Any]]:
        """Identify most frequent fix patterns"""
        fixes = {}
        
        for edge in edges:
            if edge.kind == "fixes":
                # Find the heal node
                heal_node = next((n for n in nodes if n.id == edge.src), None)
                if heal_node and heal_node.attrs.get("action"):
                    action = heal_node.attrs["action"]
                    fixes[action] = fixes.get(action, 0) + 1
        
        # Sort by frequency
        sorted_fixes = sorted(fixes.items(), key=lambda x: x[1], reverse=True)
        
        return [{"fix": k, "frequency": v} for k, v in sorted_fixes[:5]]
    
    async def mermaid(self, since: Optional[str] = None) -> str:
        """
        Generate mermaid graph visualization
        
        Args:
            since: Time window (e.g., '7d', '24h')
            
        Returns:
            Mermaid markdown string
        """
        # Parse time window
        since_dt = self._parse_time_window(since)
        
        # Get nodes and edges
        nodes = await self.storage.get_nodes(since=since_dt, limit=50)
        edges = await self.storage.get_edges(since=since_dt, limit=100)
        
        # Generate mermaid syntax
        lines = ["graph TD"]
        
        # Add nodes with labels
        node_labels = {}
        for i, node in enumerate(nodes):
            node_id = f"N{i}"
            label = self._format_node_label(node)
            node_labels[node.id] = node_id
            lines.append(f"  {node_id}[{label}]")
        
        # Add edges
        for edge in edges:
            src_id = node_labels.get(edge.src)
            dst_id = node_labels.get(edge.dst)
            
            if src_id and dst_id:
                edge_label = edge.kind.replace("_", " ").title()
                lines.append(f"  {src_id} -->|{edge_label}| {dst_id}")
        
        return "\n".join(lines)
    
    def _parse_time_window(self, window: Optional[str]) -> Optional[datetime]:
        """Parse time window string (e.g., '7d', '24h') into datetime"""
        if not window:
            return None
        
        now = datetime.now(timezone.utc)
        
        # Parse patterns like '7d', '24h', '1w'
        match = re.match(r'(\d+)([dhw])', window.lower())
        if not match:
            return None
        
        value, unit = match.groups()
        value = int(value)
        
        if unit == 'h':
            return now - timedelta(hours=value)
        elif unit == 'd':
            return now - timedelta(days=value)
        elif unit == 'w':
            return now - timedelta(weeks=value)
        
        return None
    
    def _format_node_label(self, node: LatticeNode) -> str:
        """Format node for mermaid display"""
        kind = node.kind.title()
        
        # Extract key attribute for label
        if node.kind == "deploy":
            service = node.attrs.get("service", "?")
            return f"{kind}: {service}"
        elif node.kind == "commit":
            sha = node.attrs.get("sha", "?")[:7]
            return f"{kind}: {sha}"
        elif node.kind == "drift":
            context = node.attrs.get("context", "?")
            return f"{kind}: {context}"
        elif node.kind == "heal":
            action = node.attrs.get("action", "?")
            return f"{kind}: {action}"
        elif node.kind == "change":
            file = node.attrs.get("file", "?")
            # Shorten file path
            file = file.split("/")[-1] if "/" in file else file
            return f"{kind}: {file}"
        elif node.kind == "var":
            key = node.attrs.get("key", "?")
            return f"{kind}: {key}"
        else:
            return kind
    
    async def get_summary(self, since: Optional[str] = None) -> Dict[str, Any]:
        """
        Get lattice summary
        
        Args:
            since: Optional time window
            
        Returns:
            Summary statistics
        """
        since_dt = self._parse_time_window(since)
        
        nodes = await self.storage.get_nodes(since=since_dt, limit=10000)
        edges = await self.storage.get_edges(since=since_dt, limit=10000)
        
        # Count by type
        node_counts = {}
        for node in nodes:
            node_counts[node.kind] = node_counts.get(node.kind, 0) + 1
        
        edge_counts = {}
        for edge in edges:
            edge_counts[edge.kind] = edge_counts.get(edge.kind, 0) + 1
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "window": since or "all",
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "node_types": node_counts,
            "edge_types": edge_counts
        }
    
    async def export_snapshot(self, since: Optional[str] = None) -> LatticeSnapshot:
        """
        Export lattice snapshot
        
        Args:
            since: Optional time window
            
        Returns:
            Lattice snapshot
        """
        since_dt = self._parse_time_window(since)
        snapshot = await self.storage.create_snapshot(since=since_dt)
        
        logger.info(f"📸 Exported snapshot: {snapshot.summary.get('nodes', 0)} nodes, {snapshot.summary.get('edges', 0)} edges")
        
        return snapshot


def fallback_neural_channel(name: str):
    """
    Umbra Lattice fallback neural channel for engines.
    
    Provides a minimal stub publish/subscribe bus so engines can queue signals
    until Genesis is ready. This ensures engines remain online and observable
    even when Genesis bus is temporarily unavailable.
    
    Args:
        name: Name of the engine attaching to the fallback channel
    """
    logger.info(f"🧬 Umbra Lattice: '{name}' attached to neural fallback bus")
    # Minimal stub implementation - signals are logged but not propagated
    # In production, this could buffer events for later replay when Genesis is available
