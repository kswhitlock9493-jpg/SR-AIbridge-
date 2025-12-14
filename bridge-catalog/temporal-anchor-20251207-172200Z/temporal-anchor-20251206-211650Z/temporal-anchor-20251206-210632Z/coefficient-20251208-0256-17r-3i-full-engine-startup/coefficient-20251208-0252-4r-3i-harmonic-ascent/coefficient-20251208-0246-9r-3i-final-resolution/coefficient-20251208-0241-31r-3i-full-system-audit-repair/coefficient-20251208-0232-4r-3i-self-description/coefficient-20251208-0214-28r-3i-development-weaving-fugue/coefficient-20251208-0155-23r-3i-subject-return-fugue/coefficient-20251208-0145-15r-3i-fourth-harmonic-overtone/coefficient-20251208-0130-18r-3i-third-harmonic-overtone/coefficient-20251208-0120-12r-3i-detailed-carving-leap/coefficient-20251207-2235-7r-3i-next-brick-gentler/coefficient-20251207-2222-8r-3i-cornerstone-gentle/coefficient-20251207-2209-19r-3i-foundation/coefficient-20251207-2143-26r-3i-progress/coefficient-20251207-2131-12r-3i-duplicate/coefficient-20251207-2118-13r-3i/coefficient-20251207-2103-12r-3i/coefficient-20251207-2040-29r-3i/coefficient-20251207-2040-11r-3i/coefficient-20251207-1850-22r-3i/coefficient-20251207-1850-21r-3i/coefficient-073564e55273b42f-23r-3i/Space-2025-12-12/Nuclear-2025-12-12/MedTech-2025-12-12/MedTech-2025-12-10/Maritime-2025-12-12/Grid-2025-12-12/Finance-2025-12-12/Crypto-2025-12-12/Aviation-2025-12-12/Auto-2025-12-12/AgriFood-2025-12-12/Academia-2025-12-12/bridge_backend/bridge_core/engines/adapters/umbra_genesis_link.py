"""
Umbra Genesis Link Adapter
Subscribes Umbra Lattice and Triage Mesh to Genesis event topics
"""

import logging
from typing import Dict, Any
from datetime import datetime, UTC

logger = logging.getLogger(__name__)

# Global instances
umbra_triage_core = None


async def register_umbra_triage():
    """
    Register Umbra Triage Mesh with Genesis bus
    Handles triage signal topics and heal coordination
    """
    global umbra_triage_core
    
    try:
        from bridge_backend.genesis.bus import genesis_bus
        from bridge_backend.engines.umbra.core import UmbraTriageCore
        
        if not genesis_bus.is_enabled():
            logger.info("[Umbra Triage Genesis Link] Genesis bus disabled")
            return
        
        umbra_triage_core = UmbraTriageCore()
        
        if not umbra_triage_core.enabled:
            logger.info("[Umbra Triage Genesis Link] Umbra Triage disabled")
            return
        
        # Subscribe to triage signal topics
        await genesis_bus.subscribe("triage.signal.build", on_build_signal)
        await genesis_bus.subscribe("triage.signal.deploy", on_deploy_signal)
        await genesis_bus.subscribe("triage.signal.runtime", on_runtime_signal)
        await genesis_bus.subscribe("triage.signal.api", on_api_signal)
        await genesis_bus.subscribe("triage.signal.webhook", on_webhook_signal)
        
        # Subscribe to heal events
        await genesis_bus.subscribe("genesis.heal", on_heal_request)
        
        # Subscribe to deploy failure events
        await genesis_bus.subscribe("deploy.preview.failed", on_deploy_failed)
        await genesis_bus.subscribe("deploy.signals", on_deploy_event)
        
        logger.info("✅ Umbra Triage Mesh registered with Genesis")
        
    except Exception as e:
        logger.error(f"❌ Failed to register Umbra Triage: {e}")


async def on_build_signal(event: Dict[str, Any]):
    """Handle build signal"""
    if umbra_triage_core:
        await umbra_triage_core.ingest_signal({
            "kind": "build",
            "source": event.get("source", "unknown"),
            "message": event.get("message", "Build signal"),
            "severity": event.get("severity", "info"),
            "metadata": event.get("metadata", {})
        })


async def on_deploy_signal(event: Dict[str, Any]):
    """Handle deploy signal"""
    if umbra_triage_core:
        await umbra_triage_core.ingest_signal({
            "kind": "deploy",
            "source": event.get("source", "unknown"),
            "message": event.get("message", "Deploy signal"),
            "severity": event.get("severity", "info"),
            "metadata": event.get("metadata", {})
        })


async def on_runtime_signal(event: Dict[str, Any]):
    """Handle runtime signal"""
    if umbra_triage_core:
        await umbra_triage_core.ingest_signal({
            "kind": "runtime",
            "source": event.get("source", "unknown"),
            "message": event.get("message", "Runtime signal"),
            "severity": event.get("severity", "info"),
            "metadata": event.get("metadata", {})
        })


async def on_api_signal(event: Dict[str, Any]):
    """Handle API signal"""
    if umbra_triage_core:
        await umbra_triage_core.ingest_signal({
            "kind": "api",
            "source": event.get("source", "unknown"),
            "message": event.get("message", "API signal"),
            "severity": event.get("severity", "info"),
            "metadata": event.get("metadata", {})
        })


async def on_webhook_signal(event: Dict[str, Any]):
    """Handle webhook signal"""
    if umbra_triage_core:
        await umbra_triage_core.ingest_signal({
            "kind": "webhook",
            "source": event.get("source", "unknown"),
            "message": event.get("message", "Webhook signal"),
            "severity": event.get("severity", "info"),
            "metadata": event.get("metadata", {})
        })


async def on_heal_request(event: Dict[str, Any]):
    """Handle heal request"""
    if umbra_triage_core:
        await umbra_triage_core.ingest_signal({
            "kind": "runtime",
            "source": event.get("subsystem", "unknown"),
            "message": f"Heal request from {event.get('subsystem', 'unknown')}",
            "severity": "warning",
            "metadata": {"heal_request": True, "error": event.get("error", {})}
        })


async def on_deploy_failed(event: Dict[str, Any]):
    """Handle deploy failure"""
    if umbra_triage_core:
        await umbra_triage_core.ingest_signal({
            "kind": "deploy",
            "source": event.get("platform", "unknown"),
            "message": f"Deploy failed: {event.get('reason', 'unknown')}",
            "severity": "critical",
            "metadata": event
        })


async def on_deploy_event(event: Dict[str, Any]):
    """Handle general deploy events"""
    if umbra_triage_core:
        event_type = event.get("type", "")
        if "fail" in event_type.lower() or "error" in event_type.lower():
            await umbra_triage_core.ingest_signal({
                "kind": "deploy",
                "source": event.get("source", "unknown"),
                "message": f"Deploy event: {event_type}",
                "severity": "critical" if "fail" in event_type.lower() else "warning",
                "metadata": event
            })


async def subscribe_umbra_to_genesis():
    """
    Subscribe Umbra Lattice to relevant Genesis topics
    
    Topics monitored:
    - deploy.* (deploy events)
    - envrecon.* (environment reconciliation)
    - arie.* (autonomous repository integrity)
    - chimera.* (deployment engine)
    - netlify.* (Netlify events)
    - render.* (Render events)
    - github.* (GitHub events)
    - truth.* (truth certification)
    - cascade.* (cascade propagation)
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice
        
        if not genesis_bus.is_enabled():
            logger.debug("[Umbra Genesis Link] Genesis bus disabled")
            return
        
        lattice = UmbraLattice()
        await lattice.initialize()
        
        # Define event handler
        async def handle_event(event: Dict[str, Any]):
            """Handle incoming Genesis event"""
            try:
                await lattice.record_event(event)
                logger.debug(f"[Umbra Genesis Link] Recorded event: {event.get('type')}")
            except Exception as e:
                logger.error(f"[Umbra Genesis Link] Failed to record event: {e}")
        
        # Subscribe to topics
        topics = [
            # Deploy topics
            "deploy.initiated",
            "deploy.heal.intent",
            "deploy.heal.complete",
            "deploy.certified",
            "deploy.netlify",
            "deploy.render",
            "deploy.github",
            "deploy.platform.start",
            "deploy.platform.success",
            "deploy.platform.failure",
            
            # EnvRecon topics
            "envrecon.drift",
            "envrecon.audit",
            "envrecon.heal",
            "envrecon.sync",
            
            # ARIE topics
            "arie.audit",
            "arie.fix.intent",
            "arie.fix.applied",
            "arie.fix.rollback",
            "arie.alert",
            
            # Chimera topics
            "chimera.simulate.start",
            "chimera.simulate.complete",
            "chimera.deploy.start",
            "chimera.deploy.complete",
            "chimera.certify.start",
            "chimera.certify.complete",
            "chimera.rollback.triggered",
            
            # Netlify topics (from engines)
            "deploy.netlify.preview_failed",
            
            # Truth topics
            "genesis.fact",
            
            # Cascade topics
            "genesis.heal",
            
            # Autonomy topics
            "autonomy.heal.applied",
            "autonomy.heal.error",
        ]
        
        for topic in topics:
            genesis_bus.subscribe(topic, handle_event)
            logger.debug(f"[Umbra Genesis Link] Subscribed to {topic}")
        
        logger.info(f"✅ Umbra Lattice subscribed to {len(topics)} Genesis topics")
        
    except ImportError:
        logger.debug("[Umbra Genesis Link] Genesis bus not available")
    except Exception as e:
        logger.error(f"[Umbra Genesis Link] Failed to subscribe: {e}")


async def publish_lattice_event(event_type: str, data: Dict[str, Any]):
    """
    Publish Umbra Lattice event to Genesis
    
    Args:
        event_type: Type of lattice event
        data: Event data
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.debug("[Umbra Genesis Link] Genesis bus disabled")
            return
        
        await genesis_bus.publish(f"umbra.lattice.{event_type}", {
            **data,
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        logger.debug(f"[Umbra Genesis Link] Published: umbra.lattice.{event_type}")
        
    except ImportError:
        logger.debug("[Umbra Genesis Link] Genesis bus not available")
    except Exception as e:
        logger.error(f"[Umbra Genesis Link] Failed to publish: {e}")
