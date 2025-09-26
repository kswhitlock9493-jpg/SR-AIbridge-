from fastapi.testclient import TestClient
from bridge_backend.main import app
from pathlib import Path
import json

client = TestClient(app)

def test_protocol_seal_creates_artifact(tmp_path: Path, monkeypatch):
    # Redirect vault dir to tmp for isolation
    from bridge_core.protocols import vaulting
    orig_vault_dir = vaulting.VAULT_DIR
    vaulting.VAULT_DIR = tmp_path / "vault/protocols"
    vaulting.VAULT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Call seal endpoint
        r = client.post("/bridge-core/protocols/SoulEcho/seal")
        assert r.status_code == 200
        data = r.json()
        assert data["protocol"] == "SoulEcho"
        assert data["status"] == "sealed"
        assert data["details"]["sealed_via_api"]

        # Verify artifact
        seal_file = vaulting.VAULT_DIR / "SoulEcho" / "seal.json"
        assert seal_file.exists()
        obj = json.loads(seal_file.read_text(encoding="utf-8"))
        assert obj["protocol"] == "SoulEcho"
        assert obj["status"] == "sealed"
    finally:
        vaulting.VAULT_DIR = orig_vault_dir
