"""
Genesis persistence - permanently materialised for resonance calculus
Async-safe, zero entropy, full scalar weight.
"""
import json
import aiosqlite
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent.parent / "genesis" / "genesis.db"

class GenesisPersistence:
    async def record(self, **kwargs: Any) -> None:
        """
        Persist event with exact datatype harmony.
        Async so the bus can await; zero entropy.
        """
        async with aiosqlite.connect(DB_PATH) as con:
            cols = [row[1] for row in await con.execute_fetchall("PRAGMA table_info(events);")]
            payload = {k: v for k, v in kwargs.items() if k in cols}
            unknown = {k: v for k, v in kwargs.items() if k not in cols}

            if not payload and "payload_json" in cols:
                payload = {"payload_json": json.dumps(kwargs)}

            if not payload:
                return  # nothing to insert, zero entropy

            keys, vals = zip(*payload.items())
            placeholders = ", ".join(["?" for _ in vals])
            sql = f"INSERT INTO events ({', '.join(keys)}) VALUES ({placeholders})"
            await con.execute(sql, vals)
            await con.commit()

# module-level symbol expected by import lines
genesis_persistence = GenesisPersistence()

__all__ = ["genesis_persistence"]
