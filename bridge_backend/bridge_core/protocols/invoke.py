from pathlib import Path
from datetime import datetime, timezone
import json
from .registry import get_entry

VAULT_PROTOCOLS = Path("vault") / "protocols"
VAULT_PROTOCOLS.mkdir(parents=True, exist_ok=True)

def _seal_path(name: str) -> Path:
    """Return the path to this protocol's seal file."""
    return VAULT_PROTOCOLS / f"{name}_seal.json"

def invoke_protocol(name: str, payload: dict) -> dict:
    """
    Attempt to invoke a protocol. If active → record success.
    If vaulted → record as no-op but still seal.
    Always appends a seal artifact in vault.
    """
    entry = get_entry(name)
    if not entry:
        return {"error": "protocol_not_found"}

    ts = datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"
    seal = {
        "protocol": name,
        "timestamp": ts,
        "state": entry.state,
        "payload": payload,
    }

    # Write/append to seal file
    seal_file = _seal_path(name)
    if seal_file.exists():
        with seal_file.open("r", encoding="utf-8") as f:
            seals = json.load(f)
    else:
        seals = []

    seals.append(seal)
    with seal_file.open("w", encoding="utf-8") as f:
        json.dump(seals, f, indent=2)

    # Return a runtime response
    if entry.state == "active":
        return {"status": "invoked", "seal": seal}
    else:
        return {"status": "vaulted", "seal": seal}