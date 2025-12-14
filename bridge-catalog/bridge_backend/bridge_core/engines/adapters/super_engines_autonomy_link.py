"""
Super Engines Autonomy Link
Connects the Six Super Engines to Autonomy Engine via Genesis bus
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def register_super_engines_autonomy_links():
    """
    Register autonomy integration for all Six Super Engines.
    Each engine can publish analysis results that autonomy can monitor.
    """
    from bridge_backend.genesis.bus import genesis_bus
    
    if not genesis_bus.is_enabled():
        logger.info("Genesis bus disabled, skipping super engines autonomy links")
        return
    
    logger.info("🔗 Registering Super Engines → Autonomy links...")
    
    # ScrollTongue (Language Processing) autonomy link
    async def handle_scrolltongue_event(event: Dict[str, Any]):
        """Handle language processing events for autonomy monitoring"""
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.scrolltongue_analysis",
            "source": "autonomy",
            "scrolltongue_event": event,
        })
    
    # CommerceForge (Commerce/Trading) autonomy link  
    async def handle_commerceforge_event(event: Dict[str, Any]):
        """Handle commerce/trading events for autonomy monitoring"""
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.commerceforge_trade",
            "source": "autonomy",
            "commerceforge_event": event,
        })
    
    # AuroraForge (Visual/Creative) autonomy link
    async def handle_auroraforge_event(event: Dict[str, Any]):
        """Handle visual/creative events for autonomy monitoring"""
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.auroraforge_creation",
            "source": "autonomy",
            "auroraforge_event": event,
        })
    
    # ChronicleLoom (Temporal/Historical) autonomy link
    async def handle_chronicleloom_event(event: Dict[str, Any]):
        """Handle temporal/historical events for autonomy monitoring"""
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.chronicleloom_timeline",
            "source": "autonomy",
            "chronicleloom_event": event,
        })
    
    # CalculusCore (Mathematical) autonomy link
    async def handle_calculuscore_event(event: Dict[str, Any]):
        """Handle mathematical computation events for autonomy monitoring"""
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.calculuscore_computation",
            "source": "autonomy",
            "calculuscore_event": event,
        })
    
    # QHelmSingularity (Quantum/Advanced) autonomy link
    async def handle_qhelmsingularity_event(event: Dict[str, Any]):
        """Handle quantum/advanced compute events for autonomy monitoring"""
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.qhelmsingularity_compute",
            "source": "autonomy",
            "qhelmsingularity_event": event,
        })
    
    # Subscribe to super engine topics
    genesis_bus.subscribe("scrolltongue.analysis", handle_scrolltongue_event)
    genesis_bus.subscribe("scrolltongue.translation", handle_scrolltongue_event)
    genesis_bus.subscribe("scrolltongue.pattern", handle_scrolltongue_event)
    
    genesis_bus.subscribe("commerceforge.trade", handle_commerceforge_event)
    genesis_bus.subscribe("commerceforge.market", handle_commerceforge_event)
    genesis_bus.subscribe("commerceforge.portfolio", handle_commerceforge_event)
    
    genesis_bus.subscribe("auroraforge.visual", handle_auroraforge_event)
    genesis_bus.subscribe("auroraforge.creative", handle_auroraforge_event)
    genesis_bus.subscribe("auroraforge.render", handle_auroraforge_event)
    
    genesis_bus.subscribe("chronicleloom.chronicle", handle_chronicleloom_event)
    genesis_bus.subscribe("chronicleloom.timeline", handle_chronicleloom_event)
    genesis_bus.subscribe("chronicleloom.event", handle_chronicleloom_event)
    
    genesis_bus.subscribe("calculuscore.computation", handle_calculuscore_event)
    genesis_bus.subscribe("calculuscore.optimization", handle_calculuscore_event)
    genesis_bus.subscribe("calculuscore.analysis", handle_calculuscore_event)
    
    genesis_bus.subscribe("qhelmsingularity.quantum", handle_qhelmsingularity_event)
    genesis_bus.subscribe("qhelmsingularity.advanced", handle_qhelmsingularity_event)
    genesis_bus.subscribe("qhelmsingularity.simulation", handle_qhelmsingularity_event)
    
    logger.info("✅ Super Engines → Autonomy links registered")


async def validate_super_engines_autonomy_integration() -> Dict[str, Any]:
    """
    Validate that all super engines can communicate with autonomy.
    
    Returns:
        Validation results
    """
    from bridge_backend.genesis.bus import genesis_bus
    
    if not genesis_bus.is_enabled():
        return {
            "success": False,
            "error": "Genesis bus disabled"
        }
    
    # Check that all required topics are registered
    required_topics = [
        "scrolltongue.analysis", "scrolltongue.translation", "scrolltongue.pattern",
        "commerceforge.trade", "commerceforge.market", "commerceforge.portfolio",
        "auroraforge.visual", "auroraforge.creative", "auroraforge.render",
        "chronicleloom.chronicle", "chronicleloom.timeline", "chronicleloom.event",
        "calculuscore.computation", "calculuscore.optimization", "calculuscore.analysis",
        "qhelmsingularity.quantum", "qhelmsingularity.advanced", "qhelmsingularity.simulation"
    ]
    
    registered_topics = []
    missing_topics = []
    
    for topic in required_topics:
        if topic in genesis_bus._valid_topics:
            registered_topics.append(topic)
        else:
            missing_topics.append(topic)
    
    return {
        "success": len(missing_topics) == 0,
        "total_topics": len(required_topics),
        "registered": len(registered_topics),
        "missing": len(missing_topics),
        "registered_topics": registered_topics,
        "missing_topics": missing_topics
    }
