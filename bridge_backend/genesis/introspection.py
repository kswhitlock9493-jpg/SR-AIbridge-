"""
Genesis Introspection System
Live telemetry and self-mapping for the Genesis organism
"""

from typing import Dict, Any, List, Optional
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class GenesisIntrospection:
    """
    Genesis introspection and telemetry system.
    Provides real-time visibility into the state and health of the entire organism.
    """
    
    def __init__(self):
        self._metrics: Dict[str, Any] = {}
        self._health_checks: Dict[str, bool] = {}
        self._heartbeat_interval = int(os.getenv("GENESIS_HEARTBEAT_INTERVAL", "15"))
        self._last_heartbeat: Optional[str] = None
        
        logger.info("🔍 Genesis Introspection initialized")
    
    def record_metric(self, name: str, value: Any, metadata: Optional[Dict[str, Any]] = None):
        """
        Record a metric for introspection
        
        Args:
            name: Metric name
            value: Metric value
            metadata: Optional metadata about the metric
        """
        self._metrics[name] = {
            "value": value,
            "timestamp": self._get_timestamp(),
            "metadata": metadata or {},
        }
    
    def get_metric(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific metric"""
        return self._metrics.get(name)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all recorded metrics"""
        return self._metrics.copy()
    
    def update_health(self, component: str, healthy: bool):
        """
        Update health status for a component
        
        Args:
            component: Component name
            healthy: Health status (True = healthy, False = unhealthy)
        """
        self._health_checks[component] = healthy
        logger.debug(f"Health update: {component} = {'✅' if healthy else '❌'}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        total = len(self._health_checks)
        healthy = sum(1 for h in self._health_checks.values() if h)
        
        return {
            "overall_healthy": healthy == total if total > 0 else True,
            "components": self._health_checks.copy(),
            "healthy_count": healthy,
            "total_count": total,
            "health_percentage": (healthy / total * 100) if total > 0 else 100.0,
        }
    
    def heartbeat(self):
        """Record a heartbeat pulse"""
        self._last_heartbeat = self._get_timestamp()
        self.record_metric("last_heartbeat", self._last_heartbeat)
    
    def get_heartbeat_status(self) -> Dict[str, Any]:
        """Get heartbeat status"""
        return {
            "last_heartbeat": self._last_heartbeat,
            "interval_seconds": self._heartbeat_interval,
        }
    
    def generate_echo_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive echo report for genesis.echo topic
        
        Returns:
            Complete introspection report
        """
        return {
            "type": "genesis.echo.report",
            "timestamp": self._get_timestamp(),
            "health": self.get_health_status(),
            "heartbeat": self.get_heartbeat_status(),
            "metrics": self.get_all_metrics(),
        }
    
    def get_system_map(self) -> Dict[str, Any]:
        """
        Generate a system map showing all components and their relationships
        
        Returns:
            System topology map
        """
        try:
            from .manifest import genesis_manifest
            
            manifest = genesis_manifest.get_manifest()
            engines = manifest.get("engines", {})
            
            # Build dependency graph
            graph = {}
            for engine_name in engines.keys():
                deps = genesis_manifest.get_dependencies(engine_name)
                topics = genesis_manifest.get_topics(engine_name)
                role = genesis_manifest.get_engine_role(engine_name)
                
                graph[engine_name] = {
                    "dependencies": deps,
                    "topics": topics,
                    "role": role,
                    "health": self._health_checks.get(engine_name, None),
                }
            
            return {
                "total_engines": len(engines),
                "graph": graph,
                "timestamp": self._get_timestamp(),
            }
            
        except Exception as e:
            logger.error(f"Failed to generate system map: {e}")
            return {"error": str(e)}
    
    def _get_timestamp(self) -> str:
        """Get ISO timestamp"""
        return datetime.utcnow().isoformat() + "Z"


# Global singleton introspection instance
genesis_introspection = GenesisIntrospection()
