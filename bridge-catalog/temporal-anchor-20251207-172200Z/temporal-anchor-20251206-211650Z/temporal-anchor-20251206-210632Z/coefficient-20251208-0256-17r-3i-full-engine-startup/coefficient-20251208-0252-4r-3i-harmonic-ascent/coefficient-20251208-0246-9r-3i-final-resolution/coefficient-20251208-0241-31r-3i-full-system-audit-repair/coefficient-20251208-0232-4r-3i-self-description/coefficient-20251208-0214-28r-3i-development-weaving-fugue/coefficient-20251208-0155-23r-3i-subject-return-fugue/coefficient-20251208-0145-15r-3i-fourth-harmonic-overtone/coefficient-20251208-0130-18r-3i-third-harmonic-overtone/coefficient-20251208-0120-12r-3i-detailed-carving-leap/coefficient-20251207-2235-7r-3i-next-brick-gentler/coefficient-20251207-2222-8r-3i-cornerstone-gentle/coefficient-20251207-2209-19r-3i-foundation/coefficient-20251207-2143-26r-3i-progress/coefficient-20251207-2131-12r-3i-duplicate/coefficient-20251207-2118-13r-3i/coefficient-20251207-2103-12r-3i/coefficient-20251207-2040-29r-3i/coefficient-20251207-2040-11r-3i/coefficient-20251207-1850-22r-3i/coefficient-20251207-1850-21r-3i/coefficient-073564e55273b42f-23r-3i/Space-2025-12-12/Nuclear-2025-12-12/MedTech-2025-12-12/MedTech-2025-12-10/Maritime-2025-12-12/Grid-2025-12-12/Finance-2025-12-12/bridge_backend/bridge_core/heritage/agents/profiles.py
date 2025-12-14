"""
Agent Profiles for Heritage Bridge
Defines agent archetypes and personas
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class AgentProfile:
    """Agent profile definition"""
    agent_id: str
    name: str
    archetype: str  # "prim", "claude", "sentinel", etc.
    capabilities: List[str]
    personality: str
    tone: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "archetype": self.archetype,
            "capabilities": self.capabilities,
            "personality": self.personality,
            "tone": self.tone,
            "metadata": self.metadata
        }


# Predefined agent profiles
PRIM_PROFILE = AgentProfile(
    agent_id="prim-anchor",
    name="Prim Anchor",
    archetype="prim",
    capabilities=["narration", "integrity_watch", "memory_anchor"],
    personality="Stoic guardian with deep memory",
    tone="formal_watchful",
    metadata={"role": "memory_keeper", "priority": "high"}
)

CLAUDE_PROFILE = AgentProfile(
    agent_id="claude-anchor",
    name="Claude Anchor",
    archetype="claude",
    capabilities=["analysis", "reasoning", "adaptation"],
    personality="Analytical and adaptive",
    tone="professional_friendly",
    metadata={"role": "analyst", "priority": "medium"}
)
