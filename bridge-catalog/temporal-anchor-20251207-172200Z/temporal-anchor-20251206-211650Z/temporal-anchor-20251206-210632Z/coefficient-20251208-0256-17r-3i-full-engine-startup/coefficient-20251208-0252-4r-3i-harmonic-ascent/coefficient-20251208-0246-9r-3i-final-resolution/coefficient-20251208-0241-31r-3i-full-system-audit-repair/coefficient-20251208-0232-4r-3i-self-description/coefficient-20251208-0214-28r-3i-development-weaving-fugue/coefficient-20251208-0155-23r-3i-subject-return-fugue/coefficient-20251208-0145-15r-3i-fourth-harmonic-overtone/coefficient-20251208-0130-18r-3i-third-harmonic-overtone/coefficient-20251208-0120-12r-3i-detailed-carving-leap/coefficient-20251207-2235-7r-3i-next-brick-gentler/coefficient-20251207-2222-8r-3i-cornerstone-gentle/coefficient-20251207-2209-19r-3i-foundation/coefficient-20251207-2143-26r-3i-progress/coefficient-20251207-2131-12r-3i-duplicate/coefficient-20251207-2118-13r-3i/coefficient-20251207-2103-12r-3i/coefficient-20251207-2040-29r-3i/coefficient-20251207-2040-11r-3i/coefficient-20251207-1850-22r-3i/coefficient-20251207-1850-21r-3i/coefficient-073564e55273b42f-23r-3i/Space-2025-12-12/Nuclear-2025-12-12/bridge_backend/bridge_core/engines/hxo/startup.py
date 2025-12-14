"""
HXO Nexus Startup Integration
Automatically initializes the HXO Nexus when the application starts
"""

import logging
import os

logger = logging.getLogger(__name__)


async def startup_hxo_nexus():
    """
    Initialize HXO Nexus on application startup
    
    This function should be called during the FastAPI lifespan startup event
    or equivalent application initialization.
    """
    try:
        # Check if HXO Nexus is enabled
        enabled = os.getenv("HXO_NEXUS_ENABLED", "true").lower() == "true"
        
        if not enabled:
            logger.info("HXO Nexus is disabled via configuration")
            return
        
        # Import and initialize the nexus
        from bridge_core.engines.hxo import initialize_nexus
        
        logger.info("Initializing HXO Nexus...")
        nexus = await initialize_nexus()
        
        # Get health status
        health = await nexus.health_check()
        
        logger.info(
            f"✅ HXO Nexus started successfully: "
            f"{health['nexus_id']} v{health['version']} - "
            f"{health['registered_engines']} engines registered, "
            f"{health['connection_count']} connections"
        )
        
        # Start HypShard if enabled
        hypshard_enabled = os.getenv("HYPSHARD_ENABLED", "true").lower() == "true"
        
        if hypshard_enabled:
            from bridge_core.engines.hxo.hypshard import HypShardV3Manager
            
            manager = HypShardV3Manager()
            await manager.start()
            
            stats = await manager.get_stats()
            logger.info(
                f"✅ HypShard v3 started: "
                f"capacity={stats['capacity']:,}, "
                f"policies={stats['policies']}"
            )
        
        return nexus
        
    except Exception as e:
        logger.error(f"Failed to initialize HXO Nexus: {e}", exc_info=True)
        # Don't crash the application if HXO fails to start
        return None


async def shutdown_hxo_nexus():
    """
    Cleanup HXO Nexus on application shutdown
    """
    try:
        logger.info("Shutting down HXO Nexus...")
        
        # HypShard cleanup would go here if needed
        # For now, just log
        
        logger.info("✅ HXO Nexus shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during HXO Nexus shutdown: {e}", exc_info=True)
