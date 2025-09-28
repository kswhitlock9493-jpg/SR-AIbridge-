from fastapi.testclient import TestClient
from bridge_backend.main import app
from pathlib import Path

client = TestClient(app)

def test_list_and_browse_vault(tmp_path, monkeypatch):
    vault_root = tmp_path / "vault"
    vault_root.mkdir()
    (vault_root / "foo.txt").write_text("hello", encoding="utf-8")
    subdir = vault_root / "subdir"
    subdir.mkdir()
    (subdir / "bar.txt").write_text("world", encoding="utf-8")

    monkeypatch.setattr("bridge_core.vault.routes.VAULT_ROOT", vault_root)

    # list top-level
    r = client.get("/vault")
    assert r.status_code == 200
    items = r.json()["vault"]
    assert any(i["name"] == "foo.txt" for i in items)

    # browse subdir
    r = client.get("/vault/subdir")
    assert r.status_code == 200
    data = r.json()
    assert any(i["name"] == "bar.txt" for i in data["items"])

    # read file
    r = client.get("/vault/subdir/bar.txt")
    assert r.status_code == 200
    assert "world" in r.json()["content"]

def test_missing_path(monkeypatch, tmp_path):
    vault_root = tmp_path / "vault"
    vault_root.mkdir()
    monkeypatch.setattr("bridge_core.vault.routes.VAULT_ROOT", vault_root)

    r = client.get("/vault/does_not_exist")
    assert r.status_code == 404
