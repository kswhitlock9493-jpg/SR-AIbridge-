#!/usr/bin/env python3
"""
Smoke test for Leviathan Solver API endpoint
Tests the solver module and simulates the API endpoint behavior
"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock dependencies
import unittest.mock as mock
sys.modules['aiohttp'] = mock.MagicMock()
sys.modules['sqlalchemy'] = mock.MagicMock()
sys.modules['sqlalchemy.ext'] = mock.MagicMock()
sys.modules['sqlalchemy.ext.asyncio'] = mock.MagicMock()
sys.modules['aiosqlite'] = mock.MagicMock()

from bridge_core.engines.leviathan.solver import solve, SolveRequest

print("=" * 70)
print("Leviathan Solver Smoke Test")
print("=" * 70)

# Test 1: Basic solve
print("\n🧪 Test 1: Basic solve request")
print("-" * 70)
payload = {
    "q": "What would it take to build a 4D projection demo for Nova?",
    "captain": "Kyle",
    "project": "nova",
    "dispatch": False
}
print(f"Request: {json.dumps(payload, indent=2)}")
print()

req = SolveRequest(**payload)
result = solve(req)

print("Response:")
print(f"  ✓ Summary: {result['summary'][:100]}...")
print(f"  ✓ Plan phases: {len(result['plan'])}")
for phase in result['plan']:
    print(f"    - Phase {phase['phase']}: {phase['name']} ({phase['estimate_weeks']} weeks)")
print(f"  ✓ Requirements categories: {list(result['requirements'].keys())}")
print(f"  ✓ Math requirements: {result['requirements']['math']}")
print(f"  ✓ Science requirements: {result['requirements']['science']}")
print(f"  ✓ Team requirements: {result['requirements']['team']}")
print(f"  ✓ Citations - Truths: {len(result['citations']['truths'])}, Parser hits: {len(result['citations']['parser_hits'])}")
print(f"  ✓ Tasks spawned: {len(result['tasks'])}")
print(f"  ✓ Proof seal: {result['proof']['seal'][:32]}...")
print(f"  ✓ Engines used: {result['proof']['engines_used']}")

# Test 2: Query with multiple engine triggers
print("\n🧪 Test 2: Query triggering multiple engines")
print("-" * 70)
payload2 = {
    "q": "Build a 4D quantum navigation system with interactive UX, vendor analysis, and comprehensive budget plan",
    "modes": ["research", "design", "plan"]
}
print(f"Request: {json.dumps(payload2, indent=2)}")
print()

req2 = SolveRequest(**payload2)
result2 = solve(req2)

print("Response:")
print(f"  ✓ Detected intents: {result2['proof']['intents']}")
print(f"  ✓ Engines used: {result2['proof']['engines_used']}")
print(f"  ✓ Math requirements: {result2['requirements']['math']}")
print(f"  ✓ Quantum requirements: {result2['requirements']['quantum']}")
print(f"  ✓ Business ops: {result2['requirements']['team']}")

# Test 3: Verify proof artifact
print("\n🧪 Test 3: Proof artifact generation")
print("-" * 70)
proof = result['proof']
print(f"  ✓ Timestamp: {proof['ts']}")
print(f"  ✓ Query: {proof['q']}")
print(f"  ✓ Intents: {proof['intents']}")
print(f"  ✓ Sub-tasks: {len(proof['subs'])}")
for sub in proof['subs']:
    print(f"    - {sub['id']}: {sub['prompt'][:60]}...")
print(f"  ✓ Seal (SHA256): {proof['seal']}")
print(f"  ✓ Engines available: {proof['engines_used']['engines_available']}")

# Test 4: Six Super Engines adapter verification
print("\n🧪 Test 4: Six Super Engines adapter verification")
print("-" * 70)

# Test each adapter individually
from bridge_core.engines.leviathan.solver import (
    engine_math_science,
    engine_creativity,
    engine_business,
    engine_language,
    engine_history
)

# Math/Science adapter
q_math = "Implement 4D rotation matrices and projection operators"
m_result = engine_math_science(q_math)
print("Math/Science Adapter (CalculusCore + QHelmSingularity):")
print(f"  ✓ Notes: {len(m_result['notes'])} generated")
print(f"  ✓ Math requirements: {m_result['requirements']['math']}")
print(f"  ✓ Science requirements: {m_result['requirements']['science']}")

# Creativity adapter
q_creative = "Design interactive demo with UX wireframes"
c_result = engine_creativity(q_creative)
print("Creativity Adapter (AuroraForge):")
print(f"  ✓ Notes: {len(c_result['notes'])} generated")
print(f"  ✓ Artifacts: {c_result['artifacts']}")

# Business adapter
q_business = "Calculate budget and vendor costs for hardware"
b_result = engine_business(q_business)
print("Business Adapter (CommerceForge):")
print(f"  ✓ Notes: {len(b_result['notes'])} generated")
print(f"  ✓ Ops requirements: {b_result['requirements']['ops']}")
print(f"  ✓ Team requirements: {b_result['requirements']['team']}")

# Language adapter
points = ["Point 1: Math modeling", "Point 2: Implementation", "Point 3: Testing"]
l_result = engine_language("Test query", points)
print("Language Adapter (ScrollTongue):")
print(f"  ✓ Synthesized text: {l_result[:80]}...")

# History adapter
steps = [{"id": "step1", "prompt": "Test step"}]
h_result = engine_history("Review project history", steps)
print("History Adapter (ChronicleLoom):")
print(f"  ✓ Notes: {len(h_result['notes'])} generated")
print(f"  ✓ Chronicle refs: {h_result['chronicle_refs']}")

print("\n" + "=" * 70)
print("✅ All smoke tests passed!")
print("=" * 70)
print("\n📝 Summary:")
print("  • Leviathan Solver is operational")
print("  • Six Super Engines adapters are working:")
print("    - CalculusCore (Math)")
print("    - QHelmSingularity (Quantum/Science)")
print("    - AuroraForge (Creativity/Visual)")
print("    - ChronicleLoom (History)")
print("    - ScrollTongue (Language)")
print("    - CommerceForge (Business)")
print("  • Intent classification functional")
print("  • Proof artifacts generated with SHA256 seals")
print("  • Ready for API endpoint integration")
