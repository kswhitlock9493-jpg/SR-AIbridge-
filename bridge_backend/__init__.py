# This file makes bridge_backend a Python package for proper imports.

# Database connection validation on startup
import asyncio
import logging

logger = logging.getLogger(__name__)


async def verify_database_connection():
    """Verify database connection on startup"""
    try:
        # Import here to avoid circular dependencies
        from bridge_backend.db import async_engine
        from sqlalchemy import text
        
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection verified.")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


# Run verification on import if running in async context
# This will be called by the FastAPI lifespan events
def init_database_check():
    """Initialize database check - call this from FastAPI startup"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, schedule the task
            asyncio.create_task(verify_database_connection())
        else:
            # If no loop is running, run synchronously
            asyncio.run(verify_database_connection())
    except RuntimeError:
        # No event loop available yet, will be called during FastAPI startup
        pass
