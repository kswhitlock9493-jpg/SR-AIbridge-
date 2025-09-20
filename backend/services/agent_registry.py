import aiosqlite
import json
import uuid
from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from models.agent import Agent, AgentStatus, AgentCapability, AgentRegistration, AgentHeartbeat


class AgentRegistry:
    """Agent registry service with SQLite persistence"""
    
    def __init__(self, db_path: str = "agents.db"):
        self.db_path = db_path
        self.db_dir = Path(db_path).parent
        self.db_dir.mkdir(parents=True, exist_ok=True)
    
    async def initialize_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    status TEXT NOT NULL,
                    capabilities TEXT,
                    last_heartbeat TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            await db.commit()
    
    async def register_agent(self, registration: AgentRegistration) -> Agent:
        """Register a new agent"""
        agent_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        agent = Agent(
            id=agent_id,
            name=registration.name,
            endpoint=registration.endpoint,
            status=AgentStatus.OFFLINE,
            capabilities=registration.capabilities,
            created_at=now,
            updated_at=now,
            metadata=registration.metadata
        )
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO agents 
                (id, name, endpoint, status, capabilities, last_heartbeat, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent.id,
                agent.name,
                agent.endpoint,
                agent.status.value,
                json.dumps([cap.dict() for cap in agent.capabilities]),
                None,
                agent.created_at.isoformat(),
                agent.updated_at.isoformat(),
                json.dumps(agent.metadata) if agent.metadata else None
            ))
            await db.commit()
        
        return agent
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM agents WHERE id = ?", (agent_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_agent(row)
    
    async def get_all_agents(self) -> List[Agent]:
        """Get all agents"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM agents ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            
            return [self._row_to_agent(row) for row in rows]
    
    async def get_agents_by_capability(self, capability_name: str) -> List[Agent]:
        """Get agents by capability"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM agents")
            rows = await cursor.fetchall()
            
            agents = []
            for row in rows:
                agent = self._row_to_agent(row)
                if any(cap.name == capability_name for cap in agent.capabilities):
                    agents.append(agent)
            
            return agents
    
    async def update_heartbeat(self, heartbeat: AgentHeartbeat) -> Optional[Agent]:
        """Update agent heartbeat"""
        now = datetime.utcnow()
        
        async with aiosqlite.connect(self.db_path) as db:
            # Update heartbeat and status
            await db.execute("""
                UPDATE agents 
                SET last_heartbeat = ?, status = ?, updated_at = ?
                WHERE id = ?
            """, (
                now.isoformat(),
                heartbeat.status.value,
                now.isoformat(),
                heartbeat.agent_id
            ))
            await db.commit()
            
            # Return updated agent
            return await self.get_agent(heartbeat.agent_id)
    
    async def remove_agent(self, agent_id: str) -> bool:
        """Remove agent from registry"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM agents WHERE id = ?", (agent_id,)
            )
            await db.commit()
            return cursor.rowcount > 0
    
    async def get_agents_by_status(self, status: AgentStatus) -> List[Agent]:
        """Get agents by status"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM agents WHERE status = ?", (status.value,)
            )
            rows = await cursor.fetchall()
            
            return [self._row_to_agent(row) for row in rows]
    
    async def cleanup_stale_agents(self, timeout_minutes: int = 5):
        """Mark agents as offline if no heartbeat within timeout"""
        cutoff = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE agents 
                SET status = ? 
                WHERE last_heartbeat < ? AND status != ?
            """, (
                AgentStatus.OFFLINE.value,
                cutoff.isoformat(),
                AgentStatus.OFFLINE.value
            ))
            await db.commit()
    
    def _row_to_agent(self, row) -> Agent:
        """Convert database row to Agent object"""
        capabilities_data = json.loads(row['capabilities']) if row['capabilities'] else []
        capabilities = [AgentCapability(**cap) for cap in capabilities_data]
        
        return Agent(
            id=row['id'],
            name=row['name'],
            endpoint=row['endpoint'],
            status=AgentStatus(row['status']),
            capabilities=capabilities,
            last_heartbeat=datetime.fromisoformat(row['last_heartbeat']) if row['last_heartbeat'] else None,
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            metadata=json.loads(row['metadata']) if row['metadata'] else None
        )