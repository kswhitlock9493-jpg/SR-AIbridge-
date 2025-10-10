__version__ = "1.9.6d"

# This file makes bridge_backend a Python package for proper imports.

# Database connection validation on startup
import asyncio
import logging

logger = logging.getLogger(__name__)


def verify_database_connection():
    """Verify database connection on startup (synchronous version for SQLAlchemy)."""
    try:
        from bridge_backend.config import settings
        from sqlalchemy import create_engine, text
        
        # Create a synchronous engine for verification
        engine = create_engine(settings.DATABASE_URL, echo=False)
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection verified.")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def verify_database_connection_async():
    """Verify database connection on startup (async version)"""
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
            asyncio.create_task(verify_database_connection_async())
        else:
            # If no loop is running, run synchronously
            asyncio.run(verify_database_connection_async())
    except RuntimeError:
        # No event loop available yet, will be called during FastAPI startup
        pass


# Auto-diagnose deployment logs if enabled
def run_auto_diagnose():
    """Run deployment diagnostics if AUTO_DIAGNOSE is enabled"""
    try:
        from bridge_backend.config import settings
        from subprocess import run
        import os
        
        if settings.AUTO_DIAGNOSE:
            print("🧩 Auto-diagnose active. Running deploy_diagnose.py...")
            # Get the directory containing this __init__.py file
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(backend_dir, "scripts", "deploy_diagnose.py")
            run(["python3", script_path], check=False)
    except Exception as e:
        print(f"⚠️ Auto-diagnose skipped: {e}")

