"""
SR-AIbridge Armada Seeder

- Seeds armada_fleet table with example ships (adjust names/locations if desired)
- Uses async SQLAlchemy/databases for compatibility with SQLite or Postgres
- Checks for duplicates before inserting ships (prevents multiple runs from making extra rows)
- See docs below for usage

Insights:
- Prim: Simple, env-driven, async-ready, easy to run, ensures frontend map isn’t empty
- Copilot: Added duplicate check for safer reseeding; recommended pattern for dev AND prod bootstrapping.

Usage:
    1. Set .env with a working DATABASE_URL (Postgres, Railway, or fallback SQLite)
    2. Run: python seed.py
    3. Launch backend (uvicorn main:app --reload) & visit /armada/status to verify seeded fleet
"""

import asyncio
from databases import Database
from sqlalchemy import Table, Column, Integer, String, MetaData, select
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bridge.db")

# Table definition (must match backend)
metadata = MetaData()

armada_fleet = Table(
    "armada_fleet",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("status", String, nullable=False),
    Column("location", String, nullable=False),
)

async def seed_data():
    db = Database(DATABASE_URL)
    await db.connect()

    # Example fleet -- adjust for your domain
    ships = [
        {"name": "SR-Flagship", "status": "online", "location": "Bridge Command"},
        {"name": "SR-Vanguard", "status": "online", "location": "Outer Rim"},
        {"name": "SR-Defiant", "status": "offline", "location": "Dry Dock"},
        {"name": "SR-Oracle", "status": "online", "location": "Deep Space Node"},
    ]

    # Prevent duplicates: check by name
    for ship in ships:
        query = select([armada_fleet]).where(armada_fleet.c.name == ship["name"])
        exists = await db.fetch_one(query)
        if not exists:
            await db.execute(armada_fleet.insert().values(**ship))
            print(f"✅ Added {ship['name']}")
        else:
            print(f"⏩ Skipped (already exists): {ship['name']}")

    await db.disconnect()
    print("🎉 Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_data())
