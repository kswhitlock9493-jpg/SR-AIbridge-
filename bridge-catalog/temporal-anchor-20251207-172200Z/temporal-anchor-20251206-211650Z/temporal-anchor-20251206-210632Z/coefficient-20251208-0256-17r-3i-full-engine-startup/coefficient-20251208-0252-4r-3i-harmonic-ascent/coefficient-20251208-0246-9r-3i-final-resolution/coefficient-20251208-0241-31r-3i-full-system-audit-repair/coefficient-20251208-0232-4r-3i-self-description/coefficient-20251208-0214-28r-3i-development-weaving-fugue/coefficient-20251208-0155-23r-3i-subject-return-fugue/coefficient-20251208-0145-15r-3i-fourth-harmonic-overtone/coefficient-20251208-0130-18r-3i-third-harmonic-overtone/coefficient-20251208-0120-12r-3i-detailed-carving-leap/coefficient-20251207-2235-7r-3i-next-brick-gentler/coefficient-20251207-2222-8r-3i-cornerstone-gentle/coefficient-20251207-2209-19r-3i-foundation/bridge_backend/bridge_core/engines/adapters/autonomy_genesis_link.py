"""
Autonomy Genesis Link - Event-driven autonomous healing

Subscribes to deployment and environment events and triggers
autonomous healing through the Governor.
"""

import logging
from typing import Dict, Any
from bridge_backend.genesis.bus import genesis_bus
from bridge_backend.engines.autonomy.governor import AutonomyGovernor
from bridge_backend.engines.autonomy.models import Incident

logger = logging.getLogger(__name__)


async def on_netlify_preview_failed(event: Dict[str, Any]):
    """Handle Netlify preview failure events"""
    try:
        logger.info("[Autonomy Genesis] Netlify preview failed event received")
        
        incident = Incident(
            kind="deploy.netlify.preview_failed",
            source="netlify",
            details=event
        )
        
        gov = AutonomyGovernor()
        decision = await gov.decide(incident)
        result = await gov.execute(decision)
        
        logger.info(f"[Autonomy Genesis] Decision: {decision.action}, Result: {result.get('status')}")
    except Exception as e:
        logger.exception(f"[Autonomy Genesis] Failed to handle Netlify preview failure: {e}")


async def on_render_deploy_failed(event: Dict[str, Any]):
    """Handle Render deployment failure events"""
    try:
        logger.info("[Autonomy Genesis] Render deploy failed event received")
        
        incident = Incident(
            kind="deploy.render.failed",
            source="render",
            details=event
        )
        
        gov = AutonomyGovernor()
        decision = await gov.decide(incident)
        result = await gov.execute(decision)
        
        logger.info(f"[Autonomy Genesis] Decision: {decision.action}, Result: {result.get('status')}")
    except Exception as e:
        logger.exception(f"[Autonomy Genesis] Failed to handle Render deploy failure: {e}")


async def on_envrecon_drift(event: Dict[str, Any]):
    """Handle environment drift detection events"""
    try:
        logger.info("[Autonomy Genesis] EnvRecon drift event received")
        
        incident = Incident(
            kind="envrecon.drift",
            source="envrecon",
            details=event
        )
        
        gov = AutonomyGovernor()
        decision = await gov.decide(incident)
        result = await gov.execute(decision)
        
        logger.info(f"[Autonomy Genesis] Decision: {decision.action}, Result: {result.get('status')}")
    except Exception as e:
        logger.exception(f"[Autonomy Genesis] Failed to handle EnvRecon drift: {e}")


async def on_arie_deprecated_detected(event: Dict[str, Any]):
    """Handle ARIE deprecation detection events"""
    try:
        logger.info("[Autonomy Genesis] ARIE deprecation event received")
        
        incident = Incident(
            kind="arie.deprecated.detected",
            source="arie",
            details=event
        )
        
        gov = AutonomyGovernor()
        decision = await gov.decide(incident)
        result = await gov.execute(decision)
        
        logger.info(f"[Autonomy Genesis] Decision: {decision.action}, Result: {result.get('status')}")
    except Exception as e:
        logger.exception(f"[Autonomy Genesis] Failed to handle ARIE deprecation: {e}")


def register_autonomy_genesis_links():
    """
    Register all autonomy event subscriptions with Genesis bus
    
    This should be called during application startup to wire
    autonomy into the Genesis event system.
    """
    if not genesis_bus.is_enabled():
        logger.info("[Autonomy Genesis] Genesis bus disabled, skipping link registration")
        return
    
    logger.info("[Autonomy Genesis] Registering event subscriptions")
    
    # Subscribe to deployment events
    genesis_bus.subscribe("deploy.netlify.preview_failed", on_netlify_preview_failed)
    genesis_bus.subscribe("deploy.render.failed", on_render_deploy_failed)
    
    # Subscribe to environment events
    genesis_bus.subscribe("envrecon.drift", on_envrecon_drift)
    
    # Subscribe to ARIE events
    genesis_bus.subscribe("arie.deprecated.detected", on_arie_deprecated_detected)
    
    logger.info("[Autonomy Genesis] Event subscriptions registered")


# Auto-register on import if enabled
import os
if os.getenv("AUTONOMY_ENABLED", "true").lower() == "true":
    try:
        register_autonomy_genesis_links()
    except Exception as e:
        logger.warning(f"[Autonomy Genesis] Failed to auto-register links: {e}")
