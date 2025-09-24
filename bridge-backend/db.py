"""
SQLite-first async database module for SR-AIbridge
Comprehensive health check, self-heal, and safe error handling
"""
import os
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from models import Base, Guardian, VaultLog, Mission, Agent

# Setup logging
logger = logging.getLogger(__name__)

# SQLite-first database configuration
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bridge.db")

# SQLite-first async URL setup
if DATABASE_URL.startswith("sqlite:///"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
elif DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
elif DATABASE_URL.startswith("postgres://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

logger.info(f"🔧 SQLite-first database URL: {ASYNC_DATABASE_URL}")

# SQLite-optimized async engine configuration
engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "echo": False  # Set to True for SQL debugging
}

if "sqlite" in ASYNC_DATABASE_URL:
    # SQLite-specific optimizations
    engine_kwargs.update({
        "connect_args": {
            "check_same_thread": False,
            "timeout": 30,
            "isolation_level": None  # Autocommit mode for better performance
        }
    })

# Create async engine
async_engine = create_async_engine(ASYNC_DATABASE_URL, **engine_kwargs)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class DatabaseManager:
    """SQLite-first async database manager with health checks and self-heal"""
    
    def __init__(self):
        self.engine = async_engine
        self.session_factory = AsyncSessionLocal
        self._initialized = False
        self._health_status = "unknown"
        self._last_health_check = None
    
    async def initialize(self):
        """Initialize database tables with comprehensive error handling"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            self._initialized = True
            self._health_status = "healthy"
            
            # Initialize default guardian if none exists
            await self._ensure_default_guardian()
            
            logger.info("✅ SQLite-first database initialized successfully")
            return {"status": "success", "message": "Database initialized"}
        except Exception as e:
            self._health_status = "unhealthy"
            error_msg = f"Failed to initialize database: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {"status": "error", "message": error_msg, "error": str(e)}
    
    async def close(self):
        """Close database connection safely"""
        try:
            await self.engine.dispose()
            self._initialized = False
            logger.info("🛑 Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async session with comprehensive error handling"""
        if not self._initialized:
            await self.initialize()
        
        async with self.session_factory() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Database error: {e}")
                raise
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected database error: {e}")
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive database health check with self-healing"""
        check_time = datetime.utcnow()
        
        try:
            async with self.get_session() as session:
                # Test basic connectivity
                from sqlalchemy import text
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                
                # Count records in each table using text() for explicit declaration
                agent_count = await session.scalar(text(f"SELECT COUNT(*) FROM {Agent.__tablename__}"))
                mission_count = await session.scalar(text(f"SELECT COUNT(*) FROM {Mission.__tablename__}"))
                vault_count = await session.scalar(text(f"SELECT COUNT(*) FROM {VaultLog.__tablename__}"))
                guardian_count = await session.scalar(text(f"SELECT COUNT(*) FROM {Guardian.__tablename__}"))
                
                # Calculate health score
                health_score = 100.0
                issues = []
                
                # Check for potential issues
                if guardian_count == 0:
                    health_score -= 20
                    issues.append("No guardians active")
                
                if agent_count == 0:
                    health_score -= 10
                    issues.append("No agents registered")
                
                self._health_status = "healthy" if health_score >= 80 else "degraded" if health_score >= 60 else "unhealthy"
                self._last_health_check = check_time
                
                return {
                    "status": self._health_status,
                    "health_score": health_score,
                    "connection": "active",
                    "database_type": DATABASE_TYPE,
                    "counts": {
                        "agents": agent_count,
                        "missions": mission_count,
                        "vault_logs": vault_count,
                        "guardians": guardian_count
                    },
                    "issues": issues,
                    "last_check": check_time.isoformat(),
                    "self_heal_available": True
                }
        except OperationalError as e:
            # Database connection issues - attempt self-heal
            heal_result = await self.self_heal()
            return {
                "status": "unhealthy",
                "error": "Database connection error",
                "error_details": str(e),
                "database_type": DATABASE_TYPE,
                "last_check": check_time.isoformat(),
                "self_heal_attempted": True,
                "self_heal_result": heal_result
            }
        except Exception as e:
            self._health_status = "unhealthy"
            return {
                "status": "unhealthy", 
                "error": str(e),
                "database_type": DATABASE_TYPE,
                "last_check": check_time.isoformat(),
                "self_heal_available": True
            }
    
    async def self_heal(self) -> Dict[str, Any]:
        """Self-healing database operations"""
        heal_actions = []
        success = True
        
        try:
            # 1. Reinitialize database connection
            heal_actions.append("Reinitializing database connection")
            await self.close()
            self._initialized = False
            init_result = await self.initialize()
            
            if init_result["status"] == "error":
                success = False
                heal_actions.append(f"Failed to reinitialize: {init_result['message']}")
            else:
                heal_actions.append("Database reinitialized successfully")
            
            # 2. Ensure default guardian exists
            guardian_result = await self._ensure_default_guardian()
            heal_actions.append(f"Guardian check: {guardian_result['message']}")
            
            # 3. Clean up orphaned records (if any)
            cleanup_result = await self._cleanup_orphaned_records()
            heal_actions.append(f"Cleanup: {cleanup_result['message']}")
            
            return {
                "status": "success" if success else "partial",
                "actions_taken": heal_actions,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            heal_actions.append(f"Self-heal failed: {str(e)}")
            return {
                "status": "failed",
                "actions_taken": heal_actions,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _ensure_default_guardian(self) -> Dict[str, Any]:
        """Ensure a default guardian exists"""
        try:
            async with self.get_session() as session:
                # Check if any guardians exist
                from sqlalchemy import text
                guardian_count = await session.scalar(text(f"SELECT COUNT(*) FROM {Guardian.__tablename__}"))
                
                if guardian_count == 0:
                    # Create default guardian
                    default_guardian = Guardian(
                        name="System Guardian",
                        status="active",
                        health_score=100.0,
                        active=True
                    )
                    session.add(default_guardian)
                    await session.commit()
                    return {"status": "created", "message": "Default guardian created"}
                else:
                    return {"status": "exists", "message": f"Found {guardian_count} guardians"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to ensure guardian: {str(e)}"}
    
    async def _cleanup_orphaned_records(self) -> Dict[str, Any]:
        """Clean up any orphaned or invalid records"""
        try:
            cleaned_count = 0
            # Add cleanup logic as needed for your specific use case
            return {"status": "success", "message": f"Cleaned {cleaned_count} orphaned records"}
        except Exception as e:
            return {"status": "error", "message": f"Cleanup failed: {str(e)}"}

    # Safe CRUD operations with error handling
    async def get_agents(self) -> List[Dict[str, Any]]:
        """Get all agents safely"""
        try:
            async with self.get_session() as session:
                from sqlalchemy import text
                result = await session.execute(text(f"SELECT * FROM {Agent.__tablename__}"))
                return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Error getting agents: {e}")
            return []
    
    async def create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create agent with safe error handling"""
        try:
            async with self.get_session() as session:
                agent = Agent(**agent_data)
                session.add(agent)
                await session.commit()
                await session.refresh(agent)
                return {"status": "success", "agent": {"id": agent.id, "name": agent.name}}
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_missions(self) -> List[Dict[str, Any]]:
        """Get all missions safely"""
        try:
            async with self.get_session() as session:
                from sqlalchemy import text
                result = await session.execute(text(f"SELECT * FROM {Mission.__tablename__}"))
                return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Error getting missions: {e}")
            return []
    
    async def create_mission(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create mission with safe error handling"""
        try:
            async with self.get_session() as session:
                mission = Mission(**mission_data)
                session.add(mission)
                await session.commit()
                await session.refresh(mission)
                return {"status": "success", "mission": {"id": mission.id, "title": mission.title}}
        except Exception as e:
            logger.error(f"Error creating mission: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_vault_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get vault logs safely"""
        try:
            async with self.get_session() as session:
                from sqlalchemy import text
                result = await session.execute(text(f"SELECT * FROM {VaultLog.__tablename__} ORDER BY timestamp DESC LIMIT {limit}"))
                return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Error getting vault logs: {e}")
            return []
    
    async def create_vault_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create vault log with safe error handling"""
        try:
            async with self.get_session() as session:
                vault_log = VaultLog(**log_data)
                session.add(vault_log)
                await session.commit()
                await session.refresh(vault_log)
                return {"status": "success", "log": {"id": vault_log.id}}
        except Exception as e:
            logger.error(f"Error creating vault log: {e}")
            return {"status": "error", "error": str(e)}

    async def get_guardians(self) -> List[Dict[str, Any]]:
        """Get all guardians safely"""
        try:
            async with self.get_session() as session:
                from sqlalchemy import text
                result = await session.execute(text(f"SELECT * FROM {Guardian.__tablename__}"))
                return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"Error getting guardians: {e}")
            return []
    
    async def create_guardian(self, guardian_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create guardian with safe error handling"""
        try:
            async with self.get_session() as session:
                guardian = Guardian(**guardian_data)
                session.add(guardian)
                await session.commit()
                await session.refresh(guardian)
                return {
                    "status": "success",
                    "message": "Guardian created successfully",
                    "guardian": {
                        "id": guardian.id,
                        "name": guardian.name,
                        "status": guardian.status,
                        "health_score": guardian.health_score,
                        "active": guardian.active
                    }
                }
        except Exception as e:
            logger.error(f"Error creating guardian: {e}")
            return {
                "status": "error",
                "message": f"Failed to create guardian: {str(e)}"
            }

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions for easy access
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session - convenience function"""
    async with db_manager.get_session() as session:
        yield session

async def init_database():
    """Initialize database - convenience function"""
    return await db_manager.initialize()

async def close_database():
    """Close database - convenience function"""
    await db_manager.close()

async def database_health():
    """Check database health - convenience function""" 
    return await db_manager.health_check()

async def database_self_heal():
    """Trigger database self-heal - convenience function"""
    return await db_manager.self_heal()