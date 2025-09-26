from __future__ import annotations
from pathlib import Path
from typing import Dict, Optional

try:
    import yaml  # type: ignore
except Exception:  # PyYAML optional
    yaml = None

DOCTRINE_ROOT = Path("DOCTRINE/expansion/protocols")

class ProtocolEntry:
    """
    Represents one protocol in the registry.
    state: "active" | "vaulted"
    This minimal slice does NOT provide handlers or invocation logic.
    """
    def __init__(self, name: str, state: str = "vaulted"):
        self.name = name
        self.state = state
        self.lore_path = DOCTRINE_ROOT / name / "lore.md"
        self.policy_path = DOCTRINE_ROOT / name / "policy.yaml"

    def lore(self) -> str:
        if self.lore_path.exists():
            return self.lore_path.read_text(encoding="utf-8")
        return ""

    def policy(self) -> dict:
        if self.policy_path.exists() and yaml:
            try:
                return yaml.safe_load(self.policy_path.read_text(encoding="utf-8")) or {}
            except Exception:
                return {}
        return {}

# Initial placeholder set (expanded in later doctrine slice)
PROTO_NAMES = [
    "SoulEcho",
    "CascadeChainbreaker",
    "CipherSigRelay",
]

REGISTRY: Dict[str, ProtocolEntry] = {
    name: ProtocolEntry(name=name, state="vaulted")
    for name in PROTO_NAMES
}

def list_registry() -> list[dict]:
    """Return registry metadata for API/debug (later route will use this)."""
    return [
        {
            "name": e.name,
            "state": e.state,
            "has_lore": e.lore_path.exists(),
            "has_policy": e.policy_path.exists(),
        }
        for e in sorted(REGISTRY.values(), key=lambda x: x.name.lower())
    ]

def get_entry(name: str) -> Optional[ProtocolEntry]:
    return REGISTRY.get(name)