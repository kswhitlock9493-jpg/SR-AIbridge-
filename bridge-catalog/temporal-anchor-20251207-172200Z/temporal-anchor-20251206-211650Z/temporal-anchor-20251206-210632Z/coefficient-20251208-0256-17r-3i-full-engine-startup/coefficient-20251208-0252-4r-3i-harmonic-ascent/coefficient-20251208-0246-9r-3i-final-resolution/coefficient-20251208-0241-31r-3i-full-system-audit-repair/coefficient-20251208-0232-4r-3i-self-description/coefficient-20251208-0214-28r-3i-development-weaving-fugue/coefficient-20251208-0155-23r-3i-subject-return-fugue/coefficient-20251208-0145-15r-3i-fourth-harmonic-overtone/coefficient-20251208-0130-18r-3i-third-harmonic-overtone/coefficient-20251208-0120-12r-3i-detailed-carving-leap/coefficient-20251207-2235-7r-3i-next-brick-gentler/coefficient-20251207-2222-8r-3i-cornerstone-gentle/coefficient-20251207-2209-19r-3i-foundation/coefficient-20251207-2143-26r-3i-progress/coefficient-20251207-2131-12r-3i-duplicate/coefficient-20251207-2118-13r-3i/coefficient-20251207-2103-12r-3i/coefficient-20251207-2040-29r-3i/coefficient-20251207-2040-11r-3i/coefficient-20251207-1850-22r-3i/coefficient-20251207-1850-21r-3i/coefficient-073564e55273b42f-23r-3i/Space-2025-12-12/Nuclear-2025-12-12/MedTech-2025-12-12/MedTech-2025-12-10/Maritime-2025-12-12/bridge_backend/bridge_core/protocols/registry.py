from __future__ import annotations
from pathlib import Path
from typing import Dict, Callable, Awaitable, Optional

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - graceful degrade if PyYAML missing
    yaml = None


class ProtocolRegistry:
    """In-memory registry for protocols (swap to DB later)."""

    def __init__(self):
        self._protocols: Dict[str, Dict] = {}

    def add(self, name: str, status: str, details: str = "stub") -> None:
        self._protocols[name] = {
            "name": name,
            "status": status,
            "details": details,
        }

    def list(self) -> list[Dict]:
        return list(self._protocols.values())

    def get(self, name: str) -> Optional[Dict]:
        return self._protocols.get(name)

    def clear(self) -> None:
        self._protocols.clear()


# PR 1A-4d — Protocol Registry Utilities
# New ProtocolEntry class for the registry utility functions
class ProtocolEntry:
    def __init__(self, name: str, state: str = "inactive", details: Optional[dict] = None):
        self.name = name
        self.state = state
        self.details = details or {}

    def activate(self):
        self.state = "active"

    def vault(self):
        self.state = "vaulted"


_registry: Dict[str, ProtocolEntry] = {}


def register_protocol(name: str, details: Optional[dict] = None):
    """Register a new protocol entry into the registry."""
    if name not in _registry:
        _registry[name] = ProtocolEntry(name, "inactive", details)
    return _registry[name]


def get_entry(name: str) -> Optional[ProtocolEntry]:
    return _registry.get(name)


def list_registry() -> list[dict]:
    return [{"name": e.name, "state": e.state, "details": e.details} for e in _registry.values()]


def activate_protocol(name: str) -> bool:
    e = get_entry(name)
    if not e:
        return False
    e.activate()
    return True


def vault_protocol(name: str) -> bool:
    e = get_entry(name)
    if not e:
        return False
    e.vault()
    return True

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

class DoctrineProtocolEntry:
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

# Global registry mapping protocol name -> DoctrineProtocolEntry instance
REGISTRY: Dict[str, DoctrineProtocolEntry] = {
    name: DoctrineProtocolEntry(name=name, state="vaulted")
    for name in PROTO_NAMES
}

async def _default_handler(entry: "DoctrineProtocolEntry", payload: dict) -> dict:
    if entry.state != "active":
        return {"protocol": entry.name, "status": "not_yet_implemented"}
    return {"protocol": entry.name, "status": "ok", "echo": payload}

# Bind default handlers
for _e in REGISTRY.values():
    _e.handler = (lambda entry=_e: (lambda payload: _default_handler(entry, payload)))()

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


def seal(name: str, details: dict = None) -> dict:
    """Seal a protocol (stub implementation)."""
    from .vaulting import seal as vault_seal
    return vault_seal(name, status="sealed", details=details or {})