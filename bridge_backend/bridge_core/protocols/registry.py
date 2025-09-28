from __future__ import annotations
from pathlib import Path
from typing import Dict, Callable, Awaitable, Optional

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - graceful degrade if PyYAML missing
    yaml = None

"""
PR 1A-2h: ProtocolEntry lore & policy paths + lore()/policy() helpers.
PR 1A-2i: Activation helpers (set_state / activate_protocol / vault_protocol)
PR 1A-2j: per-entry handler wiring (async default handlers + invoke delegation)

Provides:
- ProtocolEntry class with lore_path & policy_path
- PROTO_NAMES placeholder list
- REGISTRY dict of ProtocolEntry instances
- get_entry(name) helper
- list_registry() returning metadata including has_lore / has_policy flags
- DOCTRINE_ROOT constant (configurable in tests)
- Activation helpers to toggle protocol state
- Per-entry async handler default (_default_handler) bound at init
- invoke_protocol() delegates to handler

Design notes:
- lore() returns '' if file missing.
- policy() returns parsed YAML dict if file exists and PyYAML available, else {}.
- Safe failure: any YAML parse error -> {}.
- Activation helpers are additive; default state remains 'vaulted'.
- Default handler returns not_yet_implemented unless state is active.
"""

# Root where doctrine protocol folders will live
DOCTRINE_ROOT = Path("DOCTRINE/expansion/protocols")

class ProtocolEntry:
    """Represents one protocol in the registry.

    state: "active" | "vaulted"
    Lore + policy assets (optional) live under:
        DOCTRINE/expansion/protocols/<name>/lore.md
        DOCTRINE/expansion/protocols/<name>/policy.yaml
    handler: async callable(payload: dict) -> dict (default wired)
    """
    def __init__(self,
        name: str,
        state: str = "vaulted",
        handler: Optional[Callable[[dict], Awaitable[dict]]] = None,
    ):
        self.name = name
        self.state = state
        self.lore_path = DOCTRINE_ROOT / name / "lore.md"
        self.policy_path = DOCTRINE_ROOT / name / "policy.yaml"
        self.handler = handler

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

async def _default_handler(entry: "ProtocolEntry", payload: dict) -> dict:
    if entry.state != "active":
        return {"protocol": entry.name, "status": "not_yet_implemented"}
    return {"protocol": entry.name, "status": "ok", "echo": payload}

# Bind default handlers
for _e in REGISTRY.values():
    _e.handler = (lambda entry=_e: (lambda payload: _default_handler(entry, payload)))()

# --- Activation helpers ---------------------------------------------------------

def set_state(name: str, state: str) -> bool:
    """Set the state of a protocol entry. Returns True if successful, False if not found."""
    entry = REGISTRY.get(name)
    if not entry:
        return False
    entry.state = state
    return True


def activate_protocol(name: str) -> bool:
    """Shortcut: mark a protocol as active."""
    return set_state(name, "active")


def vault_protocol(name: str) -> bool:
    """Shortcut: mark a protocol as vaulted."""
    return set_state(name, "vaulted")

# --- Invocation delegation ------------------------------------------------------

async def invoke_protocol(name: str, payload: dict) -> dict:
    """Delegate invocation to the protocol's bound handler.

    Errors:
      - not_found  -> {"error": "not_found"}
      - no_handler -> {"error": "no_handler"} (should not occur in normal flow)
    """
    entry = REGISTRY.get(name)
    if not entry:
        return {"error": "not_found"}
    if not entry.handler:
        return {"error": "no_handler"}
    return await entry.handler(payload)

# --- Missing functions needed by routes.py ---

def get_entry(name: str) -> Optional[ProtocolEntry]:
    """Get a protocol entry by name."""
    return REGISTRY.get(name)

def list_registry() -> list:
    """List all protocols in the registry with metadata."""
    result = []
    for name, entry in REGISTRY.items():
        result.append({
            "name": name,
            "state": entry.state,
            "has_lore": entry.lore_path.exists(),
            "has_policy": entry.policy_path.exists()
        })
    return result

def seal(name: str, details: dict = None) -> dict:
    """Seal a protocol (stub implementation)."""
    from .vaulting import seal as vault_seal
    return vault_seal(name, status="sealed", details=details or {})