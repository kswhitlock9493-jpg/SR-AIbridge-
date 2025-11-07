"""
Chimera Genesis Link Adapter
Links Chimera engine to Genesis event bus with retry logic and graceful fallback
"""
from __future__ import annotations
import logging
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

chimera_engine = None

# Retry configuration: quick backoff attempts
RETRY_SECONDS = (0.5, 1, 2, 4)


def _load_bus():
    """
    Load Genesis bus module with normalized import path.
    
    Returns:
        Module or None: Genesis bus module if successful, None otherwise
    """
    try:
        from ...paths import import_genesis_bus
        return import_genesis_bus()
    except Exception as e:
        logger.error(f"[Chimera↔Genesis] import bus failed: {e}")
        return None


def register_chimera_link() -> bool:
    """
    Register Chimera as a Genesis link.
    
    Returns:
        bool: True if registration successful, False otherwise
    """
    bus_mod = _load_bus()
    if bus_mod and hasattr(bus_mod, "genesis_bus"):
        try:
            # Get the actual bus instance
            bus = bus_mod.genesis_bus
            if hasattr(bus, "publish"):
                # Note: publish is async, but we call it synchronously here for boot-time registration
                # The event will be queued and processed by the event loop when it starts
                # This is safe because Genesis bus handles sync calls in boot context
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If loop is running, schedule the coroutine
                        asyncio.create_task(bus.publish("chimera.link.register", {"status": "online"}))
                    else:
                        # If loop is not running, run it synchronously
                        loop.run_until_complete(bus.publish("chimera.link.register", {"status": "online"}))
                except RuntimeError:
                    # No event loop, just skip the publish (safe during testing)
                    pass
                logger.info("✅ Chimera registered to Genesis bus")
                return True
        except Exception as e:
            logger.error(f"[Chimera↔Genesis] publish failed: {e}")
    return False


def register_with_retry() -> bool:
    """
    Register Chimera with retry logic.
    
    Attempts immediate registration, then retries with exponential backoff.
    
    Returns:
        bool: True if registration successful, False if all attempts exhausted
    """
    # Try immediate registration
    if register_chimera_link():
        return True
    
    # Retry with backoff
    for delay in RETRY_SECONDS:
        logger.info(f"[Chimera↔Genesis] Retrying in {delay}s...")
        time.sleep(delay)
        if register_chimera_link():
            return True
    
    logger.warning("⚠️ [Chimera↔Genesis] All registration attempts exhausted")
    return False


async def register():
    """
    Legacy async register function for backward compatibility.
    
    Note: The synchronous register_with_retry() is now preferred.
    """
    global chimera_engine
    
    try:
        from ...paths import import_genesis_bus
        genesis_bus_mod = import_genesis_bus()
        from ...engines.chimera.core import ChimeraEngine
        
        chimera_engine = ChimeraEngine(Path(".").resolve())
        
        # Subscribe to deploy events
        genesis_bus = genesis_bus_mod.genesis_bus
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
