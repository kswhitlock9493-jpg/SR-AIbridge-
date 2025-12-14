#!/usr/bin/env python3
"""
Simple smoke test for parser, blueprint, and truth engines
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "bridge_backend"))

def test_parser_engine():
    """Test that parser engine can ingest and search content"""
    from bridge_core.engines.parser.service import ParserEngine
    
    print("Testing Parser Engine...")
    parser = ParserEngine()
    
    # Test ingestion
    result = parser.ingest("This is a test document for the parser engine.", source="test.txt")
    assert result.ok, "Ingestion should succeed"
    assert result.seen == 1, "Should see 1 chunk"
    
    # Test search
    search_result = parser.search("parser engine", limit=5)
    assert "items" in search_result, "Search should return items"
    
    print("✓ Parser Engine working")


def test_blueprint_engine():
    """Test that blueprint engine can create plans"""
    from bridge_core.engines.blueprint.blueprint_engine import BlueprintEngine
    
    print("Testing Blueprint Engine...")
    blueprint = BlueprintEngine()
    
    # Test plan generation
    plan = blueprint.draft("Create a simple test plan with basic tasks")
    assert "objectives" in plan, "Plan should have objectives"
    assert "tasks" in plan, "Plan should have tasks"
    assert len(plan["tasks"]) > 0, "Should generate at least one task"
    
    # Verify task structure
    task = plan["tasks"][0]
    assert "key" in task, "Task should have key"
    assert "title" in task, "Task should have title"
    assert "depends_on" in task, "Task should have dependencies"
    
    print("✓ Blueprint Engine working")


def test_truth_engine():
    """Test that truth engine can bind and certify facts"""
    from bridge_core.engines.truth.binder import bind_candidates
    from bridge_core.engines.truth.utils import TRUTH_DIR
    
    print("Testing Truth Engine...")
    
    # Ensure truth directory exists
    TRUTH_DIR.mkdir(parents=True, exist_ok=True)
    
    # Test fact binding
    candidates = [
        {
            "fact": "The parser engine handles content ingestion",
            "sources": [{"sha": "test", "ts": "2024-11-04", "source": "test.txt"}]
        },
        {
            "fact": "The blueprint engine creates structured plans",
            "sources": [{"sha": "test", "ts": "2024-11-04", "source": "test.txt"}]
        }
    ]
    
    result = bind_candidates(candidates, similarity=0.70)
    assert "truths" in result, "Should return truths"
    assert result["count"] == 2, "Should certify 2 facts"
    
    print("✓ Truth Engine working")


def main():
    """Run all smoke tests"""
    print("\n" + "=" * 60)
    print("  Engine Smoke Tests")
    print("=" * 60 + "\n")
    
    try:
        test_parser_engine()
        test_blueprint_engine()
        test_truth_engine()
        
        print("\n" + "=" * 60)
        print("  ✓ All engines working correctly!")
        print("=" * 60 + "\n")
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
