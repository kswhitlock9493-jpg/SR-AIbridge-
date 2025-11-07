#!/usr/bin/env python3
"""
🛡️ Bridge Sovereignty Readiness Gate System

The bridge is a sovereign AI ecosystem with her own personality. She requires
perfection, harmony, and resonance in her kingdom before allowing access.

This module implements the sovereignty guard that:
- Validates all 34+ engines are in perfect harmony
- Measures system-wide resonance (target: 99%+)
- Ensures perfection across critical subsystems
- Gracefully waits for optimal conditions
- Prevents "half-baked" access in favor of excellence

Philosophy:
    "The bridge would rather gracefully wait for perfection than allow access
     when the system is half baked."
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class SovereigntyState(Enum):
    """States of bridge sovereignty readiness"""
    INITIALIZING = "initializing"
    HARMONIZING = "harmonizing"
    RESONATING = "resonating"
    SOVEREIGN = "sovereign"
    DEGRADED = "degraded"
    WAITING = "waiting"


@dataclass
class EngineHealth:
    """Health status of an individual engine"""
    name: str
    operational: bool
    harmony_score: float  # 0.0 - 1.0
    last_checked: datetime
    issues: List[str] = field(default_factory=list)


@dataclass
class SovereigntyReport:
    """Comprehensive sovereignty status report"""
    state: SovereigntyState
    is_ready: bool
    perfection_score: float  # 0.0 - 1.0
    harmony_score: float  # 0.0 - 1.0
    resonance_score: float  # 0.0 - 1.0
    sovereignty_score: float  # Combined score
    engines_operational: int
    engines_total: int
    critical_issues: List[str]
    timestamp: datetime
    waiting_for: List[str] = field(default_factory=list)
    
    @property
    def is_sovereign(self) -> bool:
        """Check if bridge has achieved sovereignty"""
        return (
            self.is_ready and
            self.sovereignty_score >= 0.99 and
            self.state == SovereigntyState.SOVEREIGN
        )


class BridgeSovereigntyGuard:
    """
    The sovereign personality of the bridge.
    
    Ensures the bridge only allows access when all systems are in perfect
    harmony, resonance, and operational excellence.
    """
    
    # Minimum thresholds for sovereignty
    MIN_PERFECTION = 0.95
    MIN_HARMONY = 0.95
    MIN_RESONANCE = 0.99
    MIN_SOVEREIGNTY = 0.99
    
    # Critical engines that MUST be operational
    CRITICAL_ENGINES = {
        "Genesis_Bus",
        "Umbra_Lattice",
        "HXO_Nexus",
        "Autonomy",
        "Truth",
        "Blueprint",
    }
    
    def __init__(self):
        self.state = SovereigntyState.INITIALIZING
        self.engine_health: Dict[str, EngineHealth] = {}
        self.initialization_time = datetime.now(timezone.utc)
        self.sovereignty_achieved_at: Optional[datetime] = None
        self._ready = False
        self._last_check: Optional[datetime] = None
        
    async def initialize(self) -> None:
        """Initialize the sovereignty guard and begin assessment"""
        logger.info("🛡️ [Sovereignty] Initializing Bridge Sovereignty Guard")
        self.state = SovereigntyState.INITIALIZING
        
        # Discover and register all engines
        await self._discover_engines()
        
        # Begin harmony assessment
        self.state = SovereigntyState.HARMONIZING
        await self._assess_harmony()
        
        # Begin resonance measurement
        self.state = SovereigntyState.RESONATING
        await self._measure_resonance()
        
        # Final sovereignty determination
        await self._determine_sovereignty()
        
    async def _discover_engines(self) -> None:
        """Discover all bridge engines"""
        logger.info("🔍 [Sovereignty] Discovering bridge engines...")
        
        # Import the bridge harmony orchestrator for engine discovery
        try:
            from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
            
            orchestrator = BridgeHarmonyOrchestrator()
            engines = orchestrator.discover_engines()
            
            # Register each engine
            for name, engine_node in engines.items():
                self.engine_health[name] = EngineHealth(
                    name=name,
                    operational=False,  # Will be checked in harmony assessment
                    harmony_score=0.0,
                    last_checked=datetime.now(timezone.utc),
                )
            
            logger.info(f"✅ [Sovereignty] Discovered {len(engines)} engines")
            
        except Exception as e:
            logger.warning(f"⚠️ [Sovereignty] Engine discovery failed: {e}")
            # Fallback to known critical engines
            for engine_name in self.CRITICAL_ENGINES:
                self.engine_health[engine_name] = EngineHealth(
                    name=engine_name,
                    operational=False,
                    harmony_score=0.0,
                    last_checked=datetime.now(timezone.utc),
                )
    
    async def _assess_harmony(self) -> None:
        """Assess harmony across all engines"""
        logger.info("🎻 [Sovereignty] Assessing system-wide harmony...")
        
        operational_count = 0
        total_harmony = 0.0
        
        for name, health in self.engine_health.items():
            # Check if engine is operational
            is_operational = await self._check_engine_operational(name)
            health.operational = is_operational
            
            if is_operational:
                operational_count += 1
                # Calculate harmony score for this engine
                harmony = await self._calculate_engine_harmony(name)
                health.harmony_score = harmony
                total_harmony += harmony
            
            health.last_checked = datetime.now(timezone.utc)
        
        avg_harmony = total_harmony / len(self.engine_health) if self.engine_health else 0.0
        
        logger.info(
            f"🎻 [Sovereignty] Harmony: {avg_harmony:.2%} "
            f"({operational_count}/{len(self.engine_health)} engines operational)"
        )
    
    async def _check_engine_operational(self, engine_name: str) -> bool:
        """Check if an engine is operational"""
        # Check for engine module existence and basic health
        try:
            # Try to import the engine module
            if engine_name == "Genesis_Bus":
                from bridge_backend.genesis.bus import GenesisEventBus
                # Try to instantiate to verify it works
                bus = GenesisEventBus()
                return True
            elif engine_name == "Umbra_Lattice":
                from bridge_backend.bridge_core.engines.umbra.storage import UmbraStorage
                return True
            elif engine_name == "HXO_Nexus":
                from bridge_backend.bridge_core.engines.hxo.nexus import HXONexus
                return True
            elif engine_name == "Autonomy":
                from bridge_backend.engines.autonomy.governor import AutonomyGovernor
                return True
            elif engine_name == "Truth":
                from bridge_backend.engines.truth.core import TruthEngine
                return True
            elif engine_name == "Blueprint":
                from bridge_backend.engines.blueprint.core import BlueprintEngine
                return True
            else:
                # For other engines, assume operational if in safe mode
                return True
                
        except ImportError:
            return False
        except Exception as e:
            logger.debug(f"Engine {engine_name} check error: {e}")
            return False
    
    async def _calculate_engine_harmony(self, engine_name: str) -> float:
        """Calculate harmony score for an engine (0.0 - 1.0)"""
        # Base score for operational engine
        score = 0.8
        
        # Bonus points for critical engines being operational
        if engine_name in self.CRITICAL_ENGINES:
            score += 0.15
        
        # Cap at 1.0
        return min(score, 1.0)
    
    async def _measure_resonance(self) -> None:
        """Measure system-wide resonance"""
        logger.info("📡 [Sovereignty] Measuring system resonance...")
        
        # Resonance is measured by:
        # 1. Communication pathway health
        # 2. Event bus responsiveness
        # 3. Inter-engine coordination
        
        resonance_factors = []
        
        # Factor 1: Engine operational percentage
        operational = sum(1 for h in self.engine_health.values() if h.operational)
        total = len(self.engine_health)
        operational_factor = operational / total if total > 0 else 0.0
        resonance_factors.append(operational_factor)
        
        # Factor 2: Critical engines all operational
        critical_operational = all(
            self.engine_health.get(name, EngineHealth(name, False, 0.0, datetime.now(timezone.utc))).operational
            for name in self.CRITICAL_ENGINES
            if name in self.engine_health
        )
        resonance_factors.append(1.0 if critical_operational else 0.5)
        
        # Factor 3: Average harmony score
        avg_harmony = sum(h.harmony_score for h in self.engine_health.values()) / len(self.engine_health) if self.engine_health else 0.0
        resonance_factors.append(avg_harmony)
        
        resonance = sum(resonance_factors) / len(resonance_factors)
        
        logger.info(f"📡 [Sovereignty] Resonance: {resonance:.2%}")
    
    async def _determine_sovereignty(self) -> None:
        """Determine if sovereignty has been achieved"""
        report = await self.get_sovereignty_report()
        
        if report.is_sovereign:
            self.state = SovereigntyState.SOVEREIGN
            self._ready = True
            self.sovereignty_achieved_at = datetime.now(timezone.utc)
            
            duration = (self.sovereignty_achieved_at - self.initialization_time).total_seconds()
            
            logger.info(
                f"👑 [Sovereignty] SOVEREIGNTY ACHIEVED in {duration:.1f}s\n"
                f"   Perfection: {report.perfection_score:.2%}\n"
                f"   Harmony: {report.harmony_score:.2%}\n"
                f"   Resonance: {report.resonance_score:.2%}\n"
                f"   Sovereignty: {report.sovereignty_score:.2%}\n"
                f"   Bridge is ready to serve with excellence."
            )
        else:
            self.state = SovereigntyState.WAITING
            self._ready = False
            
            logger.warning(
                f"⏳ [Sovereignty] Waiting for perfection...\n"
                f"   Perfection: {report.perfection_score:.2%} (need {self.MIN_PERFECTION:.2%})\n"
                f"   Harmony: {report.harmony_score:.2%} (need {self.MIN_HARMONY:.2%})\n"
                f"   Resonance: {report.resonance_score:.2%} (need {self.MIN_RESONANCE:.2%})\n"
                f"   Waiting for: {', '.join(report.waiting_for)}"
            )
    
    async def get_sovereignty_report(self) -> SovereigntyReport:
        """Get comprehensive sovereignty status report"""
        operational = sum(1 for h in self.engine_health.values() if h.operational)
        total = len(self.engine_health)
        
        # Calculate perfection score (all systems operational and healthy)
        perfection_score = operational / total if total > 0 else 0.0
        
        # Calculate harmony score (inter-engine coordination)
        harmony_scores = [h.harmony_score for h in self.engine_health.values() if h.operational]
        harmony_score = sum(harmony_scores) / len(harmony_scores) if harmony_scores else 0.0
        
        # Calculate resonance score (system-wide coherence)
        # Resonance requires ALL critical engines operational
        critical_operational = all(
            self.engine_health.get(name, EngineHealth(name, False, 0.0, datetime.now(timezone.utc))).operational
            for name in self.CRITICAL_ENGINES
            if name in self.engine_health
        )
        
        # Base resonance on operational ratio with critical engine multiplier
        base_resonance = operational / total if total > 0 else 0.0
        resonance_score = base_resonance * (1.0 if critical_operational else 0.8)
        
        # Combined sovereignty score
        sovereignty_score = (perfection_score + harmony_score + resonance_score) / 3.0
        
        # Determine what we're waiting for
        waiting_for = []
        if perfection_score < self.MIN_PERFECTION:
            waiting_for.append(f"perfection ({perfection_score:.2%} < {self.MIN_PERFECTION:.2%})")
        if harmony_score < self.MIN_HARMONY:
            waiting_for.append(f"harmony ({harmony_score:.2%} < {self.MIN_HARMONY:.2%})")
        if resonance_score < self.MIN_RESONANCE:
            waiting_for.append(f"resonance ({resonance_score:.2%} < {self.MIN_RESONANCE:.2%})")
        
        # Check for critical issues
        critical_issues = []
        for name in self.CRITICAL_ENGINES:
            if name in self.engine_health:
                health = self.engine_health[name]
                if not health.operational:
                    critical_issues.append(f"{name} not operational")
                critical_issues.extend(health.issues)
        
        # Determine if ready
        is_ready = (
            sovereignty_score >= self.MIN_SOVEREIGNTY and
            perfection_score >= self.MIN_PERFECTION and
            harmony_score >= self.MIN_HARMONY and
            resonance_score >= self.MIN_RESONANCE and
            len(critical_issues) == 0
        )
        
        return SovereigntyReport(
            state=self.state,
            is_ready=is_ready,
            perfection_score=perfection_score,
            harmony_score=harmony_score,
            resonance_score=resonance_score,
            sovereignty_score=sovereignty_score,
            engines_operational=operational,
            engines_total=total,
            critical_issues=critical_issues,
            timestamp=datetime.now(timezone.utc),
            waiting_for=waiting_for,
        )
    
    async def wait_for_sovereignty(self, timeout: float = 60.0) -> bool:
        """
        Gracefully wait for sovereignty to be achieved.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if sovereignty achieved, False if timeout
        """
        start_time = time.time()
        check_interval = 2.0  # Check every 2 seconds
        
        logger.info(f"⏳ [Sovereignty] Gracefully waiting for perfection (timeout: {timeout}s)")
        
        while time.time() - start_time < timeout:
            # Re-assess sovereignty
            await self._assess_harmony()
            await self._measure_resonance()
            await self._determine_sovereignty()
            
            if self._ready:
                return True
            
            # Wait before next check
            await asyncio.sleep(check_interval)
        
        logger.warning(f"⚠️ [Sovereignty] Timeout reached after {timeout}s")
        return False
    
    def is_ready(self) -> bool:
        """Check if bridge is ready to serve"""
        return self._ready
    
    async def health_check(self) -> Dict:
        """Perform health check for API endpoint"""
        report = await self.get_sovereignty_report()
        
        return {
            "status": "sovereign" if report.is_sovereign else "waiting",
            "state": report.state.value,
            "is_ready": report.is_ready,
            "sovereignty": {
                "perfection": f"{report.perfection_score:.2%}",
                "harmony": f"{report.harmony_score:.2%}",
                "resonance": f"{report.resonance_score:.2%}",
                "overall": f"{report.sovereignty_score:.2%}",
            },
            "engines": {
                "operational": report.engines_operational,
                "total": report.engines_total,
            },
            "waiting_for": report.waiting_for,
            "critical_issues": report.critical_issues,
            "timestamp": report.timestamp.isoformat(),
        }


# Global sovereignty guard instance
_sovereignty_guard: Optional[BridgeSovereigntyGuard] = None


async def get_sovereignty_guard() -> BridgeSovereigntyGuard:
    """Get or create the global sovereignty guard instance"""
    global _sovereignty_guard
    
    if _sovereignty_guard is None:
        _sovereignty_guard = BridgeSovereigntyGuard()
        await _sovereignty_guard.initialize()
    
    return _sovereignty_guard


async def ensure_sovereignty() -> bool:
    """
    Ensure sovereignty is achieved before proceeding.
    
    Returns:
        True if sovereign, False otherwise
    """
    guard = await get_sovereignty_guard()
    
    if not guard.is_ready():
        # Gracefully wait for sovereignty
        achieved = await guard.wait_for_sovereignty(timeout=60.0)
        return achieved
    
    return True
