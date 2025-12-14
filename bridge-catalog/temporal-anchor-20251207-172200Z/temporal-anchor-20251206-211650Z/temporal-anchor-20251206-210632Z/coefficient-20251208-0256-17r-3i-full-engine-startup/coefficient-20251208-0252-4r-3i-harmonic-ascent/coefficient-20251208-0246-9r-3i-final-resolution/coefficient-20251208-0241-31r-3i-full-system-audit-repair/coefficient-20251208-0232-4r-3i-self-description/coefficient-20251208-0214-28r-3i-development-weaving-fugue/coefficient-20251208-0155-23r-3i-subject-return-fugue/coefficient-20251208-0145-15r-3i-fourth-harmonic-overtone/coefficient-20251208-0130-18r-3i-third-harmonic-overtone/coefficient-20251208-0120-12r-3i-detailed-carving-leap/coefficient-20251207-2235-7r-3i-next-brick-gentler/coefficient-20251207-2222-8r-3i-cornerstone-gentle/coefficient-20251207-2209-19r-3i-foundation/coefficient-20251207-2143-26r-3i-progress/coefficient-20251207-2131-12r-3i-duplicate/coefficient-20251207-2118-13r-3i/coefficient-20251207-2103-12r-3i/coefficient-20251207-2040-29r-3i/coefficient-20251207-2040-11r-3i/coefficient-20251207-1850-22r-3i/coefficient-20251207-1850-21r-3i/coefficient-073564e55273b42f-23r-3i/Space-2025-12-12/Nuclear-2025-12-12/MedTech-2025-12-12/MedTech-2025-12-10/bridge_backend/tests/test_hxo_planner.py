"""
Tests for HXO Core Functionality
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, UTC
import tempfile
import shutil
from pathlib import Path
import asyncio

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.hypshard_x.models import (
    HXOPlan, HXOStage, ShardSpec, ShardResult, ShardPhase,
    ExecutorType, PartitionerType, SchedulerType
)
from engines.hypshard_x.core import HXOCore
from engines.hypshard_x.merkle import MerkleTree


class TestHXOPlanner(unittest.TestCase):
    """Test HXO plan creation and CAS ID computation"""
    
    def test_cas_id_computation(self):
        """Test that CAS IDs are deterministic"""
        inputs1 = {"file": "test.py", "size": 100}
        inputs2 = {"file": "test.py", "size": 100}
        
        cas_id1 = ShardSpec.compute_cas_id("stage1", "pack_backend", inputs1, [])
        cas_id2 = ShardSpec.compute_cas_id("stage1", "pack_backend", inputs2, [])
        
        self.assertEqual(cas_id1, cas_id2, "CAS IDs should be deterministic")
    
    def test_cas_id_uniqueness(self):
        """Test that different inputs produce different CAS IDs"""
        inputs1 = {"file": "test1.py", "size": 100}
        inputs2 = {"file": "test2.py", "size": 100}
        
        cas_id1 = ShardSpec.compute_cas_id("stage1", "pack_backend", inputs1, [])
        cas_id2 = ShardSpec.compute_cas_id("stage1", "pack_backend", inputs2, [])
        
        self.assertNotEqual(cas_id1, cas_id2, "Different inputs should produce different CAS IDs")
    
    def test_plan_creation(self):
        """Test HXO plan creation"""
        stage = HXOStage(
            id="pack_backend",
            kind="deploy.pack",
            slo_ms=120000,
            partitioner=PartitionerType.BY_FILESIZE,
            executor=ExecutorType.PACK_BACKEND
        )
        
        plan = HXOPlan(
            plan_id="test-plan-1",
            name="test_plan",
            stages=[stage],
            constraints={"max_shards": 1000}
        )
        
        self.assertEqual(plan.plan_id, "test-plan-1")
        self.assertEqual(len(plan.stages), 1)
        self.assertEqual(plan.get_max_shards(), 1000)


class TestHXOMerkleTree(unittest.TestCase):
    """Test Merkle tree aggregation and proofs"""
    
    def test_merkle_single_leaf(self):
        """Test Merkle tree with single leaf"""
        tree = MerkleTree("test-plan")
        
        result = ShardResult(
            cas_id="shard1",
            success=True,
            output_digest="abc123",
            started_at=datetime.now(UTC),
            finished_at=datetime.now(UTC),
            attempt=0
        )
        
        tree.add_leaf(result)
        root = tree.compute_root()
        
        self.assertIsNotNone(root)
        self.assertIsInstance(root, str)
    
    def test_merkle_multiple_leaves(self):
        """Test Merkle tree with multiple leaves"""
        tree = MerkleTree("test-plan")
        
        for i in range(5):
            result = ShardResult(
                cas_id=f"shard{i}",
                success=True,
                output_digest=f"digest{i}",
                started_at=datetime.now(UTC),
                finished_at=datetime.now(UTC),
                attempt=0
            )
            tree.add_leaf(result)
        
        root = tree.compute_root()
        
        self.assertIsNotNone(root)
        self.assertEqual(len(tree.leaves), 5)
    
    def test_merkle_proof_generation(self):
        """Test Merkle proof generation"""
        tree = MerkleTree("test-plan")
        
        for i in range(4):
            result = ShardResult(
                cas_id=f"shard{i}",
                success=True,
                output_digest=f"digest{i}",
                started_at=datetime.now(UTC),
                finished_at=datetime.now(UTC),
                attempt=0
            )
            tree.add_leaf(result)
        
        tree.compute_root()
        
        # Generate proof for first shard
        proof = tree.generate_proof("shard0")
        
        self.assertIsNotNone(proof)
        self.assertEqual(proof.leaf_cas_id, "shard0")
        
        # Verify proof
        is_valid = tree.verify_proof(proof)
        self.assertTrue(is_valid, "Generated proof should be valid")


class TestHXOCore(unittest.TestCase):
    """Test HXO core orchestration"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.hxo = HXOCore(vault_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_submit_plan(self):
        """Test plan submission"""
        async def run_test():
            stage = HXOStage(
                id="pack_backend",
                kind="deploy.pack",
                slo_ms=120000,
                partitioner=PartitionerType.BY_MODULE,
                executor=ExecutorType.PACK_BACKEND,
                config={"modules": ["module_a", "module_b"]}
            )
            
            plan = HXOPlan(
                plan_id="test-plan-1",
                name="test_plan",
                stages=[stage],
                constraints={"max_shards": 100}
            )
            
            # Submit plan
            plan_id = await self.hxo.submit_plan(plan)
            
            self.assertEqual(plan_id, "test-plan-1")
            self.assertIn(plan_id, self.hxo.active_plans)
            
            # Wait a bit for shard creation
            await asyncio.sleep(0.5)
            
            # Check status
            status = await self.hxo.get_status(plan_id)
            
            self.assertIsNotNone(status)
            self.assertEqual(status.plan_id, plan_id)
            self.assertGreater(status.total_shards, 0)
        
        asyncio.run(run_test())


class TestHXOAdapters(unittest.TestCase):
    """Test HXO adapter integrations"""
    
    def test_blueprint_validation(self):
        """Test Blueprint validation"""
        from bridge_core.engines.adapters.hxo_blueprint_link import validate_stage
        
        # Valid stage
        stage_data = {
            "id": "pack_backend",
            "kind": "deploy.pack",
            "partitioner": "by_filesize",
            "executor": "pack_backend"
        }
        
        is_valid, error = validate_stage(stage_data)
        self.assertTrue(is_valid, f"Stage should be valid: {error}")
        
        # Invalid partitioner
        stage_data_invalid = {
            "id": "pack_backend",
            "kind": "deploy.pack",
            "partitioner": "invalid_partitioner",
            "executor": "pack_backend"
        }
        
        is_valid, error = validate_stage(stage_data_invalid)
        self.assertFalse(is_valid, "Invalid partitioner should fail validation")
    
    def test_parser_plan_spec(self):
        """Test Parser plan spec parsing"""
        from bridge_core.engines.adapters.hxo_parser_link import parse_plan_spec
        
        async def run_test():
            spec = {
                "name": "test_deploy",
                "stages": [
                    {"id": "pack", "kind": "deploy.pack"},
                    {"id": "migrate", "kind": "deploy.migrate"}
                ],
                "constraints": {"max_shards": 1000}
            }
            
            plan_data = await parse_plan_spec(spec)
            
            self.assertEqual(plan_data["name"], "test_deploy")
            self.assertEqual(len(plan_data["stages"]), 2)
            self.assertEqual(plan_data["constraints"]["max_shards"], 1000)
        
        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
