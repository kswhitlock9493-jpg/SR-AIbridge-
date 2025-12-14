from fastapi.testclient import TestClient
from pathlib import Path
from main import app
from bridge_backend.bridge_core.protocols import registry

client = TestClient(app)

def test_lore_and_policy_routes(tmp_path: Path, monkeypatch):
    # Create dummy doctrine files
    d = tmp_path / "DOCTRINE/expansion/protocols/SoulEcho"
    d.mkdir(parents=True)
    (d / "lore.md").write_text("SoulEcho Lore Scroll", encoding="utf-8")
    (d / "policy.yaml").write_text("limits:\n  max: 10", encoding="utf-8")

    # Patch doctrine root
    monkeypatch.setattr(registry, "DOCTRINE_ROOT", tmp_path / "DOCTRINE/expansion/protocols")

    r = client.get("/bridge-core/protocols/SoulEcho/lore")
    assert r.status_code == 200
    assert "Lore" in r.json()["lore"]

    r = client.get("/bridge-core/protocols/SoulEcho/policy")
    assert r.status_code == 200
    pol = r.json()["policy"]
    assert isinstance(pol, dict)
    assert pol.get("limits", {}).get("max") == 10
