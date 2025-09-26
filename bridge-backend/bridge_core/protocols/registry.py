"""PR 1A-2a: bare registry skeleton
Minimal placeholder defining ProtocolEntry only.
Will be expanded in later slices (lists, helpers, handlers, routes).
"""

class ProtocolEntry:
    """
    Minimal placeholder class for a protocol entry.
    Will be expanded in later PRs.
    state: "active" | "vaulted" (string stored directly)
    """
    def __init__(self, name: str, state: str = "vaulted"):
        self.name = name
        self.state = state
