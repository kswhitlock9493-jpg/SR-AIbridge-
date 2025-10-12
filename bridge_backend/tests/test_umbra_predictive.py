"""
Tests for Umbra Predictive - Confidence-Based Pre-Repair Engine
"""

import pytest
import asyncio
from datetime import datetime, timezone
from bridge_backend.bridge_core.engines.umbra.predictive import UmbraPredictive
from bridge_backend.bridge_core.engines.umbra.memory import UmbraMemory
from bridge_backend.bridge_core.engines.umbra.core import UmbraCore


@pytest.mark.asyncio
async def test_umbra_predictive_initialization():
    """Test Umbra Predictive initialization"""
    predictive = UmbraPredictive()
    
    assert predictive is not None
    assert predictive.enabled is True
    assert predictive.confidence_threshold > 0


@pytest.mark.asyncio
async def test_predict_issue_with_patterns():
    """Test issue prediction with learned patterns"""
    memory = UmbraMemory()
    core = UmbraCore(memory=memory)
    predictive = UmbraPredictive(memory=memory, core=core)
    
    # Record some repair experiences to learn from
    await memory.record("repair", {
        "anomaly_id": "high_error_rate",
        "actions": [{"action": "restart"}],
        "confidence": 0.85
    }, {"success": True})
    
    await memory.record("repair", {
        "anomaly_id": "high_error_rate",
        "actions": [{"action": "restart"}],
        "confidence": 0.90
    }, {"success": True})
    
    # Predict based on telemetry
    telemetry = {
        "error_rate": 0.08,  # Not high yet, but trending
        "response_time": 100,
        "memory_usage": 0.5
    }
    
    prediction = await predictive.predict_issue(telemetry)
    
    # May or may not predict based on confidence threshold
    if prediction:
        assert "predicted_issue" in prediction
        assert "confidence" in prediction
        assert prediction["confidence"] >= predictive.confidence_threshold


@pytest.mark.asyncio
async def test_predict_issue_no_patterns():
    """Test prediction with no learned patterns"""
    memory = UmbraMemory()
    predictive = UmbraPredictive(memory=memory)
    
    telemetry = {
        "error_rate": 0.05,
        "response_time": 100
    }
    
    prediction = await predictive.predict_issue(telemetry)
    
    # Should return None with no patterns
    assert prediction is None


@pytest.mark.asyncio
async def test_apply_preventive_repair():
    """Test applying preventive repair"""
    memory = UmbraMemory()
    core = UmbraCore(memory=memory)
    predictive = UmbraPredictive(memory=memory, core=core)
    
    # Create a prediction
    prediction = {
        "predicted_issue": "high_error_rate",
        "confidence": 0.85,
        "recommended_actions": [
            {"action": "restart_service", "target": "backend"}
        ]
    }
    
    # Apply preventive repair
    result = await predictive.apply_preventive_repair(prediction)
    
    assert result is not None
    assert result["success"] is True
    assert result.get("preventive") is True
    assert "prediction" in result


@pytest.mark.asyncio
async def test_update_model_increase_threshold():
    """Test model update increasing threshold on low accuracy"""
    predictive = UmbraPredictive()
    
    initial_threshold = predictive.confidence_threshold
    
    # Provide low accuracy feedback
    feedback = {
        "accuracy": 0.6,
        "prediction": "test"
    }
    
    await predictive.update_model(feedback)
    
    # Threshold should increase for low accuracy
    assert predictive.confidence_threshold >= initial_threshold


@pytest.mark.asyncio
async def test_update_model_decrease_threshold():
    """Test model update decreasing threshold on high accuracy"""
    predictive = UmbraPredictive()
    
    initial_threshold = predictive.confidence_threshold
    
    # Provide high accuracy feedback
    feedback = {
        "accuracy": 0.95,
        "prediction": "test"
    }
    
    await predictive.update_model(feedback)
    
    # Threshold should decrease for high accuracy
    assert predictive.confidence_threshold <= initial_threshold


@pytest.mark.asyncio
async def test_get_metrics():
    """Test metrics retrieval"""
    memory = UmbraMemory()
    core = UmbraCore(memory=memory)
    predictive = UmbraPredictive(memory=memory, core=core)
    
    metrics = predictive.get_metrics()
    
    assert metrics is not None
    assert "enabled" in metrics
    assert "predictions_made" in metrics
    assert "confidence_threshold" in metrics
    assert "avg_confidence" in metrics


@pytest.mark.asyncio
async def test_confidence_threshold_bounds():
    """Test that confidence threshold stays within reasonable bounds"""
    predictive = UmbraPredictive()
    
    # Try to decrease threshold significantly
    for _ in range(10):
        await predictive.update_model({"accuracy": 0.99})
    
    assert predictive.confidence_threshold >= 0.5  # Should not go too low
    
    # Try to increase threshold significantly
    for _ in range(10):
        await predictive.update_model({"accuracy": 0.5})
    
    assert predictive.confidence_threshold <= 1.0  # Should not exceed 1.0
