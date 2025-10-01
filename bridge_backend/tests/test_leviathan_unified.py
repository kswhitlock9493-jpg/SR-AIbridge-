from fastapi.testclient import TestClient
from bridge_backend.main import app
from pathlib import Path
import json

client = TestClient(app)

def test_unified_search_with_tags(tmp_path, monkeypatch):
    # --- Creativity asset ---
    creat_dir = tmp_path / "creativity"
    creat_dir.mkdir(parents=True, exist_ok=True)
    (creat_dir / "a.json").write_text(json.dumps({
        "sha": "aaa",
        "title": "Dragon Sketch",
        "text": "A concept art piece of a dragon.",
        "tags": ["art", "fantasy"],
        "source": "creativity-test",
        "created_at": "2025-10-01T10:00:00Z",
        "path": "vault/creativity/assets/a.json"
    }), encoding="utf-8")
    monkeypatch.setattr("bridge_backend.bridge_core.engines.creativity.service.ASSETS_DIR", creat_dir)

    # --- Parser ledger + chunk ---
    parser_dir = tmp_path / "parser"
    (parser_dir).mkdir(parents=True, exist_ok=True)
    ledger = parser_dir / "ledger.jsonl"
    ledger.write_text(json.dumps({
        "sha": "psha1",
        "source": "docs/dragon_notes.txt",
        "ts": "2025-10-01T09:00:00Z",
        "tags": ["notes","fantasy"]
    }) + "\n", encoding="utf-8")
    (parser_dir / "psha1.txt").write_text("The dragon sleeps beneath the ruins.", encoding="utf-8")

    monkeypatch.setattr("bridge_backend.bridge_core.engines.truth.utils.PARSER_DIR", parser_dir)
    monkeypatch.setattr("bridge_backend.bridge_core.engines.truth.utils.PARSER_LEDGER", ledger)

    # --- Truths file ---
    truth_dir = tmp_path / "truth"
    truth_dir.mkdir(parents=True, exist_ok=True)
    truths = truth_dir / "truths.jsonl"
    truths.write_text(json.dumps({
        "truth": "Dragons prefer caves.",
        "created_at": "2025-10-01T11:00:00Z",
        "prov": [{"sha":"psha1","source":"docs/dragon_notes.txt","ts":"2025-10-01T09:00:00Z"}],
        "tags": ["lore","fantasy"]
    }) + "\n", encoding="utf-8")
    monkeypatch.setattr("bridge_backend.bridge_core.engines.truth.utils.TRUTH_DIR", truth_dir)

    # reload leviathan to pick up monkeypatched paths
    from importlib import reload
    import bridge_backend.bridge_core.engines.leviathan.service as svc
    reload(svc)
    import bridge_backend.bridge_core.engines.leviathan.routes as routes
    reload(routes)

    test_client = TestClient(app)

    # 1) Plain search (should hit all three planes)
    r = test_client.post("/engines/leviathan/search", json={"query": "dragon"})
    assert r.status_code == 200
    planes = set(row["plane"] for row in r.json()["results"])
    assert {"creativity","parser","truth"} & planes  # at least some of them

    # 2) Tag filter that should still match (fantasy)
    r = test_client.post("/engines/leviathan/search", json={"query": "dragon", "tags": ["fantasy"]})
    assert r.status_code == 200
    data = r.json()["results"]
    assert all("fantasy" in (row.get("tags") or []) for row in data if row["plane"] in ("creativity","parser","truth") and row.get("tags"))

    # 3) Tag filter that should exclude results
    r = test_client.post("/engines/leviathan/search", json={"query": "dragon", "tags": ["sci-fi"]})
    assert r.status_code == 200
    assert r.json()["results"] == []
