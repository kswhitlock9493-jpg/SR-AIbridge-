"""
Database Bootstrap Module for SR-AIbridge v1.9.6b

Auto-creates database schemas if missing on startup.
Ensures seamless deployment without manual migration steps.
"""
import logging

logger = logging.getLogger(__name__)


async def auto_sync_schema():
    """
    Auto-synchronize database schema.
    Creates all tables if they don't exist.
    Safe to call on every startup - only creates missing tables.
    """
    try:
        from bridge_backend.utils.db import engine
        from bridge_backend.models import Base as ModelsBase

        async with engine.begin() as conn:
            await conn.run_sync(ModelsBase.metadata.create_all)

        logger.info("[DB Bootstrap] ✅ Schema auto-sync complete")
        return True
    except Exception as e:
        logger.warning(f"[DB Bootstrap] ⚠️ Schema sync failed (non-fatal): {e}")
        return False
