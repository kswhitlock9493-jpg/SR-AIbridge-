#!/usr/bin/env python3
"""
Minimal test for Leviathan Solver without app dependencies
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock aiohttp to avoid import errors
import unittest.mock as mock
sys.modules['aiohttp'] = mock.MagicMock()
sys.modules['sqlalchemy'] = mock.MagicMock()
sys.modules['sqlalchemy.ext'] = mock.MagicMock()
sys.modules['sqlalchemy.ext.asyncio'] = mock.MagicMock()
sys.modules['aiosqlite'] = mock.MagicMock()

from bridge_core.engines.leviathan.solver import solve, SolveRequest

def test_basic_solve():
    """Test basic solve functionality"""
    print("Testing basic solve...")
    req = SolveRequest(q='Build a 4D projection demo with quantum rendering')
    result = solve(req)
    
    assert 'summary' in result, "Missing summary"
    assert 'plan' in result, "Missing plan"
    assert 'requirements' in result, "Missing requirements"
    assert 'citations' in result, "Missing citations"
    assert 'tasks' in result, "Missing tasks"
    assert 'proof' in result, "Missing proof"
    
    # Verify plan structure
    assert len(result['plan']) > 0, "Plan should have phases"
    for phase in result['plan']:
        assert 'phase' in phase
        assert 'name' in phase
        assert 'deliverables' in phase
        assert 'estimate_weeks' in phase
    
    # Verify requirements structure
    assert 'math' in result['requirements']
    assert 'science' in result['requirements']
    assert 'software' in result['requirements']
    assert 'team' in result['requirements']
    
    # Verify proof has seal
    assert result['proof']['seal'], "Proof should have seal"
    assert 'engines_used' in result['proof']
    
    print("✓ Basic solve test passed")
    print(f"✓ Summary: {result['summary'][:80]}...")
    print(f"✓ Plan has {len(result['plan'])} phases")
    print(f"✓ Requirements: {list(result['requirements'].keys())}")
    print(f"✓ Proof seal: {result['proof']['seal'][:16]}...")
    print(f"✓ Engines used: {result['proof']['engines_used']}")
    return True

def test_intent_classification():
    """Test intent classification with different queries"""
    print("\nTesting intent classification...")
    
    # Research intent
    req1 = SolveRequest(q='What are the latest papers on 4D visualization?')
    result1 = solve(req1)
    assert 'research' in result1['proof']['intents']
    print("✓ Research intent detected")
    
    # Design intent
    req2 = SolveRequest(q='Design a system architecture for quantum rendering')
    result2 = solve(req2)
    assert 'design' in result2['proof']['intents']
    print("✓ Design intent detected")
    
    # Plan intent
    req3 = SolveRequest(q='Create a roadmap with milestones for the project')
    result3 = solve(req3)
    assert 'plan' in result3['proof']['intents']
    print("✓ Plan intent detected")
    
    print("✓ Intent classification test passed")
    return True

def test_with_modes():
    """Test solve with specific modes"""
    print("\nTesting with specific modes...")
    req = SolveRequest(
        q='Design a visualization system',
        modes=['design', 'research']
    )
    result = solve(req)
    assert result['proof']['intents'] == ['design', 'research']
    print("✓ Custom modes test passed")
    return True

def test_engine_adapters():
    """Test that engine adapters are working"""
    print("\nTesting engine adapters...")
    
    # Query with keywords to trigger different adapters
    req = SolveRequest(
        q='Build a 4D projection demo with quantum rendering, UX design, and business plan'
    )
    result = solve(req)
    
    engines_used = result['proof']['engines_used']
    assert 'math_science' in engines_used
    assert 'creativity' in engines_used
    assert 'business' in engines_used
    
    # Check that requirements were populated
    assert len(result['requirements']['math']) > 0
    assert len(result['requirements']['team']) > 0
    
    print(f"✓ Engines used: {engines_used}")
    print(f"✓ Math requirements: {result['requirements']['math']}")
    print(f"✓ Team requirements: {result['requirements']['team']}")
    print("✓ Engine adapters test passed")
    return True

def test_proof_generation():
    """Test proof artifact generation"""
    print("\nTesting proof generation...")
    
    req = SolveRequest(q='Test proof generation')
    result = solve(req)
    
    proof = result['proof']
    assert 'ts' in proof
    assert 'q' in proof
    assert 'intents' in proof
    assert 'subs' in proof
    assert 'seal' in proof
    assert len(proof['seal']) == 64  # SHA256 hex digest
    
    print(f"✓ Proof timestamp: {proof['ts']}")
    print(f"✓ Proof seal (SHA256): {proof['seal'][:32]}...")
    print("✓ Proof generation test passed")
    return True

if __name__ == '__main__':
    print("=" * 70)
    print("Leviathan Solver Tests")
    print("=" * 70)
    
    all_passed = True
    tests = [
        test_basic_solve,
        test_intent_classification,
        test_with_modes,
        test_engine_adapters,
        test_proof_generation
    ]
    
    for test in tests:
        try:
            if not test():
                all_passed = False
        except Exception as e:
            print(f"✗ Test {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)
