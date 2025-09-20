"""
Guardian Verses: proposal submission, ratification, audit ledger.
Uses ed25519 (PyNaCl). Writes ratified verses to rituals/verses.jsonl and custody to vault/custody.scroll
"""

import os
import json
import time
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from nacl.signing import VerifyKey, SigningKey
from nacl.exceptions import BadSignatureError
from threading import Lock

CUSTODY_LOG = Path("vault/custody.scroll")
PROPOSALS_DIR = Path("rituals/proposals")
RATIFIED_LINES = Path("rituals/verses.jsonl")
TRUST_KEYS = Path("vault/keys/trust.json")  # JSON: {"admiral": "<pub_hex>", ...}

os.makedirs(CUSTODY_LOG.parent, exist_ok=True)
os.makedirs(PROPOSALS_DIR, exist_ok=True)
os.makedirs(RATIFIED_LINES.parent, exist_ok=True)
os.makedirs(TRUST_KEYS.parent, exist_ok=True)

_lock = Lock()

def atomic_append_jsonl(path: Path, obj: Dict[str, Any]):
    """Atomic append (POSIX)"""
    line = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o640)
    try:
        os.write(fd, line.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)

def load_trust_keys() -> Dict[str, str]:
    if not TRUST_KEYS.exists():
        return {}
    return json.loads(TRUST_KEYS.read_text(encoding="utf-8"))

def verify_signature(pub_hex: str, message_bytes: bytes, sig_b64: str) -> bool:
    try:
        vk = VerifyKey(bytes.fromhex(pub_hex))
        sig = base64.b64decode(sig_b64)
        vk.verify(message_bytes, sig)  # will raise if invalid
        return True
    except (BadSignatureError, Exception):
        return False

def submit_proposal(proposal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Persist a proposal proposal JSON (unsigned or signed). Must include:
      - id (nonce)
      - body (string)
      - proposer (string id)
      - signature_b64 (optional)
      - pub_hex (optional when signature present)
    """
    ts = time.time()
    proposal_record = {
        "ts": ts,
        "id": proposal.get("id") or f"proposal-{int(ts*1000)}",
        "proposer": proposal.get("proposer"),
        "body": proposal.get("body"),
        "pub_hex": proposal.get("pub_hex"),
        "signature_b64": proposal.get("signature_b64"),
        "status": "submitted"
    }
    # save proposal file (immutable)
    pfile = PROPOSALS_DIR / f"{proposal_record['id']}.json"
    with pfile.open("w", encoding="utf-8") as f:
        json.dump(proposal_record, f, indent=2)
    # custody ledger: proposal submitted
    atomic_append_jsonl(CUSTODY_LOG, {"ts": ts, "action": "proposal_submitted", "id": proposal_record["id"], "proposer": proposal_record["proposer"]})
    return proposal_record

def ratify_proposal(proposal_id: str, ratifier_pub_hex: str, signature_b64: str) -> Dict[str, Any]:
    """
    Ratify a proposal: verify signature by a trusted pub, then append to ratified verses stream.
    - Reject if signature invalid or pub not in trust list.
    - Prevent nonce replays: if the same proposal_id already ratified, reject.
    """
    trust = load_trust_keys()
    # check ratifier is trusted
    if ratifier_pub_hex not in trust.values():
        raise PermissionError("ratifier not trusted")

    # load proposal
    pfile = PROPOSALS_DIR / f"{proposal_id}.json"
    if not pfile.exists():
        raise FileNotFoundError("proposal not found")

    proposal = json.loads(pfile.read_text(encoding="utf-8"))
    message = json.dumps({"id": proposal["id"], "body": proposal["body"], "proposer": proposal["proposer"]}).encode("utf-8")

    # verify signature
    if not verify_signature(ratifier_pub_hex, message, signature_b64):
        raise ValueError("invalid signature")

    # idempotency / nonce replay check: scan ratified lines for this id
    if RATIFIED_LINES.exists():
        for line in RATIFIED_LINES.read_text(encoding="utf-8").splitlines():
            try:
                j = json.loads(line)
                if j.get("id") == proposal_id:
                    raise ValueError("proposal already ratified")
            except Exception:
                continue

    # ratify: append ratified verse
    ratified = {
        "ts": time.time(),
        "id": proposal["id"],
        "body": proposal["body"],
        "proposer": proposal["proposer"],
        "ratifier_pub_hex": ratifier_pub_hex,
        "signature_b64": signature_b64
    }
    _lock.acquire()
    try:
        atomic_append_jsonl(RATIFIED_LINES, ratified)
        atomic_append_jsonl(CUSTODY_LOG, {"ts": ratified["ts"], "action": "proposal_ratified", "id": proposal_id, "ratifier_pub": ratifier_pub_hex})
    finally:
        _lock.release()
    return ratified

# Utility for tests / CLI: generate ephemeral key + sign message
def generate_signing_key_hexpair():
    sk = SigningKey.generate()
    sk_hex = sk.encode().hex()
    pk_hex = sk.verify_key.encode().hex()
    return sk_hex, pk_hex

def sign_message(sk_hex: str, message_bytes: bytes) -> str:
    sk = SigningKey(bytes.fromhex(sk_hex))
    sig = sk.sign(message_bytes).signature
    return base64.b64encode(sig).decode()