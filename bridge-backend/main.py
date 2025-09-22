import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy import (
    Table, Column, Integer, String, DateTime, MetaData
)
from databases import Database
from dotenv import load_dotenv

# Load env variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bridge.db")  # fallback to sqlite

# Database setup
metadata = MetaData()

captain_messages = Table(
    "captain_messages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("from_", String, nullable=False),
    Column("to", String, nullable=False),
    Column("message", String, nullable=False),
    Column("timestamp", DateTime, default=datetime.utcnow),
)

armada_fleet = Table(
    "armada_fleet",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("status", String, nullable=False),
    Column("location", String, nullable=False),
)

database = Database(DATABASE_URL)

app = FastAPI(title="SR-AIbridge Backend")

# --- Models ---
class Message(BaseModel):
    from_: str
    to: str
    message: str
    timestamp: datetime = datetime.utcnow()

# --- Startup / Shutdown ---
@app.on_event("startup")
async def startup():
    await database.connect()
    # Create tables if they do not exist (for SQLite quickstart)
    if DATABASE_URL.startswith("sqlite"):
        import sqlalchemy
        engine = sqlalchemy.create_engine(DATABASE_URL)
        metadata.create_all(engine)
        # Pre-seed armada_fleet if empty
        with engine.connect() as conn:
            result = conn.execute(armada_fleet.select())
            if result.rowcount == 0:
                conn.execute(armada_fleet.insert(), [
                    {"name": "Flagship Sovereign", "status": "online", "location": "Sector Alpha"},
                    {"name": "Frigate Horizon", "status": "offline", "location": "Sector Beta"},
                    {"name": "Scout Whisper", "status": "online", "location": "Sector Delta"},
                ])

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# --- Captain-to-Captain Endpoints ---
@app.get("/captains/messages", response_model=List[Message])
async def list_messages():
    query = captain_messages.select().order_by(captain_messages.c.timestamp.desc())
    results = await database.fetch_all(query)
    # Convert SQLAlchemy row objects to Message objects
    return [Message(**{**dict(r), "from_": r["from_"]}) for r in results]

@app.post("/captains/send")
async def send_message(msg: Message):
    query = captain_messages.insert().values(
        from_=msg.from_, to=msg.to, message=msg.message, timestamp=msg.timestamp
    )
    await database.execute(query)
    return {"ok": True, "stored": msg.dict()}

# --- Armada Endpoints ---
@app.get("/armada/status")
async def get_armada():
    query = armada_fleet.select()
    results = await database.fetch_all(query)
    return [dict(r) for r in results]

# --- Status Endpoint ---
@app.get("/status")
async def get_status():
    return {
        "agents_online": 2,
        "active_missions": 1,
        "admiral": "Admiral Kyle"
    }