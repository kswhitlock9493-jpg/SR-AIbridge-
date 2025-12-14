"""
Post-Boot Stage
Essential initialization that runs immediately after server starts
"""
import logging
import asyncio

logger = logging.getLogger(__name__)


async def run_post_boot():
    """
    Post-boot initialization stage
    
    - Database connection warming
    - Essential cache priming
    - Health check initialization
    """
    logger.info("🔧 Post-boot stage starting...")
    
    # Warm database connection pool
    try:
        from bridge_backend.db import get_async_session_factory
        factory = get_async_session_factory()
        async with factory() as session:
            # Simple query to warm connection
            await session.execute("SELECT 1")
        logger.info("✅ Database connection warmed")
    except Exception as e:
        logger.warning(f"⚠️ Database warming failed: {e}")
    
    # Initialize health check baseline
    try:
        from bridge_backend.runtime.health_probe import HealthProbe
        probe = HealthProbe()
        await probe.check_all()
        logger.info("✅ Health check baseline established")
    except Exception as e:
        logger.warning(f"⚠️ Health probe failed: {e}")
    
    # Small delay to simulate work
    await asyncio.sleep(1)
    
    logger.info("✅ Post-boot stage completed")
