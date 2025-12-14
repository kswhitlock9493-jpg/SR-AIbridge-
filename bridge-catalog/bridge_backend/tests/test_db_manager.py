import pytest
import asyncio
from bridge_backend.bridge_core.db import db_manager

@pytest.mark.asyncio
async def test_db_manager_missions(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path}/test.db")
    await db_manager.init_db()

    await db_manager.add_mission("Explore Nebula", "pending", "2025-09-27T00:00:00Z")
    missions = await db_manager.get_missions()
    assert len(missions) == 1
    assert missions[0]["name"] == "Explore Nebula"

@pytest.mark.asyncio
async def test_db_manager_logs(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path}/test2.db")
    await db_manager.init_db()

    await db_manager.add_log("2025-09-27T00:00:00Z", "system", "boot", "{}")
    logs = await db_manager.get_logs()
    assert len(logs) == 1
    assert logs[0]["message"] == "boot"