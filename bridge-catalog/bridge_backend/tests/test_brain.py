"""
Tests for SR-AIbridge Sovereign Brain functionality
"""
import os
import tempfile
import pytest
import json
from datetime import datetime

from bridge_backend.src.brain import BrainLedger, create_brain_ledger
from bridge_backend.src.keys import SovereignKeys, initialize_admiral_keys
from bridge_backend.src.signer import create_signer


class TestBrainLedger:
    """Test the brain ledger functionality"""
    
    @pytest.fixture
    def temp_brain(self):
        """Create a temporary brain ledger for testing"""
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as f:
            db_path = f.name
        
        try:
            brain = create_brain_ledger(db_path)
            yield brain
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.fixture
    def temp_keys(self):
        """Create temporary keys for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            keys = initialize_admiral_keys(temp_dir)
            yield keys
    
    def test_brain_initialization(self, temp_brain):
        """Test brain database initialization"""
        stats = temp_brain.get_statistics()
        
        assert stats['total_memories'] == 0
        assert stats['signed_memories'] == 0
        assert 'brain_metadata' in stats
        assert 'initialized_at' in stats['brain_metadata']
        assert stats['brain_metadata']['version'] == '1.0'
    
    def test_add_memory(self, temp_brain):
        """Test adding memory entries"""
        # Add a simple memory
        entry_id = temp_brain.add_memory(
            content="Test memory content",
            category="test",
            classification="public"
        )
        
        assert entry_id is not None
        assert entry_id > 0
        
        # Verify the memory was added
        memory = temp_brain.get_memory(entry_id)
        assert memory is not None
        assert memory.content == "Test memory content"
        assert memory.category == "test"
        assert memory.classification == "public"
        assert memory.signed_hash is not None  # Should be signed by default
    
    def test_add_memory_with_metadata(self, temp_brain):
        """Test adding memory with custom metadata"""
        metadata = {
            "source": "test_suite",
            "priority": "high",
            "tags": ["test", "metadata"]
        }
        
        entry_id = temp_brain.add_memory(
            content="Memory with metadata",
            category="test",
            classification="private",
            metadata=metadata
        )
        
        memory = temp_brain.get_memory(entry_id)
        stored_metadata = json.loads(memory.metadata)
        
        assert stored_metadata["source"] == "test_suite"
        assert stored_metadata["priority"] == "high"
        assert stored_metadata["tags"] == ["test", "metadata"]
        assert stored_metadata["auto_signed"] is True
    
    def test_add_unsigned_memory(self, temp_brain):
        """Test adding unsigned memory"""
        entry_id = temp_brain.add_memory(
            content="Unsigned test memory",
            sign=False
        )
        
        memory = temp_brain.get_memory(entry_id)
        assert memory.signed_hash is None
        assert memory.signature_data is None
    
    def test_search_memories(self, temp_brain):
        """Test memory search functionality"""
        # Add some test memories
        temp_brain.add_memory("First test memory", "category1", "public")
        temp_brain.add_memory("Second test memory", "category2", "private")
        temp_brain.add_memory("Another memory with keyword", "category1", "public")
        
        # Search by content
        results = temp_brain.search_memories(query="test memory")
        assert len(results) >= 2
        
        # Search by category
        results = temp_brain.search_memories(category="category1")
        assert len(results) == 2
        
        # Search by classification
        results = temp_brain.search_memories(classification="private")
        assert len(results) == 1
        
        # Combined search
        results = temp_brain.search_memories(query="keyword", category="category1")
        assert len(results) == 1
        assert "keyword" in results[0].content
    
    def test_update_memory(self, temp_brain):
        """Test memory updates"""
        # Add initial memory
        entry_id = temp_brain.add_memory("Original content", "original", "public")
        
        # Update content
        success = temp_brain.update_memory(
            entry_id,
            content="Updated content",
            category="updated",
            classification="private"
        )
        
        assert success is True
        
        # Verify update
        memory = temp_brain.get_memory(entry_id)
        assert memory.content == "Updated content"
        assert memory.category == "updated"
        assert memory.classification == "private"
        assert memory.signed_hash is not None  # Should be re-signed
    
    def test_delete_memory(self, temp_brain):
        """Test memory deletion"""
        entry_id = temp_brain.add_memory("Memory to delete", "test", "public")
        
        # Verify it exists
        memory = temp_brain.get_memory(entry_id)
        assert memory is not None
        
        # Delete it
        success = temp_brain.delete_memory(entry_id)
        assert success is True
        
        # Verify it's gone
        memory = temp_brain.get_memory(entry_id)
        assert memory is None
    
    def test_get_categories(self, temp_brain):
        """Test category listing"""
        # Add memories in different categories
        temp_brain.add_memory("Memory 1", "cat1", "public")
        temp_brain.add_memory("Memory 2", "cat1", "public")
        temp_brain.add_memory("Memory 3", "cat2", "public")
        
        categories = temp_brain.get_categories()
        
        # Should have categories with counts
        cat_dict = dict(categories)
        assert cat_dict["cat1"] == 2
        assert cat_dict["cat2"] == 1
    
    def test_export_memories(self, temp_brain):
        """Test memory export"""
        # Add test memories
        temp_brain.add_memory("Export test 1", "export", "public", {"test": True})
        temp_brain.add_memory("Export test 2", "export", "private", {"test": True})
        temp_brain.add_memory("Other memory", "other", "public")
        
        # Export all memories
        export_data = temp_brain.export_memories()
        
        assert export_data["export_type"] == "sovereign_brain_dump"
        assert export_data["memory_count"] == 3
        assert len(export_data["memories"]) == 3
        
        # Export filtered by category
        export_data = temp_brain.export_memories(category="export")
        assert export_data["memory_count"] == 2
        
        # Export without signatures
        export_data = temp_brain.export_memories(include_signatures=False)
        for memory_data in export_data["memories"]:
            assert "signed_hash" not in memory_data
            assert "signature_data" not in memory_data
    
    def test_verify_signatures(self, temp_brain):
        """Test signature verification"""
        # Add signed and unsigned memories
        temp_brain.add_memory("Signed memory", sign=True)
        temp_brain.add_memory("Unsigned memory", sign=False)
        
        results = temp_brain.verify_memory_signatures()
        
        assert results["total_checked"] == 2
        assert results["valid_signatures"] >= 1  # At least one valid
        assert results["unsigned_memories"] >= 1  # At least one unsigned
    
    def test_statistics(self, temp_brain):
        """Test brain statistics"""
        # Add various memories
        temp_brain.add_memory("Memory 1", "cat1", "public")
        temp_brain.add_memory("Memory 2", "cat1", "private", sign=False)
        temp_brain.add_memory("Memory 3", "cat2", "public")
        
        stats = temp_brain.get_statistics()
        
        assert stats["total_memories"] == 3
        assert stats["signed_memories"] == 2  # Two signed memories
        assert stats["unsigned_memories"] == 1  # One unsigned
        assert len(stats["categories"]) == 2
        assert len(stats["classifications"]) == 2
        assert stats["database_size"] > 0


class TestBrainIntegration:
    """Integration tests for brain with keys and signing"""
    
    @pytest.fixture
    def temp_system(self):
        """Create a complete temporary system"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "brain.sqlite")
            key_dir = os.path.join(temp_dir, "keys")
            
            keys = initialize_admiral_keys(key_dir)
            signer = create_signer(key_dir)
            brain = BrainLedger(db_path, signer)
            
            yield {
                "brain": brain,
                "keys": keys,
                "signer": signer,
                "temp_dir": temp_dir,
                "db_path": db_path,
                "key_dir": key_dir
            }
    
    def test_end_to_end_memory_with_signing(self, temp_system):
        """Test complete memory lifecycle with signing"""
        brain = temp_system["brain"]
        
        # Add a signed memory
        entry_id = brain.add_memory(
            content="End-to-end test memory",
            category="integration",
            classification="test",
            metadata={"test_type": "integration"}
        )
        
        # Verify it was signed properly
        memory = brain.get_memory(entry_id)
        assert memory.signed_hash is not None
        assert memory.signature_data is not None
        
        # Verify signatures
        results = brain.verify_memory_signatures()
        assert results["valid_signatures"] == 1
        assert results["invalid_signatures"] == 0
        
        # Export and verify the export includes signature data
        export_data = brain.export_memories(include_signatures=True)
        exported_memory = export_data["memories"][0]
        
        assert "signed_hash" in exported_memory
        assert "signature_data" in exported_memory
    
    def test_key_rotation_impact(self, temp_system):
        """Test how key rotation affects existing signatures"""
        brain = temp_system["brain"]
        keys = temp_system["keys"]
        
        # Add memory with original keys
        entry_id = brain.add_memory("Memory before rotation", sign=True)
        
        # Verify initial signature
        results = brain.verify_memory_signatures()
        assert results["valid_signatures"] == 1
        
        # Rotate keys (simulate by generating new keypair)
        old_keys, new_keys = keys.generate_keypair()
        keys.save_keypair(old_keys, "admiral")
        
        # The old signature should still be valid with the old public key
        # But we can't create new signatures that verify with old keys
        memory = brain.get_memory(entry_id)
        assert memory.signed_hash is not None
        
        # Add new memory with new keys
        new_entry_id = brain.add_memory("Memory after rotation", sign=True)
        new_memory = brain.get_memory(new_entry_id)
        assert new_memory.signed_hash is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])