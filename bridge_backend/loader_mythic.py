import json
from pathlib import Path

MYTHIC_DIR = Path(__file__).parent.parent / "bridge_native_agents" / "agents"

def awaken_mythic():
    for p in MYTHIC_DIR.glob("*.json"):
        agent = json.loads(p.read_text())
        print(f"🔱 PERMANENCE: {agent['callsign']} awakened – {agent['mythic_role']}")

# FastAPI lifespan hook
from contextlib import asynccontextmanager

@asynccontextmanager
async def mythic_lifespan(app):
    awaken_mythic()
    yield
