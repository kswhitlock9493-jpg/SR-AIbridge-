from fastapi.testclient import TestClient
from pathlib import Path
import json
from importlib import reload
import tempfile
import pytest

def test_ingest_and_search_with_tags(tmp_path, monkeypatch):
    """Test ingesting and searching creative assets with tag filtering"""
    # Setup isolated vault directory
    from importlib import reload
    import bridge_core.engines.creativity.service as svc
    monkeypatch.setattr("bridge_core.engines.creativity.service.CREATIVITY_DIR", tmp_path)
    monkeypatch.setattr("bridge_core.engines.creativity.service.ASSETS_DIR", tmp_path)
    reload(svc)
    import bridge_core.engines.creativity.routes as routes
    reload(routes)
    from bridge_backend.main import app
    test_client = TestClient(app)

    # Ingest an asset with tags
    payload = {"title": "Test Poem", "text": "The stars sing tonight", "tags": ["poetry", "story"], "source": "test"}
    r = test_client.post("/engines/creativity/ingest", json=payload)
    assert r.status_code == 200
    assert r.json()["ok"] == True
    sha = r.json()["asset"]["sha"]
    
    # Verify metadata file was created
    meta_file = tmp_path / f"{sha}.json"
    txt_file = tmp_path / f"{sha}.txt"
    assert meta_file.exists()
    assert txt_file.exists()
    
    # Verify metadata content
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    assert meta["title"] == "Test Poem"
    assert meta["text"] == "The stars sing tonight"
    assert "poetry" in meta["tags"]
    assert "story" in meta["tags"]
    assert meta["source"] == "test"

    # Search by keyword only
    r = test_client.post("/engines/creativity/search", json={"query": "stars"})
    assert r.status_code == 200
    results = r.json()["results"]
    assert any(res["sha"] == sha for res in results)

    # Search by keyword + tag filter
    r = test_client.post("/engines/creativity/search", json={"query": "stars", "tags": ["poetry"]})
    assert r.status_code == 200
    results = r.json()["results"]
    assert any("poetry" in res["tags"] for res in results)
    
    # Search with tag that doesn't match
    r = test_client.post("/engines/creativity/search", json={"query": "stars", "tags": ["nonexistent"]})
    assert r.status_code == 200
    results = r.json()["results"]
    assert len(results) == 0  # Should not find any results

def test_ingest_multiple_assets_and_filter(tmp_path, monkeypatch):
    """Test ingesting multiple assets and filtering by tags"""
    from importlib import reload
    import bridge_core.engines.creativity.service as svc
    monkeypatch.setattr("bridge_core.engines.creativity.service.CREATIVITY_DIR", tmp_path)
    monkeypatch.setattr("bridge_core.engines.creativity.service.ASSETS_DIR", tmp_path)
    reload(svc)
    import bridge_core.engines.creativity.routes as routes
    reload(routes)
    from bridge_backend.main import app
    test_client = TestClient(app)

    # Ingest multiple assets
    payloads = [
        {"title": "Dragon Tale", "text": "A dragon flies over mountains", "tags": ["fantasy", "dragon"], "source": "test1"},
        {"title": "Space Adventure", "text": "Stars twinkle in the cosmos", "tags": ["scifi", "space"], "source": "test2"},
        {"title": "Dragon Comic", "text": "A dragon breathes fire", "tags": ["comic", "dragon"], "source": "test3"}
    ]
    
    for payload in payloads:
        r = test_client.post("/engines/creativity/ingest", json=payload)
        assert r.status_code == 200
    
    # Search for "dragon" with "comic" tag - should find only Dragon Comic
    r = test_client.post("/engines/creativity/search", json={"query": "dragon", "tags": ["comic"]})
    assert r.status_code == 200
    results = r.json()["results"]
    assert len(results) == 1
    assert results[0]["title"] == "Dragon Comic"
    
    # Search for "dragon" without tag filter - should find both dragon entries
    r = test_client.post("/engines/creativity/search", json={"query": "dragon"})
    assert r.status_code == 200
    results = r.json()["results"]
    assert len(results) == 2
