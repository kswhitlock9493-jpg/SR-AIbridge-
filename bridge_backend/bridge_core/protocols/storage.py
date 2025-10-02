from pathlib import Path
import json
from typing import Dict

try:
    from bridge_core.protocols.registry import ProtocolEntry, _registry
    from bridge_core.protocols.vaulting import get_vault_dir
except ImportError:
    from bridge_backend.bridge_core.protocols.registry import ProtocolEntry, _registry
    from bridge_backend.bridge_core.protocols.vaulting import get_vault_dir

VAULT_DIR = get_vault_dir()
VAULT_DIR.mkdir(parents=True, exist_ok=True)
PROTOCOLS_FILE = VAULT_DIR / "protocols.json"

def save_registry():
    data = {
        name: {"state": e.state, "details": e.details}
        for name, e in _registry.items()
    }
    with PROTOCOLS_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_registry():
    if not PROTOCOLS_FILE.exists():
        return
    with PROTOCOLS_FILE.open("r", encoding="utf-8") as f:
        data: Dict[str, dict] = json.load(f)
    _registry.clear()
    for name, meta in data.items():
        _registry[name] = ProtocolEntry(
            name,
            state=meta.get("state", "inactive"),
            details=meta.get("details", {}),
        )