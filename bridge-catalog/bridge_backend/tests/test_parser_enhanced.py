from fastapi.testclient import TestClient
from bridge_backend.main import app

client = TestClient(app)

RAW = "Alpha para.\n\nBeta para.\n\nGamma para."  # different paragraphs to avoid dedup issues

def test_ingest_and_list_search_and_tag():
    # ingest
    r = client.post("/engines/parser/ingest", json={"raw": RAW, "source": "unit", "max_chunk": 50})  # small chunk size to force multiple chunks
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] and data["seen"] >= 1
    shas = [m["sha"] for m in data["manifest"]]
    assert shas

    # manifest of first sha
    r = client.get(f"/engines/parser/chunk/{shas[0]}")
    assert r.status_code == 200
    man = r.json()["meta"]
    assert man["sha"] == shas[0]

    # tag add
    r = client.post("/engines/parser/tag/add", json={"sha": shas[0], "tags": ["research", "alpha"]})
    assert r.status_code == 200
    assert "alpha" in r.json()["tags"]

    # list by tag
    r = client.get("/engines/parser/list", params={"tag": "alpha"})
    assert r.status_code == 200
    assert any(x["sha"] == shas[0] for x in r.json()["items"])

    # link lineage (parent->child)
    if len(shas) > 1:
        r = client.post("/engines/parser/link", json={"parent_sha": shas[0], "child_sha": shas[1], "relation": "contains"})
        assert r.status_code == 200

    # search substring
    r = client.get("/engines/parser/search", params={"q": "Beta"})
    assert r.status_code == 200
    assert len(r.json()["items"]) >= 1

def test_reassemble_roundtrip():
    # small doc
    r = client.post("/engines/parser/ingest", json={"raw": "One.\n\nTwo.", "source": "roundtrip"})
    shas = [m["sha"] for m in r.json()["manifest"]]
    r = client.post("/engines/parser/reassemble", json={"sha_list": shas})
    assert r.status_code == 200
    txt = r.json()["text"]
    assert "One." in txt and "Two." in txt