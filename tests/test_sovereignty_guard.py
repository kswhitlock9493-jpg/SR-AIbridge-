#!/usr/bin/env python3
"""
Tests for Bridge Sovereignty Readiness Gate System
"""

import pytest
import asyncio
from datetime import datetime, timezone

from bridge_core.sovereignty.readiness_gate import (
    BridgeSovereigntyGuard,
    SovereigntyState,
    EngineHealth,
    SovereigntyReport,
    get_sovereignty_guard,
    ensure_sovereignty,
)


class TestBridgeSovereigntyGuard:
    """Test the Bridge Sovereignty Guard"""
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test sovereignty guard initialization"""
        guard = BridgeSovereigntyGuard()
        
        # Should start in initializing state
        assert guard.state == SovereigntyState.INITIALIZING
        assert not guard.is_ready()
        
        # Initialize
        await guard.initialize()
        
        # Should have discovered engines
        assert len(guard.engine_health) > 0
    
    @pytest.mark.asyncio
    async def test_engine_discovery(self):
        """Test engine discovery"""
        guard = BridgeSovereigntyGuard()
        await guard._discover_engines()
        
        # Should discover at least the critical engines
        assert len(guard.engine_health) >= len(guard.CRITICAL_ENGINES)
        
        # Each engine should have health status
        for name, health in guard.engine_health.items():
            assert isinstance(health, EngineHealth)
            assert health.name == name
            assert isinstance(health.last_checked, datetime)
    
    @pytest.mark.asyncio
    async def test_harmony_assessment(self):
        """Test harmony assessment"""
        guard = BridgeSovereigntyGuard()
        await guard._discover_engines()
        await guard._assess_harmony()
        
        # All engines should have been checked
        for health in guard.engine_health.values():
            assert health.last_checked is not None
            assert 0.0 <= health.harmony_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_resonance_measurement(self):
        """Test resonance measurement"""
        guard = BridgeSovereigntyGuard()
        await guard._discover_engines()
        await guard._assess_harmony()
        await guard._measure_resonance()
        
        # Should complete without error
        assert True
    
    @pytest.mark.asyncio
    async def test_sovereignty_report(self):
        """Test sovereignty report generation"""
        guard = BridgeSovereigntyGuard()
        await guard.initialize()
        
        report = await guard.get_sovereignty_report()
        
        # Verify report structure
        assert isinstance(report, SovereigntyReport)
        assert isinstance(report.state, SovereigntyState)
        assert isinstance(report.is_ready, bool)
        assert 0.0 <= report.perfection_score <= 1.0
        assert 0.0 <= report.harmony_score <= 1.0
        assert 0.0 <= report.resonance_score <= 1.0
        assert 0.0 <= report.sovereignty_score <= 1.0
        assert report.engines_operational <= report.engines_total
        assert isinstance(report.critical_issues, list)
        assert isinstance(report.waiting_for, list)
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint"""
        guard = BridgeSovereigntyGuard()
        await guard.initialize()
        
        health = await guard.health_check()
        
        # Verify health check response structure
        assert "status" in health
        assert "state" in health
        assert "is_ready" in health
        assert "sovereignty" in health
        assert "engines" in health
        assert "timestamp" in health
        
        # Verify sovereignty section
        sov = health["sovereignty"]
        assert "perfection" in sov
        assert "harmony" in sov
        assert "resonance" in sov
        assert "overall" in sov
    
    @pytest.mark.asyncio
    async def test_wait_for_sovereignty(self):
        """Test waiting for sovereignty"""
        guard = BridgeSovereigntyGuard()
        await guard.initialize()
        
        # Wait with short timeout
        result = await guard.wait_for_sovereignty(timeout=5.0)
        
        # Result should be boolean
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_critical_engines(self):
        """Test that critical engines are properly identified"""
        guard = BridgeSovereigntyGuard()
        
        # Verify critical engines are defined
        assert len(guard.CRITICAL_ENGINES) > 0
        assert "Genesis_Bus" in guard.CRITICAL_ENGINES
        assert "Umbra_Lattice" in guard.CRITICAL_ENGINES
        assert "HXO_Nexus" in guard.CRITICAL_ENGINES
        assert "Autonomy" in guard.CRITICAL_ENGINES
        assert "Truth" in guard.CRITICAL_ENGINES
        assert "Blueprint" in guard.CRITICAL_ENGINES
    
    @pytest.mark.asyncio
    async def test_sovereignty_thresholds(self):
        """Test sovereignty thresholds are correctly set"""
        guard = BridgeSovereigntyGuard()
        
        # Verify thresholds
        assert guard.MIN_PERFECTION == 0.95
        assert guard.MIN_HARMONY == 0.95
        assert guard.MIN_RESONANCE == 0.99
        assert guard.MIN_SOVEREIGNTY == 0.99
    
    @pytest.mark.asyncio
    async def test_engine_operational_check(self):
        """Test engine operational checks"""
        guard = BridgeSovereigntyGuard()
        
        # Test checking a critical engine
        is_operational = await guard._check_engine_operational("Genesis_Bus")
        assert isinstance(is_operational, bool)
    
    @pytest.mark.asyncio
    async def test_engine_harmony_calculation(self):
        """Test engine harmony score calculation"""
        guard = BridgeSovereigntyGuard()
        
        # Test harmony calculation for critical engine
        harmony = await guard._calculate_engine_harmony("Genesis_Bus")
        assert 0.0 <= harmony <= 1.0
        
        # Critical engines should have higher base harmony
        critical_harmony = await guard._calculate_engine_harmony("Genesis_Bus")
        non_critical_harmony = await guard._calculate_engine_harmony("SomeOtherEngine")
        assert critical_harmony >= non_critical_harmony


class TestSovereigntyHelpers:
    """Test sovereignty helper functions"""
    
    @pytest.mark.asyncio
    async def test_get_sovereignty_guard(self):
        """Test getting the global sovereignty guard"""
        guard = await get_sovereignty_guard()
        
        assert isinstance(guard, BridgeSovereigntyGuard)
        
        # Getting again should return the same instance
        guard2 = await get_sovereignty_guard()
        assert guard is guard2
    
    @pytest.mark.asyncio
    async def test_ensure_sovereignty(self):
        """Test ensure_sovereignty helper"""
        result = await ensure_sovereignty()
        
        # Should return boolean
        assert isinstance(result, bool)


class TestSovereigntyReport:
    """Test SovereigntyReport data class"""
    
    def test_is_sovereign_property(self):
        """Test is_sovereign property logic"""
        # Create report with sovereign values
        report = SovereigntyReport(
            state=SovereigntyState.SOVEREIGN,
            is_ready=True,
            perfection_score=0.99,
            harmony_score=0.99,
            resonance_score=0.99,
            sovereignty_score=0.99,
            engines_operational=10,
            engines_total=10,
            critical_issues=[],
            timestamp=datetime.now(timezone.utc),
        )
        
        assert report.is_sovereign
        
        # Create report with non-sovereign values
        report2 = SovereigntyReport(
            state=SovereigntyState.WAITING,
            is_ready=False,
            perfection_score=0.80,
            harmony_score=0.80,
            resonance_score=0.80,
            sovereignty_score=0.80,
            engines_operational=8,
            engines_total=10,
            critical_issues=["Some issue"],
            timestamp=datetime.now(timezone.utc),
        )
        
        assert not report2.is_sovereign


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
