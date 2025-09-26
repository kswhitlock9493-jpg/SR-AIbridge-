from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

VAULT_DIR = Path("vault") / "protocols"
VAULT_DIR.mkdir(parents=True, exist_ok=True)

def seal(protocol_name: str, status: str = "sealed", details: dict | None = None) -> dict:
    """
    Write a minimal, auditable seal artifact for a protocol invocation or status.
    Creates:
      vault/protocols/<name>/
        - lore_applied.txt (latest timestamp marker)
        - seal.json        (latest seal snapshot)
    """
    stamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    root = VAULT_DIR / protocol_name
    root.mkdir(parents=True, exist_ok=True)

    (root / "lore_applied.txt").write_text(
        f"{protocol_name} :: {status} @ {stamp}\n", encoding="utf-8"
    )

    seal_obj = {
        "protocol": protocol_name,
        "status": status,
        "timestamp": stamp,
        "details": details or {},
    }
    (root / "seal.json").write_text(json.dumps(seal_obj, indent=2), encoding="utf-8")
    return seal_obj
