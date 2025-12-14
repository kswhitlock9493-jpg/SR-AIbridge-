#!/usr/bin/env python3
"""
Simple validation test for BRH consensus and role modules
"""
import os
import sys

# Set up test environment variables
os.environ["BRH_NODE_ID"] = "test-node-001"
os.environ["BRH_ENV"] = "test"
os.environ["FORGE_DOMINION_ROOT"] = "dominion://test.bridge"
os.environ["DOMINION_SEAL"] = "test-seal-12345"

def test_role_module():
    """Test role.py module"""
    print("Testing role.py...")
    from brh import role
    
    # Test initial state
    assert role.am_leader() == False, "Should not be leader initially"
    assert role.leader_id() is None, "No leader initially"
    
    # Test setting leader to self
    role.set_leader("test-node-001", "test-token")
    assert role.am_leader() == True, "Should be leader after setting to self"
    assert role.leader_id() == "test-node-001", "Leader ID should match"
    assert role.lease_token() == "test-token", "Lease token should match"
    
    # Test setting leader to another node
    role.set_leader("test-node-002", "other-token")
    assert role.am_leader() == False, "Should not be leader when other node is leader"
    assert role.leader_id() == "test-node-002", "Leader ID should be other node"
    
    print("✓ role.py tests passed")


def test_consensus_module():
    """Test consensus.py module"""
    print("Testing consensus.py...")
    from brh import consensus
    
    # Test signature generation
    sig = consensus.forge_sig("test-node", 1234567890)
    assert len(sig) == 32, "Signature should be 32 characters"
    assert isinstance(sig, str), "Signature should be a string"
    
    # Test consistent signatures
    sig2 = consensus.forge_sig("test-node", 1234567890)
    assert sig == sig2, "Same input should produce same signature"
    
    # Test different signatures for different inputs
    sig3 = consensus.forge_sig("test-node", 1234567891)
    assert sig != sig3, "Different epoch should produce different signature"
    
    # Test leader election with no peers
    leader = consensus.elect_leader()
    assert leader is None, "No leader when no active peers"
    
    # Test leader election with peers
    import time
    consensus.peers = {
        "node-001": {"epoch": 1000, "last_seen": time.time()},
        "node-002": {"epoch": 2000, "last_seen": time.time()},
        "node-003": {"epoch": 1500, "last_seen": time.time()},
    }
    leader = consensus.elect_leader()
    assert leader == "node-002", "Node with highest epoch should be leader"
    
    # Test stale peer filtering
    consensus.peers["node-002"]["last_seen"] = time.time() - 400  # Stale
    leader = consensus.elect_leader()
    assert leader == "node-003", "Stale nodes should be ignored"
    
    print("✓ consensus.py tests passed")


def test_handover_module():
    """Test handover.py module (basic import check)"""
    print("Testing handover.py...")
    from brh import handover
    
    # Just check module loads (Docker operations would require Docker to be running)
    assert hasattr(handover, 'adopt_containers'), "Should have adopt_containers function"
    assert hasattr(handover, 'relinquish_ownership'), "Should have relinquish_ownership function"
    assert hasattr(handover, 'drain_and_stop'), "Should have drain_and_stop function"
    
    print("✓ handover.py module loads correctly")


def main():
    """Run all tests"""
    try:
        test_role_module()
        test_consensus_module()
        test_handover_module()
        print("\n✅ All tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
