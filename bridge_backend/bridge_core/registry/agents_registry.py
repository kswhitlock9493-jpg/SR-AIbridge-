from __future__ import annotations
from pathlib import Path
import json
from typing import Dict, List, Any, Optional

try:
    from bridge_core.engines.indoctrination.service import IndoctrinationEngine
    from bridge_core.engines.agents_foundry.service import AgentsFoundry
except ImportError:
    from bridge_backend.bridge_core.engines.indoctrination.service import IndoctrinationEngine
    from bridge_backend.bridge_core.engines.agents_foundry.service import AgentsFoundry

VAULT_ROOT = Path("vault")

class AgentRegistry:
    def __init__(self,
                 indoctrination_dir: Path = VAULT_ROOT / "indoctrination",
                 agents_dir: Path = VAULT_ROOT / "agents"):
        self.indoctrination = IndoctrinationEngine(indoctrination_dir)
        self.foundry = AgentsFoundry(agents_dir)

    def list_all(self, project: Optional[str] = None) -> Dict[str, Any]:
        """Return all indoctrination scrolls + created agents."""
        scrolls = self.indoctrination.list_scrolls()
        agents = self.foundry.list(project=project)
        return {
            "indoctrination": scrolls,
            "agents": agents,
            "count": {"scrolls": len(scrolls), "agents": len(agents)},
        }

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Return full manifest of a specific agent if exists."""
        m = self.foundry.get(agent_id)
        if not m:
            return None
        return m.__dict__

    def resolve_project_agents(self, project: str) -> List[Dict[str, Any]]:
        """Return agents tied to a project namespace."""
        return self.foundry.list(project=project)
