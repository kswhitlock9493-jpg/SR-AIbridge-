"""
Chimera Genesis Link Adapter
Links Chimera engine to Genesis event bus
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

chimera_engine = None


async def register():
    """Register Chimera engine with Genesis bus"""
    global chimera_engine
    
    try:
        from ...genesis.bus import genesis_bus
        from ...engines.chimera.core import ChimeraEngine
        
        chimera_engine = ChimeraEngine(Path(".").resolve())
        
        # Subscribe to deploy events
        await genesis_bus.subscribe("deploy.preview.requested", on_preview_requested)
        await genesis_bus.subscribe("deploy.preview.failed", on_preview_failed)
        
        logger.info("✅ Chimera Genesis link registered")
    except Exception as e:
        logger.error(f"❌ Failed to register Chimera Genesis link: {e}")
        raise


async def on_preview_requested(event):
    """Handle preview requested event"""
    try:
        if chimera_engine:
            await chimera_engine.preflight()
            logger.info("🚀 Chimera preflight completed for preview request")
    except Exception as e:
        logger.error(f"❌ Chimera preflight failed: {e}")


async def on_preview_failed(event):
    """Handle preview failure event"""
    try:
        if chimera_engine:
            reason = event.get("reason", "unknown")
            await chimera_engine.heal_after_failure(reason)
            logger.info(f"🩹 Chimera auto-heal applied for reason: {reason}")
    except Exception as e:
        logger.error(f"❌ Chimera auto-heal failed: {e}")
