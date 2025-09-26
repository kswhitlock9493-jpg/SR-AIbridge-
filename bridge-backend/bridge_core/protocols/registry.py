"""
SR-AIbridge Protocol Registry

Slice PR 1A-2e: Add placeholder PROTO_NAMES and global REGISTRY.
Incremental path so far:
  - 1A-2a/2c: ProtocolEntry class only
  - 1A-2d: (intended) PROTO_NAMES list (now included here if it had not landed)
  - 1A-2e: REGISTRY dict of ProtocolEntry objects
Future slices will add helper functions (get_entry, list_registry), lore/policy paths, handlers, and FastAPI routes.
"""

class ProtocolEntry:
    """Minimal placeholder class for a protocol entry.
    state: 'vaulted' | 'active' (strings only for now)
    """
    def __init__(self, name: str, state: str = "vaulted"):
        self.name = name
        self.state = state

# Initial placeholder protocols (doctrine expansion comes later)
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

# NOTE: No helper functions yet (get_entry, list_registry) by design in this slice.
# Tests for this slice should only assert the existence and shape of REGISTRY.

"""End of registry.py for slice 1A-2e"""