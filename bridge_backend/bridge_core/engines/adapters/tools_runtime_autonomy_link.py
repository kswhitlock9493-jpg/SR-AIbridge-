"""
Tools & Runtime Autonomy Links
Connects tools and runtime systems to Autonomy Engine via Genesis bus
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def register_tools_runtime_autonomy_links():
    """
    Register autonomy integration for tools and runtime systems.
    Links firewall intelligence, network diagnostics, health monitoring, etc.
    """
    from bridge_backend.genesis.bus import genesis_bus
    
    if not genesis_bus.is_enabled():
        logger.info("Genesis bus disabled, skipping tools/runtime autonomy links")
        return
    
    logger.info("🔗 Registering Tools & Runtime → Autonomy links...")
    
    # Firewall Intelligence autonomy link
    async def handle_firewall_event(event: Dict[str, Any]):
        """Handle firewall intelligence events"""
        # Firewall threats trigger autonomy healing
        if event.get("threat_level", 0) > 5:
            await genesis_bus.publish("genesis.heal", {
                "type": "autonomy.firewall_threat",
                "source": "autonomy",
                "firewall_event": event,
            })
        else:
            await genesis_bus.publish("genesis.intent", {
                "type": "autonomy.firewall_analysis",
                "source": "autonomy",
                "firewall_event": event,
            })
    
    # Network Diagnostics autonomy link
    async def handle_network_event(event: Dict[str, Any]):
        """Handle network diagnostics events"""
        # Network issues trigger autonomy healing
        if event.get("status") == "error" or event.get("latency", 0) > 1000:
            await genesis_bus.publish("genesis.heal", {
                "type": "autonomy.network_issue",
                "source": "autonomy",
                "network_event": event,
            })
        else:
            await genesis_bus.publish("genesis.fact", {
                "type": "autonomy.network_status",
                "source": "autonomy",
                "network_event": event,
            })
    
    # Health Monitoring autonomy link
    async def handle_health_event(event: Dict[str, Any]):
        """Handle health monitoring events"""
        # Health degradation triggers autonomy healing
        health_status = event.get("status", "unknown")
        if health_status in ["unhealthy", "degraded", "critical"]:
            await genesis_bus.publish("genesis.heal", {
                "type": "autonomy.health_degraded",
                "source": "autonomy",
                "health_event": event,
            })
        else:
            await genesis_bus.publish("genesis.fact", {
                "type": "autonomy.health_check",
                "source": "autonomy",
                "health_event": event,
            })
    
    # Runtime/Deploy autonomy link
    async def handle_runtime_event(event: Dict[str, Any]):
        """Handle runtime and deployment events"""
        event_type = event.get("type", "")
        
        # Deployment failures trigger autonomy healing
        if "fail" in event_type.lower() or "error" in event_type.lower():
            await genesis_bus.publish("genesis.heal", {
                "type": "autonomy.deploy_failure",
                "source": "autonomy",
                "runtime_event": event,
            })
        else:
            await genesis_bus.publish("genesis.intent", {
                "type": "autonomy.deploy_status",
                "source": "autonomy",
                "runtime_event": event,
            })
    
    # Metrics autonomy link
    async def handle_metrics_event(event: Dict[str, Any]):
        """Handle metrics events"""
        # Anomalous metrics trigger autonomy analysis
        if event.get("anomaly_detected", False):
            await genesis_bus.publish("genesis.heal", {
                "type": "autonomy.metrics_anomaly",
                "source": "autonomy",
                "metrics_event": event,
            })
        else:
            await genesis_bus.publish("genesis.fact", {
                "type": "autonomy.metrics_snapshot",
                "source": "autonomy",
                "metrics_event": event,
            })
    
    # Subscribe to tool and runtime topics
    genesis_bus.subscribe("firewall.threat", handle_firewall_event)
    genesis_bus.subscribe("firewall.analysis", handle_firewall_event)
    genesis_bus.subscribe("network.diagnostics", handle_network_event)
    genesis_bus.subscribe("network.status", handle_network_event)
    genesis_bus.subscribe("health.check", handle_health_event)
    genesis_bus.subscribe("health.status", handle_health_event)
    genesis_bus.subscribe("runtime.deploy", handle_runtime_event)
    genesis_bus.subscribe("runtime.status", handle_runtime_event)
    genesis_bus.subscribe("metrics.snapshot", handle_metrics_event)
    genesis_bus.subscribe("metrics.anomaly", handle_metrics_event)
    
    logger.info("✅ Tools & Runtime → Autonomy links registered")


async def publish_health_event(component: str, status: str, details: Dict[str, Any] = None):
    """
    Utility function to publish health events from any component.
    
    Args:
        component: Component name
        status: Health status (healthy, degraded, unhealthy, critical)
        details: Additional health details
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if genesis_bus.is_enabled():
            await genesis_bus.publish("health.status", {
                "component": component,
                "status": status,
                "details": details or {},
                "timestamp": _get_timestamp()
            })
    except Exception as e:
        logger.debug(f"Failed to publish health event: {e}")


async def publish_network_event(event_type: str, data: Dict[str, Any]):
    """
    Utility function to publish network diagnostics events.
    
    Args:
        event_type: Event type (diagnostics, status)
        data: Event data
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if genesis_bus.is_enabled():
            await genesis_bus.publish(f"network.{event_type}", {
                **data,
                "timestamp": _get_timestamp()
            })
    except Exception as e:
        logger.debug(f"Failed to publish network event: {e}")


async def publish_firewall_event(threat_level: int, analysis: Dict[str, Any]):
    """
    Utility function to publish firewall intelligence events.
    
    Args:
        threat_level: Threat level (0-10)
        analysis: Firewall analysis data
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if genesis_bus.is_enabled():
            event_type = "firewall.threat" if threat_level > 5 else "firewall.analysis"
            await genesis_bus.publish(event_type, {
                "threat_level": threat_level,
                "analysis": analysis,
                "timestamp": _get_timestamp()
            })
    except Exception as e:
        logger.debug(f"Failed to publish firewall event: {e}")


async def publish_runtime_event(event_type: str, data: Dict[str, Any]):
    """
    Utility function to publish runtime/deploy events.
    
    Args:
        event_type: Event type (deploy, status)
        data: Event data
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if genesis_bus.is_enabled():
            await genesis_bus.publish(f"runtime.{event_type}", {
                **data,
                "timestamp": _get_timestamp()
            })
    except Exception as e:
        logger.debug(f"Failed to publish runtime event: {e}")


def _get_timestamp() -> str:
    """Get ISO timestamp"""
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"
