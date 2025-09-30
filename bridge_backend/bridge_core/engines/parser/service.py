from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

VAULT_DIR = Path("vault") / "parser"
VAULT_DIR.mkdir(parents=True, exist_ok=True)

def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"

def _sha256_text(txt: str) -> str:
    h = hashlib.sha256(); h.update(txt.encode("utf-8", "ignore"))
    return h.hexdigest()

class ParserEngine:
    """
    Universal parsing + filing engine.
    - Tokenizes or chunks raw input.
    - Deduplicates using SHA256 fingerprints.
    - Files into vault/ with lineage + metadata.
    - Recombines coherent blocks when retrieved.
    """

    def __init__(self, vault: Path = VAULT_DIR):
        self.vault = vault
        self.ledger = self.vault / "ledger.jsonl"
        self.vault.mkdir(parents=True, exist_ok=True)

    def _append_ledger(self, entry: Dict[str, Any]) -> None:
        with self.ledger.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def parse_and_file(self, raw: str, source: str = "unknown") -> Dict[str, Any]:
        """
        Break down raw text, deduplicate, and file.
        Returns a manifest summary.
        """
        chunks = self._chunk(raw)
        seen, filed = 0, 0
        manifest = []
        for ch in chunks:
            digest = _sha256_text(ch)
            seen += 1
            out_path = self.vault / f"{digest}.txt"
            if out_path.exists():
                continue  # dedup skip
            out_path.write_text(ch, encoding="utf-8")
            filed += 1
            entry = {
                "sha256": digest,
                "path": str(out_path),
                "source": source,
                "ts": _now(),
                "bytes": len(ch.encode("utf-8", "ignore"))
            }
            manifest.append(entry)
            self._append_ledger(entry)
        return {"ok": True, "seen": seen, "filed": filed, "manifest": manifest}

    def _chunk(self, raw: str, size: int = 2000) -> List[str]:
        """
        Very simple chunker: break by paragraphs / size.
        """
        paras = re.split(r"\n\s*\n", raw)
        chunks = []
        for p in paras:
            if not p.strip():
                continue
            if len(p) <= size:
                chunks.append(p.strip())
            else:
                for i in range(0, len(p), size):
                    chunks.append(p[i:i+size])
        return chunks

    def reassemble(self, sha_list: List[str]) -> str:
        """
        Recombine previously filed chunks.
        """
        blocks = []
        for sha in sha_list:
            path = self.vault / f"{sha}.txt"
            if path.exists():
                blocks.append(path.read_text(encoding="utf-8"))
        return "\n\n".join(blocks)