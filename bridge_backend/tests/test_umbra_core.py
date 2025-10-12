"""
Tests for Umbra Core - Pipeline Self-Healing Engine
"""

import pytest
import asyncio
from datetime import datetime, timezone
from bridge_backend.bridge_core.engines.umbra.core import UmbraCore


@pytest.mark.asyncio
async def test_umbra_core_initialization():
    """Test Umbra Core initialization"""
    core = UmbraCore()
    
    assert core is not None
    assert core.enabled is True
    assert core.repairs_applied == []
    assert core.anomalies_detected == []


@pytest.mark.asyncio
async def test_detect_anomaly_high_error_rate():
    """Test anomaly detection for high error rate"""
    core = UmbraCore()
    
    telemetry = {
        "error_rate": 0.15,
        "response_time": 100,
        "memory_usage": 0.5
    }
    
    anomaly = await core.detect_anomaly(telemetry)
    
    assert anomaly is not None
    assert anomaly["type"] == "high_error_rate"
    assert anomaly["severity"] == "high"
    assert "error_rate" in anomaly["message"].lower()


@pytest.mark.asyncio
async def test_detect_anomaly_high_latency():
    """Test anomaly detection for high latency"""
    core = UmbraCore()
    
    telemetry = {
        "error_rate": 0.01,
        "response_time": 6000,
        "memory_usage": 0.5
    }
    
    anomaly = await core.detect_anomaly(telemetry)
    
    assert anomaly is not None
    assert anomaly["type"] == "high_latency"
    assert anomaly["severity"] == "medium"


@pytest.mark.asyncio
async def test_detect_anomaly_high_memory():
    """Test anomaly detection for high memory usage"""
    core = UmbraCore()
    
    telemetry = {
        "error_rate": 0.01,
        "response_time": 100,
        "memory_usage": 0.95
    }
    
    anomaly = await core.detect_anomaly(telemetry)
    
    assert anomaly is not None
    assert anomaly["type"] == "high_memory"
    assert anomaly["severity"] == "high"


@pytest.mark.asyncio
async def test_detect_no_anomaly():
    """Test no anomaly detected with normal telemetry"""
    core = UmbraCore()
    
    telemetry = {
        "error_rate": 0.01,
        "response_time": 100,
        "memory_usage": 0.5
    }
    
    anomaly = await core.detect_anomaly(telemetry)
    
    assert anomaly is None


@pytest.mark.asyncio
async def test_generate_repair_for_high_error_rate():
    """Test repair generation for high error rate"""
    core = UmbraCore()
    
    anomaly = {
        "type": "high_error_rate",
        "severity": "high",
        "message": "Error rate exceeds threshold"
    }
    
    repair = await core.generate_repair(anomaly)
    
    assert repair is not None
    assert repair["repair_type"] == "auto"
    assert len(repair["actions"]) > 0
    assert repair["actions"][0]["action"] == "restart_service"
    assert repair["confidence"] > 0


@pytest.mark.asyncio
async def test_apply_repair():
    """Test repair application"""
    core = UmbraCore()
    
    repair = {
        "anomaly_id": "high_error_rate",
        "actions": [
            {
                "action": "restart_service",
                "target": "backend",
                "reason": "High error rate"
            }
        ],
        "confidence": 0.85
    }
    
    result = await core.apply_repair(repair)
    
    assert result is not None
    assert result["success"] is True
    assert len(result["actions_applied"]) == 1
    assert result["actions_applied"][0]["applied"] is True


@pytest.mark.asyncio
async def test_get_metrics():
    """Test metrics retrieval"""
    core = UmbraCore()
    
    # Detect an anomaly
    telemetry = {"error_rate": 0.15}
    await core.detect_anomaly(telemetry)
    
    metrics = core.get_metrics()
    
    assert metrics is not None
    assert "enabled" in metrics
    assert "anomalies_detected" in metrics
    assert "repairs_applied" in metrics
    assert metrics["anomalies_detected"] == 1


@pytest.mark.asyncio
async def test_full_repair_workflow():
    """Test complete detect -> generate -> apply workflow"""
    core = UmbraCore()
    
    # Step 1: Detect anomaly
    telemetry = {
        "error_rate": 0.2,
        "response_time": 200,
        "memory_usage": 0.6
    }
    
    anomaly = await core.detect_anomaly(telemetry)
    assert anomaly is not None
    
    # Step 2: Generate repair
    repair = await core.generate_repair(anomaly)
    assert repair is not None
    assert repair["confidence"] > 0
    
    # Step 3: Apply repair
    result = await core.apply_repair(repair)
    assert result is not None
    assert result["success"] is True
    
    # Check metrics
    metrics = core.get_metrics()
    assert metrics["anomalies_detected"] == 1
    assert metrics["repairs_applied"] == 1
    assert metrics["success_rate"] == 1.0
