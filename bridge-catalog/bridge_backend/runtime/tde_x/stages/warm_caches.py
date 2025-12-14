"""
Warm Caches Stage
Preload frequently accessed data into memory
"""
import logging
import asyncio

logger = logging.getLogger(__name__)


async def run_warm_caches():
    """
    Warm caches stage
    
    - Preload protocol registry
    - Warm mission cache
    - Preload agent definitions
    """
    logger.info("🔥 Warm caches stage starting...")
    
    # Warm protocol registry
    try:
        from bridge_backend.bridge_core.protocols.storage import load_registry
        load_registry()
        logger.info("✅ Protocol registry warmed")
    except Exception as e:
        logger.warning(f"⚠️ Protocol registry warming failed: {e}")
    
    # Warm agent foundry cache (if available)
    try:
        from bridge_backend.bridge_core.engines.agents_foundry.cache import warm_agent_cache
        await warm_agent_cache()
        logger.info("✅ Agent cache warmed")
    except Exception as e:
        logger.debug(f"Agent cache warming not available: {e}")
    
    # Warm Genesis manifest
    try:
        from bridge_backend.genesis.manifest import genesis_manifest
        genesis_manifest.load()
        logger.info("✅ Genesis manifest warmed")
    except Exception as e:
        logger.warning(f"⚠️ Genesis manifest warming failed: {e}")
    
    # Small delay to simulate work
    await asyncio.sleep(2)
    
    logger.info("✅ Warm caches stage completed")
