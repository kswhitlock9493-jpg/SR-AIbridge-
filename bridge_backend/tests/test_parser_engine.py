from fastapi.testclient import TestClient
from bridge_backend.main import app
import json

client = TestClient(app)

def test_parser_ingest_and_reassemble(tmp_path, monkeypatch):
    # patch vault dir
    monkeypatch.setattr("bridge_backend.bridge_core.engines.parser.service.VAULT_DIR", tmp_path)
    from bridge_backend.bridge_core.engines.parser.service import ParserEngine
    P = ParserEngine(vault=tmp_path)
    monkeypatch.setattr("bridge_backend.bridge_core.engines.parser.routes.P", P)

    text = "Hello world.\n\nThis is a second paragraph."
    r = client.post("/engines/parser/ingest", json={"raw": text, "source": "test"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"]
    assert data["filed"] > 0

    sha_list = [m["sha256"] for m in data["manifest"]]
    r2 = client.post("/engines/parser/reassemble", json={"sha_list": sha_list})
    assert r2.status_code == 200
    text_out = r2.json()["text"]
    assert "Hello world." in text_out