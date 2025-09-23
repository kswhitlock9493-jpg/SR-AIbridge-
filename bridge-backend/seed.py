"""
SR-AIbridge Database Seeder

- Seeds armada_fleet table with example ships
- Seeds agents table with example AI agents
- Seeds missions table with example missions
- Uses async SQLAlchemy/databases for compatibility with SQLite or Postgres
- Checks for duplicates before inserting data (prevents multiple runs from making extra rows)
- See docs below for usage

Insights:
- Prim: Simple, env-driven, async-ready, easy to run, ensures frontend isn't empty
- Copilot: Added agents and missions tables; guaranteed-to-run starter kit for SQLite

Usage:
    1. Set .env with a working DATABASE_URL (SQLite for guaranteed-to-run experience)
    2. Run: python seed.py
    3. Launch backend (uvicorn main:app --reload) & visit endpoints to verify seeded data
"""

import asyncio
from databases import Database
from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData, select
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bridge.db")

# Table definitions (must match backend)
metadata = MetaData()

armada_fleet = Table(
    "armada_fleet",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("status", String, nullable=False),
    Column("location", String, nullable=False),
)

agents = Table(
    "agents",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("endpoint", String, nullable=False),
    Column("capabilities", String, nullable=True),  # JSON string
    Column("status", String, nullable=False, default="offline"),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("last_heartbeat", DateTime, nullable=True),
)

missions = Table(
    "missions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("description", String, nullable=True),
    Column("status", String, nullable=False, default="pending"),
    Column("assigned_agent_id", String, nullable=True),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("completed_at", DateTime, nullable=True),
)

async def seed_data():
    db = Database(DATABASE_URL)
    await db.connect()

    # Create tables if they don't exist (for SQLite quickstart)
    if DATABASE_URL.startswith("sqlite"):
        import sqlalchemy
        engine = sqlalchemy.create_engine(DATABASE_URL)
        metadata.create_all(engine)

    # Example fleet -- adjust for your domain
    ships = [
        {"name": "SR-Flagship", "status": "online", "location": "Bridge Command"},
        {"name": "SR-Vanguard", "status": "online", "location": "Outer Rim"},
        {"name": "SR-Defiant", "status": "offline", "location": "Dry Dock"},
        {"name": "SR-Oracle", "status": "online", "location": "Deep Space Node"},
    ]

    # Example agents
    example_agents = [
        {
            "id": "agent-001", 
            "name": "Navigation AI",
            "endpoint": "http://localhost:8001/nav",
            "capabilities": '[]',
            "status": "offline",
            "created_at": datetime.utcnow()
        },
        {
            "id": "agent-002",
            "name": "Communications AI", 
            "endpoint": "http://localhost:8002/comms",
            "capabilities": '[]',
            "status": "offline",
            "created_at": datetime.utcnow()
        },
    ]

    # Example missions
    example_missions = [
        {
            "title": "System Patrol Alpha",
            "description": "Routine patrol of Alpha sector",
            "status": "pending",
            "assigned_agent_id": None,
            "created_at": datetime.utcnow()
        },
        {
            "title": "Communications Check",
            "description": "Test all communication arrays",
            "status": "in_progress", 
            "assigned_agent_id": "agent-002",
            "created_at": datetime.utcnow()
        },
    ]

    # Seed armada fleet
    print("🚢 Seeding armada fleet...")
    for ship in ships:
        query = select(armada_fleet).where(armada_fleet.c.name == ship["name"])
        exists = await db.fetch_one(query)
        if not exists:
            await db.execute(armada_fleet.insert().values(**ship))
            print(f"✅ Added ship: {ship['name']}")
        else:
            print(f"⏩ Skipped (already exists): {ship['name']}")

    # Seed agents
    print("🤖 Seeding agents...")
    for agent in example_agents:
        query = select(agents).where(agents.c.id == agent["id"])
        exists = await db.fetch_one(query)
        if not exists:
            await db.execute(agents.insert().values(**agent))
            print(f"✅ Added agent: {agent['name']}")
        else:
            print(f"⏩ Skipped (already exists): {agent['name']}")

    # Seed missions
    print("🚀 Seeding missions...")
    for mission in example_missions:
        query = select(missions).where(missions.c.title == mission["title"])
        exists = await db.fetch_one(query)
        if not exists:
            await db.execute(missions.insert().values(**mission))
            print(f"✅ Added mission: {mission['title']}")
        else:
            print(f"⏩ Skipped (already exists): {mission['title']}")

    await db.disconnect()
    print("🎉 Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_data())
