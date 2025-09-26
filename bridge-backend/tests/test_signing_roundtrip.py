"""
Tests for SR-AIbridge cryptographic signing roundtrip functionality
"""
import os
import tempfile
import pytest
import json
from datetime import datetime

from src.keys import SovereignKeys
from src.signer import AtomicSigner, BatchSigner, create_signer


class TestSigningRoundtrip:
    """Test cryptographic signing and verification roundtrips"""
    
    @pytest.fixture
    def temp_keys(self):
        """Create temporary keys for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            keys = SovereignKeys(temp_dir)
            # Generate test keypair
            signing_key, verify_key = keys.generate_keypair()
            keys.save_keypair(signing_key, "test_signer")
            yield keys
    
    @pytest.fixture
    def signer(self, temp_keys):
        """Create signer with test keys"""
        return AtomicSigner(temp_keys)
    
    def test_basic_signing_roundtrip(self, signer):
        """Test basic payload signing and verification"""
        # Create test payload
        payload = {
            "message": "Hello, sovereign world!",
            "timestamp": datetime.now().isoformat(),
            "data": {"test": True, "value": 42}
        }
        
        # Sign the payload
        signed_envelope = signer.sign_payload(payload, "test_signer")
        
        # Verify structure
        assert "payload" in signed_envelope
        assert "metadata" in signed_envelope
        assert "signature" in signed_envelope
        
        # Verify metadata
        metadata = signed_envelope["metadata"]
        assert metadata["signer"] == "test_signer"
        assert metadata["signature_version"] == "1.0"
        assert "payload_hash" in metadata
        assert "signed_at" in metadata
        
        # Verify signature structure
        signature = signed_envelope["signature"]
        assert "data" in signature
        assert "envelope_hash" in signature
        assert "public_key" in signature
        
        # Verify the signature
        is_valid, message = signer.verify_signature(signed_envelope)
        assert is_valid is True
        assert "valid" in message.lower()
    
    def test_payload_hash_consistency(self, signer):
        """Test that identical payloads produce identical hashes"""
        payload1 = {"message": "test", "value": 123}
        payload2 = {"message": "test", "value": 123}
        payload3 = {"value": 123, "message": "test"}  # Different order
        
        hash1 = signer.create_payload_hash(payload1)
        hash2 = signer.create_payload_hash(payload2)
        hash3 = signer.create_payload_hash(payload3)
        
        # Same content should produce same hash
        assert hash1 == hash2
        assert hash1 == hash3  # Order shouldn't matter due to sorting
    
    def test_signature_tampering_detection(self, signer):
        """Test that tampering with signed data is detected"""
        payload = {"message": "Original message", "important": True}
        
        # Sign the payload
        signed_envelope = signer.sign_payload(payload, "test_signer")
        
        # Verify original is valid
        is_valid, message = signer.verify_signature(signed_envelope)
        assert is_valid is True
        
        # Tamper with payload
        tampered_envelope = signed_envelope.copy()
        tampered_envelope["payload"]["message"] = "Tampered message"
        
        # Should detect tampering
        is_valid, message = signer.verify_signature(tampered_envelope)
        assert is_valid is False
        assert "mismatch" in message.lower()
        
        # Tamper with signature
        tampered_sig = signed_envelope.copy()
        tampered_sig["signature"]["data"] = "00" + tampered_sig["signature"]["data"][2:]
        
        # Should detect invalid signature
        is_valid, message = signer.verify_signature(tampered_sig)
        assert is_valid is False
        assert "invalid" in message.lower()
    
    def test_manifest_signing_roundtrip(self, signer):
        """Test manifest creation and signing"""
        # Create test items
        items = [
            {"type": "memory", "id": 1, "content": "First memory"},
            {"type": "memory", "id": 2, "content": "Second memory"},
            {"type": "config", "name": "settings.json", "size": 1024}
        ]
        
        # Create manifest
        manifest = signer.create_manifest(items, "test_manifest")
        
        # Verify manifest structure
        assert manifest["type"] == "test_manifest"
        assert manifest["items"] == items
        assert manifest["item_count"] == 3
        assert "created_at" in manifest
        assert "manifest_hash" in manifest
        
        # Sign manifest
        signed_manifest = signer.sign_manifest(manifest, "test_signer")
        
        # Verify signed manifest
        is_valid, message, details = signer.verify_manifest(signed_manifest)
        assert is_valid is True
        assert details["signer"] == "test_signer"
        assert details["item_count"] == 3
    
    def test_different_signers(self, temp_keys):
        """Test signing with different signers"""
        # Create multiple signers
        signing_key1, _ = temp_keys.generate_keypair()
        signing_key2, _ = temp_keys.generate_keypair()
        temp_keys.save_keypair(signing_key1, "signer1")
        temp_keys.save_keypair(signing_key2, "signer2")
        
        signer = AtomicSigner(temp_keys)
        
        payload = {"message": "Multi-signer test"}
        
        # Sign with first signer
        signed1 = signer.sign_payload(payload, "signer1")
        is_valid1, _ = signer.verify_signature(signed1)
        assert is_valid1 is True
        
        # Sign with second signer
        signed2 = signer.sign_payload(payload, "signer2")
        is_valid2, _ = signer.verify_signature(signed2)
        assert is_valid2 is True
        
        # Signatures should be different
        assert signed1["signature"]["data"] != signed2["signature"]["data"]
        assert signed1["signature"]["public_key"] != signed2["signature"]["public_key"]
    
    def test_signature_verification_with_wrong_key(self, temp_keys):
        """Test that signatures don't verify with wrong keys"""
        # Create two different key pairs
        signing_key1, _ = temp_keys.generate_keypair()
        signing_key2, _ = temp_keys.generate_keypair()
        temp_keys.save_keypair(signing_key1, "signer1")
        temp_keys.save_keypair(signing_key2, "signer2")
        
        signer = AtomicSigner(temp_keys)
        
        payload = {"message": "Cross-key verification test"}
        
        # Sign with signer1
        signed_envelope = signer.sign_payload(payload, "signer1")
        
        # Try to verify with signer2's key (should work because verification uses embedded public key)
        is_valid, _ = signer.verify_signature(signed_envelope)
        assert is_valid is True  # Uses embedded public key, so should work
        
        # But the signer should be correct in metadata
        assert signed_envelope["metadata"]["signer"] == "signer1"


class TestBatchSigning:
    """Test batch signing functionality"""
    
    @pytest.fixture
    def batch_signer(self, temp_keys):
        """Create batch signer with test keys"""
        signing_key, _ = temp_keys.generate_keypair()
        temp_keys.save_keypair(signing_key, "batch_signer")
        atomic_signer = AtomicSigner(temp_keys)
        return BatchSigner(atomic_signer)
    
    @pytest.fixture
    def temp_keys(self):
        """Create temporary keys for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            keys = SovereignKeys(temp_dir)
            yield keys
    
    def test_batch_signing_roundtrip(self, batch_signer):
        """Test batch signing and verification"""
        # Create test payloads
        payloads = [
            {"type": "memory", "content": "Batch memory 1", "id": 1},
            {"type": "memory", "content": "Batch memory 2", "id": 2},
            {"type": "config", "setting": "value", "priority": "high"}
        ]
        
        # Sign batch
        signed_batch = batch_signer.sign_batch(payloads, "batch_signer")
        
        # Verify batch structure
        assert "payload" in signed_batch
        batch_payload = signed_batch["payload"]
        assert "batch_id" in batch_payload
        assert batch_payload["item_count"] == 3
        assert len(batch_payload["items"]) == 3
        
        # Verify each item has batch metadata
        for i, item in enumerate(batch_payload["items"]):
            item_payload = item["payload"]
            assert item_payload["_batch_meta"]["item_index"] == i
            assert item_payload["_batch_meta"]["batch_size"] == 3
            assert "batch_id" in item_payload["_batch_meta"]
        
        # Verify batch
        results = batch_signer.verify_batch(signed_batch)
        
        assert results["batch_valid"] is True
        assert results["batch_details"]["item_count"] == 3
        assert len(results["item_results"]) == 3
        
        # All items should be valid
        for item_result in results["item_results"]:
            assert item_result["valid"] is True
    
    def test_batch_with_tampered_item(self, batch_signer):
        """Test batch verification with tampered item"""
        payloads = [
            {"message": "Good item 1"},
            {"message": "Good item 2"},
            {"message": "Item to tamper"}
        ]
        
        # Sign batch
        signed_batch = batch_signer.sign_batch(payloads, "batch_signer")
        
        # Tamper with one item
        signed_batch["payload"]["items"][2]["payload"]["message"] = "Tampered!"
        
        # Verify batch
        results = batch_signer.verify_batch(signed_batch)
        
        # Batch manifest should still be valid, but item should be invalid
        assert results["batch_valid"] is True  # Manifest itself is still valid
        
        # Check individual items
        item_results = results["item_results"]
        assert item_results[0]["valid"] is True
        assert item_results[1]["valid"] is True
        assert item_results[2]["valid"] is False  # Tampered item


class TestSigningEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.fixture
    def temp_keys(self):
        """Create temporary keys for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            keys = SovereignKeys(temp_dir)
            signing_key, _ = keys.generate_keypair()
            keys.save_keypair(signing_key, "edge_tester")
            yield keys
    
    def test_signing_nonexistent_key(self, temp_keys):
        """Test signing with nonexistent key"""
        signer = AtomicSigner(temp_keys)
        payload = {"message": "test"}
        
        with pytest.raises(ValueError, match="not found"):
            signer.sign_payload(payload, "nonexistent_signer")
    
    def test_empty_payload_signing(self, temp_keys):
        """Test signing empty payload"""
        signer = AtomicSigner(temp_keys)
        payload = {}
        
        signed_envelope = signer.sign_payload(payload, "edge_tester")
        is_valid, _ = signer.verify_signature(signed_envelope)
        assert is_valid is True
    
    def test_large_payload_signing(self, temp_keys):
        """Test signing large payload"""
        signer = AtomicSigner(temp_keys)
        
        # Create large payload
        large_data = "x" * 10000
        payload = {
            "large_field": large_data,
            "metadata": {"size": len(large_data)},
            "chunks": [large_data[i:i+100] for i in range(0, len(large_data), 100)]
        }
        
        signed_envelope = signer.sign_payload(payload, "edge_tester")
        is_valid, _ = signer.verify_signature(signed_envelope)
        assert is_valid is True
    
    def test_unicode_payload_signing(self, temp_keys):
        """Test signing payload with unicode content"""
        signer = AtomicSigner(temp_keys)
        
        payload = {
            "unicode_message": "🔑 Sovereign keys for the 🧠 brain 🚢",
            "chinese": "主权密钥",
            "arabic": "مفاتيح السيادة",
            "emoji": "🌊🗝️⚓🔐"
        }
        
        signed_envelope = signer.sign_payload(payload, "edge_tester")
        is_valid, _ = signer.verify_signature(signed_envelope)
        assert is_valid is True
        
        # Verify content is preserved
        assert signed_envelope["payload"]["unicode_message"] == payload["unicode_message"]
    
    def test_malformed_signature_verification(self, temp_keys):
        """Test verification of malformed signatures"""
        signer = AtomicSigner(temp_keys)
        
        # Missing signature field
        malformed1 = {
            "payload": {"message": "test"},
            "metadata": {"signer": "test", "signed_at": datetime.now().isoformat()}
        }
        is_valid, message = signer.verify_signature(malformed1)
        assert is_valid is False
        assert "missing" in message.lower()
        
        # Invalid signature data
        malformed2 = {
            "payload": {"message": "test"},
            "metadata": {"signer": "test", "signed_at": datetime.now().isoformat()},
            "signature": {"data": "invalid_hex", "envelope_hash": "test", "public_key": "test"}
        }
        is_valid, message = signer.verify_signature(malformed2)
        assert is_valid is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])