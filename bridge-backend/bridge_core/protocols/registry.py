from __future__ import annotations
from pathlib import Path
from typing import Dict

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - graceful degrade if PyYAML missing
    yaml = None

"""
PR 1A-2h: ProtocolEntry lore & policy paths + lore()/policy() helpers.

Provides:
- ProtocolEntry class with lore_path & policy_path
- PROTO_NAMES placeholder list
- REGISTRY dict of ProtocolEntry instances
- get_entry(name) helper
- list_registry() returning metadata including has_lore / has_policy flags
- DOCTRINE_ROOT constant (configurable in tests)

Design notes:
- lore() returns '' if file missing.
- policy() returns parsed YAML dict if file exists and PyYAML available, else {}.
- Safe failure: any YAML parse error -> {}.
"""

# Root where doctrine protocol folders will live
DOCTRINE_ROOT = Path("DOCTRINE/expansion/protocols")

class ProtocolEntry:
    """Represents one protocol in the registry.

    state: "active" | "vaulted"
    Lore + policy assets (optional) live under:
        DOCTRINE/expansion/protocols/<name>/lore.md
        DOCTRINE/expansion/protocols/<name>/policy.yaml
    """
    def __init__(self, name: str, state: str = "vaulted"):
        self.name = name
        self.state = state
        self.lore_path = DOCTRINE_ROOT / name / "lore.md"
        self.policy_path = DOCTRINE_ROOT / name / "policy.yaml"

    # --- Doctrine access helpers -------------------------------------------------
    def lore(self) -> str:
        """Return the lore scroll text if it exists, else empty string."""
        if self.lore_path.exists():
            try:
                return self.lore_path.read_text(encoding="utf-8")
            except Exception:  # pragma: no cover (I/O edge)
                return ""
        return ""

    def policy(self) -> dict:
        """Return parsed YAML policy if present & PyYAML available, else {}."""
        if self.policy_path.exists() and yaml:
            try:
                data = yaml.safe_load(self.policy_path.read_text(encoding="utf-8"))
                return data or {}
            except Exception:  # pragma: no cover (parse errors)
                return {}
        return {}

# Initial placeholder protocols (will expand in later slice)
PROTO_NAMES = [
    "SoulEcho",
    "CascadeChainbreaker",
    "CipherSigRelay",
]

# Global registry mapping protocol name -> ProtocolEntry instance
REGISTRY: Dict[str, ProtocolEntry] = {
    name: ProtocolEntry(name=name, state="vaulted")
    for name in PROTO_NAMES
}

def get_entry(name: str) -> "ProtocolEntry | None":
    """Retrieve a protocol by name, or None if missing."""
    return REGISTRY.get(name)


def list_registry() -> list[dict]:
    """Return metadata (name, state, has_lore, has_policy) for all protocols."""
    return [
        {
            "name": entry.name,
            "state": entry.state,
            "has_lore": entry.lore_path.exists(),
            "has_policy": entry.policy_path.exists(),
        }
        for entry in sorted(REGISTRY.values(), key=lambda e: e.name.lower())
    ]
