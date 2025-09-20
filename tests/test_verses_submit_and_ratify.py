import json
import tempfile
import os
from pathlib import Path
import pytest
from src.guardian_verses import generate_signing_key_hexpair, submit_proposal, sign_message, ratify_proposal, RATIFIED_LINES, PROPOSALS_DIR, TRUST_KEYS

def setup_module(module):
    # ensure test directories exist
    Path("rituals/proposals").mkdir(parents=True, exist_ok=True)
    Path("rituals").mkdir(parents=True, exist_ok=True)
    Path("vault/keys").mkdir(parents=True, exist_ok=True)

def test_submit_and_ratify_roundtrip(tmp_path, monkeypatch):
    # create ephemeral trusted key
    sk_hex, pk_hex = generate_signing_key_hexpair()
    # write trust file with admiral entry
    TRUST_KEYS.write_text(json.dumps({"admiral": pk_hex}))
    # submit proposal
    proposal = {"id": "test-prop-1", "proposer": "prim", "body": "Let the Bridge sing"}
    rec = submit_proposal(proposal)
    assert rec["id"] == "test-prop-1"
    # create signature by ratifier (must sign the canonical message)
    message_bytes = json.dumps({"id": rec["id"], "body": rec["body"], "proposer": rec["proposer"]}).encode("utf-8")
    sig_b64 = sign_message(sk_hex, message_bytes)
    # ratify
    rat = ratify_proposal(rec["id"], pk_hex, sig_b64)
    assert rat["id"] == rec["id"]
    # ratified line exists
    lines = RATIFIED_LINES.read_text(encoding="utf-8").splitlines()
    assert any(json.loads(l)["id"] == rec["id"] for l in lines)

def teardown_module(module):
    # keep artifacts for inspection in dev; don't delete in CI by default
    pass
