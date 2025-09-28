import os
import asyncio
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy import text
from .models import Base  # ORM Base import

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./vault/bridge.db")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def init_db():
    """Initialize database with required tables (idempotent)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # ORM migration

async def get_missions() -> List[Dict[str, Any]]:
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT id, name, status, created_at FROM missions"))
        return [dict(r) for r in result.mappings()]

async def add_mission(name: str, status: str, created_at: str):
    async with SessionLocal() as session:
        await session.execute(
            text("INSERT INTO missions (name, status, created_at) VALUES (:n, :s, :c)"),
            {"n": name, "s": status, "c": created_at},
        )
        await session.commit()

async def get_logs(limit: int = 100) -> List[Dict[str, Any]]:
    async with SessionLocal() as session:
        result = await session.execute(
            text("SELECT id, timestamp, source, message, details FROM logs ORDER BY id DESC LIMIT :lim"),
            {"lim": limit},
        )
        return [dict(r) for r in result.mappings()]

async def add_log(timestamp: str, source: str, message: str, details: str = ""):
    async with SessionLocal() as session:
        await session.execute(
            text("INSERT INTO logs (timestamp, source, message, details) VALUES (:t, :src, :m, :d)"),
            {"t": timestamp, "src": source, "m": message, "d": details},
        )
        await session.commit()