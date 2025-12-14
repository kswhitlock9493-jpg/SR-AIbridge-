#!/usr/bin/env python3
"""
Integration test for consensus role changes and handover
"""
import os
import sys
import time

# Set up test environment
os.environ["BRH_NODE_ID"] = "test-node-alpha"
os.environ["BRH_ENV"] = "integration-test"
os.environ["FORGE_DOMINION_ROOT"] = "dominion://test.bridge"
os.environ["DOMINION_SEAL"] = "integration-test-seal"

sys.path.insert(0, '/home/runner/work/SR-AIbridge-/SR-AIbridge-')

from brh import consensus, role


def test_leader_promotion_flow():
    """Test the complete leader promotion flow"""
    print("\n=== Testing Leader Promotion Flow ===")
    
    # Step 1: Initially no leader
    print("Step 1: Initial state - no leader")
    assert not role.am_leader(), "Should not be leader initially"
    
    # Step 2: Simulate receiving consensus that makes us leader
    print("Step 2: Applying leader change to self")
    consensus.apply_leader_change("test-node-alpha", "test-lease-001")
    
    assert role.am_leader(), "Should be leader after promotion"
    assert role.leader_id() == "test-node-alpha", "Leader ID should be self"
    assert role.lease_token() == "test-lease-001", "Lease token should match"
    print("✓ Promoted to leader successfully")
    
    # Step 3: Simulate demotion (another node becomes leader)
    print("\nStep 3: Demotion - another node becomes leader")
    consensus.apply_leader_change("test-node-beta", "test-lease-002")
    
    assert not role.am_leader(), "Should not be leader after demotion"
    assert role.leader_id() == "test-node-beta", "Leader should be other node"
    print("✓ Demoted to witness successfully")
    
    # Step 4: Test re-promotion
    print("\nStep 4: Re-promotion back to leader")
    consensus.apply_leader_change("test-node-alpha", "test-lease-003")
    
    assert role.am_leader(), "Should be leader again"
    print("✓ Re-promoted to leader successfully")


def test_consensus_election():
    """Test consensus election algorithm"""
    print("\n=== Testing Consensus Election ===")
    
    # Clear peers
    consensus.peers = {}
    
    # Add peers with different epochs
    now = time.time()
    consensus.peers = {
        "node-001": {"epoch": 1000, "last_seen": now, "sig": "sig1", "status": "alive"},
        "node-002": {"epoch": 3000, "last_seen": now, "sig": "sig2", "status": "alive"},
        "node-003": {"epoch": 2000, "last_seen": now, "sig": "sig3", "status": "alive"},
    }
    
    leader = consensus.elect_leader()
    print(f"Elected leader: {leader}")
    assert leader == "node-002", "Node with highest epoch should win"
    print("✓ Correct leader elected (highest epoch)")
    
    # Test stale peer exclusion
    consensus.peers["node-002"]["last_seen"] = now - 400  # Make stale (>300s)
    leader = consensus.elect_leader()
    print(f"Elected leader after node-002 became stale: {leader}")
    assert leader == "node-003", "Stale nodes should be excluded"
    print("✓ Stale nodes correctly excluded from election")
    
    # Test alphabetical fallback when epochs are equal
    consensus.peers = {
        "zebra-node": {"epoch": 5000, "last_seen": now, "sig": "sig1", "status": "alive"},
        "alpha-node": {"epoch": 5000, "last_seen": now, "sig": "sig2", "status": "alive"},
        "beta-node": {"epoch": 5000, "last_seen": now, "sig": "sig3", "status": "alive"},
    }
    leader = consensus.elect_leader()
    print(f"Elected leader with equal epochs: {leader}")
    assert leader == "alpha-node", "Should use alphabetical order as tiebreaker"
    print("✓ Alphabetical tiebreaker works correctly")


def test_signature_consistency():
    """Test signature generation consistency"""
    print("\n=== Testing Signature Consistency ===")
    
    # Same inputs should produce same output
    sig1 = consensus.forge_sig("test-node", 12345)
    sig2 = consensus.forge_sig("test-node", 12345)
    assert sig1 == sig2, "Same inputs should produce identical signatures"
    print(f"✓ Signature consistency verified: {sig1}")
    
    # Different inputs should produce different outputs
    sig3 = consensus.forge_sig("test-node", 12346)
    assert sig1 != sig3, "Different inputs should produce different signatures"
    print(f"✓ Signature uniqueness verified")


def main():
    """Run all integration tests"""
    try:
        test_signature_consistency()
        test_consensus_election()
        test_leader_promotion_flow()
        
        print("\n" + "="*50)
        print("✅ All integration tests passed!")
        print("="*50)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
