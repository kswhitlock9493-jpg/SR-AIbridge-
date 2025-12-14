from fastapi.testclient import TestClient
from bridge_backend.main import app
from pathlib import Path
import json, hashlib

client = TestClient(app)

def sha(t: str) -> str:
    h = hashlib.sha256(); h.update(t.encode()); return h.hexdigest()

def _mk_parser_chunk(tmp_dir: Path, text: str, ts: str = "2025-09-28T00:00:00Z", source: str = "test"):
    # lay down vault/parser files
    parser_dir = tmp_dir / "parser"
    parser_dir.mkdir(parents=True, exist_ok=True)
    ledger = parser_dir / "ledger.jsonl"
    s = sha(text)
    (parser_dir / f"{s}.txt").write_text(text, encoding="utf-8")
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"sha": s, "bytes": len(text), "source": source, "ts": ts}) + "\n")
    return s

def test_truth_find_bind_cite(tmp_path, monkeypatch):
    # point truth + parser dirs at tmp
    monkeypatch.setattr("bridge_backend.bridge_core.engines.truth.utils.TRUTH_DIR", tmp_path / "truth")
    monkeypatch.setattr("bridge_backend.bridge_core.engines.truth.utils.PARSER_DIR", tmp_path / "parser")
    monkeypatch.setattr("bridge_backend.bridge_core.engines.truth.utils.PARSER_LEDGER", tmp_path / "parser" / "ledger.jsonl")
    monkeypatch.setattr("bridge_backend.bridge_core.engines.truth.utils.PARSER_CHUNKS_DIR", tmp_path / "parser")

    # seed parser chunks
    _mk_parser_chunk(tmp_path, "Project Nova is in phase two. Nova started phase two in July.")
    _mk_parser_chunk(tmp_path, "Nova entered phase 2 in July. Phase 2 is underway for Nova.")
    _mk_parser_chunk(tmp_path, "Irrelevant line about something else.")

    # FIND
    r = client.post("/engines/truth/find", json={"query":"Nova", "limit": 10})
    assert r.status_code == 200
    found = r.json()
    assert found["count"] >= 2
    candidates = found["candidates"]

    # BIND
    r = client.post("/engines/truth/bind", json={"candidates": candidates, "similarity": 0.7})
    assert r.status_code == 200
    bound = r.json()
    assert bound["count"] >= 1
    truth_stmt = bound["truths"][0]["statement"]

    # CITE
    r = client.post("/engines/truth/cite", json={"statement": truth_stmt})
    assert r.status_code == 200
    cite_res = r.json()
    assert cite_res["match_score"] >= 0.5
    assert isinstance(cite_res.get("citations", []), list)

    # TRUTHS LIST
    r = client.get("/engines/truth/truths?limit=5")
    assert r.status_code == 200
    lst = r.json()
    assert lst["count"] >= 1
