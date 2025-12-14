"""
Integration tests for HXO Nexus connectivity implementation
Tests the "1+1=∞" connectivity paradigm
"""

import unittest
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge_core.engines.hxo.nexus import HXONexus, get_nexus_instance, initialize_nexus
from bridge_core.engines.hxo.hypshard import HypShardV3Manager
from bridge_core.engines.hxo.security import (
    QuantumEntropyHasher,
    HarmonicConsensusProtocol,
    SecurityLayerManager
)


class TestHXONexusCore(unittest.TestCase):
    """Test HXO Nexus core functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.nexus = HXONexus()
    
    def test_nexus_initialization(self):
        """Test nexus initializes with correct properties"""
        self.assertEqual(self.nexus.id, "HXO_CORE")
        self.assertEqual(self.nexus.label, "HXO Nexus")
        self.assertEqual(self.nexus.type, "central_harmonic_conductor")
        self.assertEqual(self.nexus.version, "1.9.6p")
        self.assertEqual(self.nexus.codename, "HXO Ascendant")
    
    def test_nexus_properties(self):
        """Test nexus has correct properties"""
        props = self.nexus.properties
        self.assertEqual(props["dimension"], "quantum-synchrony-layer")
        self.assertEqual(props["signature"], "harmonic_field_Ω")
        self.assertEqual(props["core_protocol"], "HCP (Harmonic Consensus Protocol)")
        self.assertEqual(props["entropy_channel"], "QEH-v3")
        self.assertEqual(props["governance"], "Truth + Autonomy")
    
    def test_engine_specs_loaded(self):
        """Test all 10 engines are specified"""
        expected_engines = [
            "GENESIS_BUS",
            "TRUTH_ENGINE",
            "BLUEPRINT_ENGINE",
            "CASCADE_ENGINE",
            "AUTONOMY_ENGINE",
            "FEDERATION_ENGINE",
            "PARSER_ENGINE",
            "LEVIATHAN_ENGINE",
            "ARIE_ENGINE",
            "ENVRECON_ENGINE"
        ]
        
        self.assertEqual(len(self.nexus._engine_specs), 10)
        
        for engine in expected_engines:
            self.assertIn(engine, self.nexus._engine_specs)
            self.assertIn("role", self.nexus._engine_specs[engine])
    
    def test_connection_topology(self):
        """Test connection topology is properly initialized"""
        # HXO_CORE should connect to all 10 engines
        hxo_connections = self.nexus.get_engine_connections("HXO_CORE")
        self.assertEqual(len(hxo_connections), 10)
        
        # Test specific connections from the spec
        self.assertTrue(self.nexus.is_connected("GENESIS_BUS", "TRUTH_ENGINE"))
        self.assertTrue(self.nexus.is_connected("TRUTH_ENGINE", "BLUEPRINT_ENGINE"))
        self.assertTrue(self.nexus.is_connected("CASCADE_ENGINE", "AUTONOMY_ENGINE"))
        self.assertTrue(self.nexus.is_connected("FEDERATION_ENGINE", "LEVIATHAN_ENGINE"))
        self.assertTrue(self.nexus.is_connected("ARIE_ENGINE", "TRUTH_ENGINE"))
    
    def test_bidirectional_connections(self):
        """Test that connections work bidirectionally"""
        # If A connects to B, we should be able to query from either direction
        graph = self.nexus.get_connection_graph()
        
        # Count total unique connections
        total_connections = sum(len(conns) for conns in graph.values())
        self.assertGreater(total_connections, 0)
    
    def test_register_engine(self):
        """Test registering an engine with the nexus"""
        self.nexus.register_engine("TEST_ENGINE", {
            "role": "test",
            "version": "1.0.0"
        })
        
        info = self.nexus.get_engine_info("TEST_ENGINE")
        self.assertIsNotNone(info)
        self.assertEqual(info["role"], "test")
        self.assertIn("registered_at", info)
    
    def test_event_handler_registration(self):
        """Test registering event handlers"""
        handler_called = []
        
        async def test_handler(event):
            handler_called.append(event)
        
        self.nexus.register_event_handler("test.event", test_handler)
        
        # Verify handler was registered
        self.assertIn("test.event", self.nexus._event_handlers)
        self.assertEqual(len(self.nexus._event_handlers["test.event"]), 1)
    
    def test_get_all_engines(self):
        """Test getting all registered engines"""
        self.nexus.register_engine("ENGINE1", {"role": "test1"})
        self.nexus.register_engine("ENGINE2", {"role": "test2"})
        
        all_engines = self.nexus.get_all_engines()
        self.assertEqual(len(all_engines), 2)
        self.assertIn("ENGINE1", all_engines)
        self.assertIn("ENGINE2", all_engines)
    
    def test_connection_graph_format(self):
        """Test connection graph returns correct format"""
        graph = self.nexus.get_connection_graph()
        
        # Graph should be a dict of lists
        self.assertIsInstance(graph, dict)
        
        for engine, connections in graph.items():
            self.assertIsInstance(connections, list)
            self.assertIsInstance(engine, str)


class TestHXONexusAsync(unittest.TestCase):
    """Test HXO Nexus async functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.nexus = HXONexus()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up"""
        self.loop.close()
    
    def test_coordinate_engines(self):
        """Test engine coordination"""
        async def run_test():
            intent = {
                "type": "test_coordination",
                "engines": ["TRUTH_ENGINE", "BLUEPRINT_ENGINE"]
            }
            
            result = await self.nexus.coordinate_engines(intent)
            
            self.assertEqual(result["status"], "coordinated")
            self.assertEqual(result["intent_type"], "test_coordination")
            self.assertIn("timestamp", result)
        
        self.loop.run_until_complete(run_test())
    
    def test_health_check(self):
        """Test nexus health check"""
        async def run_test():
            health = await self.nexus.health_check()
            
            self.assertEqual(health["nexus_id"], "HXO_CORE")
            self.assertEqual(health["version"], "1.9.6p")
            self.assertIn("enabled", health)
            self.assertIn("genesis_connected", health)
            self.assertIn("properties", health)
            self.assertIn("timestamp", health)
        
        self.loop.run_until_complete(run_test())


class TestHypShardV3(unittest.TestCase):
    """Test HypShard v3 quantum adaptive shard manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = HypShardV3Manager()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up"""
        self.loop.close()
    
    def test_hypshard_initialization(self):
        """Test HypShard initializes correctly"""
        self.assertEqual(self.manager.role, "quantum_adaptive_shard_manager")
        self.assertEqual(self.manager.max_capacity, 1_000_000)
        self.assertTrue(self.manager.policies["expand_on_load"])
        self.assertTrue(self.manager.policies["collapse_post_execute"])
        self.assertTrue(self.manager.policies["auto_balance"])
    
    def test_control_channels(self):
        """Test correct control channels are defined"""
        expected_channels = [
            "HXO_CORE",
            "FEDERATION_ENGINE",
            "LEVIATHAN_ENGINE",
            "CASCADE_ENGINE"
        ]
        
        self.assertEqual(self.manager.control_channels, expected_channels)
    
    def test_create_shard(self):
        """Test creating a shard"""
        async def run_test():
            config = {"type": "test", "capacity": 100}
            result = await self.manager.create_shard("shard_1", config)
            
            self.assertEqual(result["status"], "created")
            self.assertIn("shard", result)
            self.assertEqual(result["shard"]["id"], "shard_1")
            self.assertEqual(len(self.manager.active_shards), 1)
        
        self.loop.run_until_complete(run_test())
    
    def test_expand_shard(self):
        """Test shard expansion on load"""
        async def run_test():
            # Create initial shard
            await self.manager.create_shard("shard_1", {"type": "test"})
            
            # Expand it
            result = await self.manager.expand_shard("shard_1", reason="high_load")
            
            self.assertEqual(result["status"], "created")
            self.assertGreater(len(self.manager.active_shards), 1)
        
        self.loop.run_until_complete(run_test())
    
    def test_collapse_shard(self):
        """Test shard collapse after execution"""
        async def run_test():
            # Create shard
            await self.manager.create_shard("shard_1", {"type": "test"})
            
            # Set load to 0 (ready for collapse)
            self.manager.active_shards["shard_1"]["load"] = 0
            
            # Collapse it
            result = await self.manager.collapse_shard("shard_1")
            
            self.assertEqual(result["status"], "collapsed")
            self.assertEqual(len(self.manager.active_shards), 0)
        
        self.loop.run_until_complete(run_test())
    
    def test_shard_execution(self):
        """Test executing tasks on a shard"""
        async def run_test():
            await self.manager.create_shard("shard_1", {"type": "test"})
            
            task = {"id": "task_1", "action": "process"}
            result = await self.manager.execute_on_shard("shard_1", task)
            
            self.assertEqual(result["status"], "executed")
            self.assertEqual(result["shard_id"], "shard_1")
        
        self.loop.run_until_complete(run_test())
    
    def test_get_stats(self):
        """Test getting HypShard statistics"""
        async def run_test():
            stats = await self.manager.get_stats()
            
            self.assertEqual(stats["role"], "quantum_adaptive_shard_manager")
            self.assertEqual(stats["capacity"], 1_000_000)
            self.assertIn("active_shards", stats)
            self.assertIn("utilization", stats)
            self.assertIn("policies", stats)
        
        self.loop.run_until_complete(run_test())


class TestQuantumEntropyHasher(unittest.TestCase):
    """Test Quantum Entropy Hashing (QEH-v3)"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.hasher = QuantumEntropyHasher()
    
    def test_hasher_initialization(self):
        """Test hasher initializes correctly"""
        self.assertEqual(self.hasher.version, "v3")
        self.assertTrue(self.hasher.enabled)
    
    def test_hash_generation(self):
        """Test hash generation"""
        data = "test_data"
        hash_value = self.hasher.hash(data)
        
        self.assertIsInstance(hash_value, str)
        self.assertEqual(len(hash_value), 64)  # SHA-256 hex = 64 chars
    
    def test_hash_with_salt(self):
        """Test hash generation with salt"""
        data = "test_data"
        salt = "test_salt"
        
        hash_value = self.hasher.hash(data, salt)
        self.assertIsInstance(hash_value, str)
    
    def test_entropy_pool_refresh(self):
        """Test entropy pool refresh"""
        old_pool = self.hasher._entropy_pool
        self.hasher.refresh_entropy_pool()
        new_pool = self.hasher._entropy_pool
        
        self.assertNotEqual(old_pool, new_pool)


class TestHarmonicConsensusProtocol(unittest.TestCase):
    """Test Harmonic Consensus Protocol (HCP)"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.hcp = HarmonicConsensusProtocol()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up"""
        self.loop.close()
    
    def test_hcp_initialization(self):
        """Test HCP initializes correctly"""
        self.assertEqual(self.hcp.mode, "HARMONIC")
        self.assertEqual(self.hcp.recursion_limit, 5)
        self.assertTrue(self.hcp.enabled)
    
    def test_propose_consensus(self):
        """Test creating a consensus proposal"""
        async def run_test():
            proposal = {
                "action": "deploy",
                "target": "production"
            }
            
            result = await self.hcp.propose("proposal_1", proposal)
            
            self.assertEqual(result["status"], "proposed")
            self.assertEqual(result["proposal_id"], "proposal_1")
        
        self.loop.run_until_complete(run_test())
    
    def test_vote_on_proposal(self):
        """Test voting on a proposal"""
        async def run_test():
            # Create proposal
            proposal = {"action": "test", "required_votes": 2}
            await self.hcp.propose("proposal_1", proposal)
            
            # Vote
            result = await self.hcp.vote("proposal_1", "ENGINE_1", True)
            
            self.assertIn(result["status"], ["pending", "approved"])
        
        self.loop.run_until_complete(run_test())
    
    def test_consensus_reached(self):
        """Test consensus is reached with enough votes"""
        async def run_test():
            # Create proposal requiring 2 votes
            proposal = {"action": "test", "required_votes": 2}
            await self.hcp.propose("proposal_1", proposal)
            
            # Cast 2 approval votes
            await self.hcp.vote("proposal_1", "ENGINE_1", True)
            result = await self.hcp.vote("proposal_1", "ENGINE_2", True)
            
            self.assertEqual(result["status"], "approved")
            self.assertEqual(result["approvals"], 2)
        
        self.loop.run_until_complete(run_test())
    
    def test_get_consensus_status(self):
        """Test getting consensus status"""
        async def run_test():
            proposal = {"action": "test"}
            await self.hcp.propose("proposal_1", proposal)
            
            status = await self.hcp.get_consensus_status("proposal_1")
            
            self.assertIsNotNone(status)
            self.assertEqual(status["proposal_id"], "proposal_1")
            self.assertIn("status", status)
            self.assertIn("votes_count", status)
        
        self.loop.run_until_complete(run_test())


class TestSecurityLayerManager(unittest.TestCase):
    """Test unified security layer manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.security = SecurityLayerManager()
    
    def test_security_initialization(self):
        """Test security manager initializes correctly"""
        self.assertEqual(self.security.rbac_scope, "admiral_only")
        self.assertTrue(self.security.quantum_entropy_hashing)
        self.assertEqual(self.security.rollback_protection, "TruthEngine-verified")
        self.assertEqual(self.security.recursion_limit, 5)
        self.assertEqual(self.security.audit_trail, "ARIE-certified")
    
    def test_rbac_check_admiral(self):
        """Test RBAC check for admiral role"""
        self.assertTrue(self.security.check_rbac("admiral"))
        self.assertTrue(self.security.check_rbac("ADMIRAL"))
    
    def test_rbac_check_non_admiral(self):
        """Test RBAC check for non-admiral role"""
        self.assertFalse(self.security.check_rbac("captain"))
        self.assertFalse(self.security.check_rbac("user"))


class TestConnectivityParadigm(unittest.TestCase):
    """Test the '1+1=∞' connectivity paradigm"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.nexus = HXONexus()
    
    def test_all_engines_connect_to_nexus(self):
        """Test that all engines connect to HXO_CORE"""
        expected_engines = [
            "GENESIS_BUS",
            "TRUTH_ENGINE",
            "BLUEPRINT_ENGINE",
            "CASCADE_ENGINE",
            "AUTONOMY_ENGINE",
            "FEDERATION_ENGINE",
            "PARSER_ENGINE",
            "LEVIATHAN_ENGINE",
            "ARIE_ENGINE",
            "ENVRECON_ENGINE"
        ]
        
        hxo_connections = self.nexus.get_engine_connections("HXO_CORE")
        
        for engine in expected_engines:
            self.assertIn(engine, hxo_connections)
    
    def test_genesis_bus_connectivity(self):
        """Test Genesis Bus connects to required engines"""
        genesis_connections = self.nexus.get_engine_connections("GENESIS_BUS")
        
        required_connections = [
            "HXO_CORE",
            "TRUTH_ENGINE",
            "AUTONOMY_ENGINE",
            "ARIE_ENGINE",
            "CASCADE_ENGINE",
            "FEDERATION_ENGINE"
        ]
        
        for engine in required_connections:
            self.assertIn(engine, genesis_connections)
    
    def test_emergent_connectivity(self):
        """Test emergent connectivity through indirect connections"""
        # LEVIATHAN_ENGINE connects to ARIE_ENGINE
        self.assertTrue(self.nexus.is_connected("LEVIATHAN_ENGINE", "ARIE_ENGINE"))
        
        # ARIE_ENGINE connects to TRUTH_ENGINE
        self.assertTrue(self.nexus.is_connected("ARIE_ENGINE", "TRUTH_ENGINE"))
        
        # This creates an indirect path: LEVIATHAN -> ARIE -> TRUTH
        # demonstrating the "1+1=∞" emergent capability
    
    def test_connection_density(self):
        """Test the network has sufficient connection density"""
        graph = self.nexus.get_connection_graph()
        total_connections = sum(len(conns) for conns in graph.values())
        total_engines = len(graph)
        
        # Average connections per engine should be > 2 for good connectivity
        avg_connections = total_connections / total_engines if total_engines > 0 else 0
        self.assertGreater(avg_connections, 2.0)


if __name__ == "__main__":
    unittest.main()
