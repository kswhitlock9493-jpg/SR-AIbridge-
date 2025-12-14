import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL") or ""
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    # enforce async driver for SQLAlchemy 2.x
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

Base = declarative_base()

# Create engine only if DATABASE_URL is set, otherwise use SQLite as fallback
if not DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///./bridge_local.db"

engine: AsyncEngine = create_async_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

async def init_schema():
    from bridge_backend.models import Base as ModelsBase  # ensure model import
    async with engine.begin() as conn:
        await conn.run_sync(ModelsBase.metadata.create_all)
    logger.info("[DB] ✅ Database schema synchronized successfully.")
