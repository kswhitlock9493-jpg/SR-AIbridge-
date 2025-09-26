"""
PR 1A-2f: Add get_entry helper

This module currently provides:
- ProtocolEntry class
- PROTO_NAMES placeholder list
- REGISTRY dict of ProtocolEntry instances
- get_entry(name) helper (added in this slice)

Future planned slices: list_registry(), path attributes, lore/policy integration, activation helpers, handlers, FastAPI routes.
"""

class ProtocolEntry:
    """Minimal placeholder class for a protocol entry."""
    def __init__(self, name: str, state: str = "vaulted"):
        self.name = name
        self.state = state

# Placeholder protocol names (kept small for now)
PROTO_NAMES = [
    "SoulEcho",
    "CascadeChainbreaker",
    "CipherSigRelay",
]

# Global registry mapping protocol name -> ProtocolEntry instance
REGISTRY = {
    name: ProtocolEntry(name=name, state="vaulted")
    for name in PROTO_NAMES
}

def get_entry(name: str) -> "ProtocolEntry | None":
    """Retrieve a protocol by name, or None if missing."""
    return REGISTRY.get(name)

"""End of registry.py after slice 1A-2f"""