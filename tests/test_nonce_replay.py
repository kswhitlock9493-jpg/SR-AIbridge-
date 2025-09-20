import json
from pathlib import Path
from src.guardian_verses import generate_signing_key_hexpair, submit_proposal, sign_message, ratify_proposal, TRUST_KEYS

def test_replay_blocking(tmp_path):
    sk_hex, pk_hex = generate_signing_key_hexpair()
    TRUST_KEYS.write_text(json.dumps({"admiral": pk_hex}))
    proposal = {"id": "test-prop-replay", "proposer": "prim", "body": "Echo once"}
    rec = submit_proposal(proposal)
    message_bytes = json.dumps({"id": rec["id"], "body": rec["body"], "proposer": rec["proposer"]}).encode("utf-8")
    sig_b64 = sign_message(sk_hex, message_bytes)
    # first ratify ok
    r1 = ratify_proposal(rec["id"], pk_hex, sig_b64)
    assert r1["id"] == rec["id"]
    # second attempt must raise ValueError for "already ratified"
    import pytest
    with pytest.raises(ValueError):
        ratify_proposal(rec["id"], pk_hex, sig_b64)