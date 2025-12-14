"""
Tests for Genesis bus topic registry (v1.9.6q)
Verifies that new topics are properly registered
"""
from bridge_backend.genesis.bus import genesis_bus


def test_new_topics_present():
    """Test that v1.9.6q topics are registered in Genesis bus"""
    required_topics = [
        "deploy.tde.orchestrator.completed",
        "deploy.tde.orchestrator.failed",
        "autonomy.tuning.signal",
    ]
    
    for topic in required_topics:
        assert topic in genesis_bus._valid_topics, f"Topic {topic} not found in Genesis registry"
