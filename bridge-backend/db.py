"""
Async database module for SR-AIbridge using SQLAlchemy AsyncSession
Fixes MissingGreenlet error with proper async SQLite support
"""
import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, func, MetaData, Table, select, insert, update, delete
from sqlalchemy.exc import SQLAlchemyError

# Setup logging
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bridge.db")

# Convert to async URL format
if DATABASE_URL.startswith("sqlite:///"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
elif DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
elif DATABASE_URL.startswith("postgres://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

logger.info(f"🔧 Async database URL: {ASYNC_DATABASE_URL}")

# Create async engine with proper SQLite configuration
engine_kwargs = {}
if "sqlite" in ASYNC_DATABASE_URL:
    # SQLite specific configuration for async
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {
            "check_same_thread": False,
            "timeout": 30
        }
    })

# Create async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    **engine_kwargs
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# SQLAlchemy models
Base = declarative_base()
metadata = MetaData()

# Define tables for async operations
agents_table = Table(
    "agents", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(255), nullable=False),
    Column("endpoint", String(255), nullable=False),
    Column("capabilities", Text),  # JSON string
    Column("status", String(50), default="online"),
    Column("last_heartbeat", DateTime),
    Column("created_at", DateTime, server_default=func.now())
)

missions_table = Table(
    "missions", metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(255), nullable=False),
    Column("description", Text),
    Column("status", String(50), default="active"),
    Column("priority", String(50), default="normal"),
    Column("agent_id", Integer),
    Column("progress", Integer, default=0),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now())
)

vault_logs_table = Table(
    "vault_logs", metadata,
    Column("id", Integer, primary_key=True),
    Column("agent_name", String(255), nullable=False),
    Column("action", String(255), nullable=False),
    Column("details", Text),
    Column("log_level", String(50), default="info"),
    Column("timestamp", DateTime, server_default=func.now())
)

captain_messages_table = Table(
    "captain_messages", metadata,
    Column("id", Integer, primary_key=True),
    Column("message", Text, nullable=False),
    Column("author", String(255), default="System"),
    Column("timestamp", DateTime, server_default=func.now()),
    Column("channel", String(100), default="bridge")
)

armada_fleet_table = Table(
    "armada_fleet", metadata,
    Column("id", Integer, primary_key=True),
    Column("ship_name", String(255), nullable=False),
    Column("status", String(50), default="online"),
    Column("location", String(255), nullable=False),
    Column("patrol_sectors", Text),  # JSON array as text
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now())
)


class DatabaseManager:
    """Async database manager for SR-AIbridge"""
    
    def __init__(self):
        self.engine = async_engine
        self.session_factory = AsyncSessionLocal
        self._initialized = False
    
    async def initialize(self):
        """Initialize database tables"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(metadata.create_all)
            self._initialized = True
            logger.info("✅ Database tables initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            raise
    
    async def close(self):
        """Close database connection"""
        await self.engine.dispose()
        logger.info("🛑 Database connection closed")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async session context manager"""
        if not self._initialized:
            await self.initialize()
        
        async with self.session_factory() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Database error: {e}")
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            async with self.get_session() as session:
                # Simple query to test connection
                result = await session.execute(select(func.count()).select_from(agents_table))
                agent_count = result.scalar()
                
                return {
                    "status": "healthy",
                    "connection": "active",
                    "agent_count": agent_count,
                    "database_type": DATABASE_TYPE,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "database_type": DATABASE_TYPE,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # Agent operations
    async def get_agents(self) -> List[Dict[str, Any]]:
        """Get all agents"""
        async with self.get_session() as session:
            result = await session.execute(select(agents_table))
            return [dict(row._mapping) for row in result]
    
    async def create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent"""
        async with self.get_session() as session:
            stmt = insert(agents_table).values(**agent_data)
            result = await session.execute(stmt)
            await session.commit()
            
            # Return the created agent
            agent_id = result.inserted_primary_key[0]
            created_agent = await session.execute(
                select(agents_table).where(agents_table.c.id == agent_id)
            )
            return dict(created_agent.fetchone()._mapping)
    
    # Mission operations
    async def get_missions(self) -> List[Dict[str, Any]]:
        """Get all missions"""
        async with self.get_session() as session:
            result = await session.execute(select(missions_table))
            return [dict(row._mapping) for row in result]
    
    async def create_mission(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new mission"""
        async with self.get_session() as session:
            stmt = insert(missions_table).values(**mission_data)
            result = await session.execute(stmt)
            await session.commit()
            
            # Return the created mission
            mission_id = result.inserted_primary_key[0]
            created_mission = await session.execute(
                select(missions_table).where(missions_table.c.id == mission_id)
            )
            return dict(created_mission.fetchone()._mapping)
    
    # Vault logs operations
    async def get_vault_logs(self) -> List[Dict[str, Any]]:
        """Get all vault logs"""
        async with self.get_session() as session:
            result = await session.execute(
                select(vault_logs_table).order_by(vault_logs_table.c.timestamp.desc())
            )
            return [dict(row._mapping) for row in result]
    
    async def create_vault_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new vault log entry"""
        async with self.get_session() as session:
            stmt = insert(vault_logs_table).values(**log_data)
            result = await session.execute(stmt)
            await session.commit()
            
            # Return the created log
            log_id = result.inserted_primary_key[0]
            created_log = await session.execute(
                select(vault_logs_table).where(vault_logs_table.c.id == log_id)
            )
            return dict(created_log.fetchone()._mapping)
    
    # Captain messages operations
    async def get_captain_messages(self) -> List[Dict[str, Any]]:
        """Get all captain messages"""
        async with self.get_session() as session:
            result = await session.execute(
                select(captain_messages_table).order_by(captain_messages_table.c.timestamp.desc())
            )
            return [dict(row._mapping) for row in result]
    
    async def create_captain_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new captain message"""
        async with self.get_session() as session:
            stmt = insert(captain_messages_table).values(**message_data)
            result = await session.execute(stmt)
            await session.commit()
            
            # Return the created message
            message_id = result.inserted_primary_key[0]
            created_message = await session.execute(
                select(captain_messages_table).where(captain_messages_table.c.id == message_id)
            )
            return dict(created_message.fetchone()._mapping)
    
    # Armada fleet operations
    async def get_armada_fleet(self) -> List[Dict[str, Any]]:
        """Get all armada fleet data"""
        async with self.get_session() as session:
            result = await session.execute(select(armada_fleet_table))
            return [dict(row._mapping) for row in result]
    
    async def create_fleet_entry(self, fleet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new fleet entry"""
        async with self.get_session() as session:
            stmt = insert(armada_fleet_table).values(**fleet_data)
            result = await session.execute(stmt)
            await session.commit()
            
            # Return the created entry
            entry_id = result.inserted_primary_key[0]
            created_entry = await session.execute(
                select(armada_fleet_table).where(armada_fleet_table.c.id == entry_id)
            )
            return dict(created_entry.fetchone()._mapping)


# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions for easy access
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session - convenience function"""
    async with db_manager.get_session() as session:
        yield session


async def init_database():
    """Initialize database - convenience function"""
    await db_manager.initialize()


async def close_database():
    """Close database - convenience function"""
    await db_manager.close()


async def database_health():
    """Check database health - convenience function"""
    return await db_manager.health_check()