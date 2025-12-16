import pytest
from bridge_core.db import db_manager
from bridge_core.db.models import Mission, Log
from sqlalchemy import select

@pytest.mark.asyncio
async def test_mission_and_log_models(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path}/orm.db")
    await db_manager.init_db()

    async with db_manager.SessionLocal() as session:
        # add mission
        m = Mission(name="Scout Asteroid", status="pending")
        session.add(m)
        await session.commit()

        res = await session.execute(select(Mission))
        missions = res.scalars().all()
        assert missions[0].name == "Scout Asteroid"

        # add log
        l = Log(timestamp="2025-09-27T01:00:00Z", source="system", message="online")
        session.add(l)
        await session.commit()

        res2 = await session.execute(select(Log))
        logs = res2.scalars().all()
        assert logs[0].message == "online"