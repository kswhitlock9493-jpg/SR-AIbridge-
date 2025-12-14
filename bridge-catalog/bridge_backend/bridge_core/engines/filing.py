import os, json, hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any

VAULT_DIR = "vault/filing"
LEDGER_PATH = os.path.join(VAULT_DIR, "ledger.jsonl")

class FilingEngine:
    def __init__(self):
        os.makedirs(VAULT_DIR, exist_ok=True)
        if not os.path.exists(LEDGER_PATH):
            open(LEDGER_PATH, "a").close()

    def file_entry(self, content: str, tags: List[str], source: str) -> Dict[str, Any]:
        """Store an entry with metadata and dedup detection."""
        sha = hashlib.sha256(content.encode()).hexdigest()
        path = os.path.join(VAULT_DIR, f"{sha}.txt")

        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

        ledger_entry = {
            "sha": sha,
            "tags": tags,
            "source": source,
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "bytes": len(content.encode()),
        }
        with open(LEDGER_PATH, "a", encoding="utf-8") as log:
            log.write(json.dumps(ledger_entry) + "\n")

        return ledger_entry

    def search_entries(self, tag: str) -> List[Dict[str, Any]]:
        """Return all ledger entries matching a tag."""
        results = []
        with open(LEDGER_PATH, encoding="utf-8") as log:
            for line in log:
                entry = json.loads(line)
                if tag in entry["tags"]:
                    results.append(entry)
        return results

    def reassemble(self, shas: List[str]) -> str:
        """Recombine filed content by list of hashes."""
        parts = []
        for sha in shas:
            path = os.path.join(VAULT_DIR, f"{sha}.txt")
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    parts.append(f.read())
        return "\n\n".join(parts)