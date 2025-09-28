from pathlib import Path
from bridge_backend.bridge_core.protocols import registry

def test_list_registry_flags(tmp_path: Path):
    # Create a fake doctrine directory containing only lore.md for CipherSigRelay
    doctrine_dir = tmp_path / "DOCTRINE" / "expansion" / "protocols" / "CipherSigRelay"
    doctrine_dir.mkdir(parents=True)
    (doctrine_dir / "lore.md").write_text("cipher lore", encoding="utf-8")

    # Monkeypatch DOCTRINE_ROOT so new ProtocolEntry objects point to our temp paths
    original_root = registry.DOCTRINE_ROOT
    registry.DOCTRINE_ROOT = tmp_path / "DOCTRINE" / "expansion" / "protocols"

    try:
        # Rebuild just the CipherSigRelay entry so its paths reflect the monkeypatched root
        registry.REGISTRY["CipherSigRelay"] = registry.ProtocolEntry("CipherSigRelay")

        items = registry.list_registry()
        cipher_meta = next(i for i in items if i["name"] == "CipherSigRelay")
        assert cipher_meta["has_lore"] is True      # lore.md exists
        assert cipher_meta["has_policy"] is False    # no policy.yaml present
    finally:
        # Restore original root to avoid side effects on other tests
        registry.DOCTRINE_ROOT = original_root
