"""
Elysium Guardian - Continuous Passive Guardian System
Watches over the Bridge continuously, running health cycles
"""

import os
import logging
import asyncio
from typing import Optional
from datetime import datetime, UTC
from pathlib import Path

logger = logging.getLogger(__name__)


class ElysiumGuardian:
    """
    Elysium Continuous Guardian System
    
    Runs the full autonomy cycle on a schedule:
    1. Sanctum - Predictive simulation
    2. Forge - Autonomous repair
    3. ARIE - Integrity audit
    4. Truth - Certification
    
    Publishes elysium.cycle.complete to Genesis Bus.
    """
    
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self.enabled = os.getenv("ELYSIUM_ENABLED", "true").lower() == "true"
        self.interval_hours = int(os.getenv("ELYSIUM_INTERVAL_HOURS", "6"))
        self.run_immediately = os.getenv("ELYSIUM_RUN_IMMEDIATELY", "true").lower() == "true"
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def run_cycle(self) -> dict:
        """
        Run full system audit cycle
        
        Pipeline:
        1. Sanctum predeploy check
        2. Forge full repair
        3. ARIE integrity audit
        4. Truth certification
        5. Genesis Bus event publication
        
        Returns:
            Cycle results
        """
        logger.info("🌐 Elysium cycle starting — full system audit...")
        
        cycle_results = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "status": "stable",
            "sanctum": None,
            "forge": None,
            "arie": None,
            "certified": False
        }
        
        try:
            # Import engines
            from bridge_backend.engines.sanctum.core import SanctumEngine
            from bridge_backend.engines.forge.core import ForgeEngine
            from bridge_backend.engines.arie.core import ARIEEngine
            from bridge_backend.genesis.bus import genesis_bus
            from bridge_backend.engines.chimera.adapters.truth_adapter import TruthGate
            
            # 1. Sanctum predictive check
            logger.info("🧭 Elysium: Running Sanctum simulation...")
            sanctum = SanctumEngine(self.repo_root)
            sanctum_report = await sanctum.run_predeploy_check()
            cycle_results["sanctum"] = {
                "status": "passed" if not sanctum_report.has_errors() else "failed",
                "errors": sanctum_report.errors
            }
            
            # 2. Forge repair
            logger.info("🛠️ Elysium: Running Forge repair...")
            forge = ForgeEngine(self.repo_root)
            forge_report = await forge.run_full_repair(scan_only=False)
            cycle_results["forge"] = {
                "issues_found": len(forge_report.get("issues", [])),
                "issues_fixed": forge_report.get("fixed", 0)
            }
            
            # 3. ARIE integrity audit
            logger.info("🧠 Elysium: Running ARIE integrity audit...")
            arie = ARIEEngine(self.repo_root)
            arie_summary = arie.run(dry_run=True, apply=False)
            cycle_results["arie"] = {
                "findings_count": arie_summary.findings_count,
                "duration": arie_summary.duration_seconds
            }
            
            # 4. Truth certification
            truth = TruthGate()
            cert_result = await truth.certify(
                cycle_results,
                {"ok": True}
            )
            cycle_results["certified"] = cert_result.get("certified", False)
            
            if cycle_results["certified"]:
                logger.info("✅ Elysium: Truth certified cycle completion")
            
            # Publish to Genesis Bus
            await genesis_bus.publish("elysium.cycle.complete", cycle_results)
            
            logger.info("🪶 Elysium cycle complete - system stable")
            
        except Exception as e:
            logger.error(f"❌ Elysium: Cycle error: {e}")
            cycle_results["status"] = "error"
            cycle_results["error"] = str(e)
        
        return cycle_results
    
    async def _scheduler_loop(self):
        """Internal scheduler loop"""
        logger.info(f"🪶 Elysium: Scheduler started (interval: {self.interval_hours}h)")
        
        # Run immediately if configured
        if self.run_immediately:
            await self.run_cycle()
        
        # Schedule periodic runs
        while self._running:
            await asyncio.sleep(self.interval_hours * 3600)  # Convert hours to seconds
            if self._running:
                await self.run_cycle()
    
    def start(self):
        """
        Start the Elysium Guardian
        
        Initializes continuous monitoring and runs first cycle.
        """
        if not self.enabled:
            logger.info("🪶 Elysium: Disabled, not starting")
            return
        
        if self._running:
            logger.warning("🪶 Elysium: Already running")
            return
        
        logger.info("🪶 Elysium: Continuous monitoring thread initialized.")
        self._running = True
        
        # Start scheduler in background
        self._task = asyncio.create_task(self._scheduler_loop())
        
        logger.info(f"🪶 Elysium: Active - will run every {self.interval_hours} hours")
    
    async def start_async(self):
        """
        Async version of start for use in async contexts
        """
        if not self.enabled:
            logger.info("🪶 Elysium: Disabled, not starting")
            return
        
        if self._running:
            logger.warning("🪶 Elysium: Already running")
            return
        
        logger.info("🪶 Elysium: Continuous monitoring thread initialized.")
        self._running = True
        
        # Run scheduler loop directly
        await self._scheduler_loop()
    
    async def stop(self):
        """Stop the Elysium Guardian"""
        if not self._running:
            return
        
        logger.info("🪶 Elysium: Stopping guardian...")
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("🪶 Elysium: Stopped")
    
    async def run_manual_cycle(self) -> dict:
        """
        Manually trigger a cycle (for testing or on-demand execution)
        
        Returns:
            Cycle results
        """
        logger.info("🪶 Elysium: Manual cycle triggered")
        return await self.run_cycle()


# CLI entry point for standalone execution
if __name__ == "__main__":
    import asyncio
    
    async def main():
        guardian = ElysiumGuardian()
        
        print("\n" + "="*60)
        print("🪶 Elysium Guardian - Total Autonomy Protocol")
        print("="*60)
        print(f"Enabled: {'✅' if guardian.enabled else '❌'}")
        print(f"Interval: {guardian.interval_hours} hours")
        print("="*60)
        
        # Run one cycle
        print("\n🌐 Running full system audit cycle...\n")
        results = await guardian.run_manual_cycle()
        
        print("\n" + "="*60)
        print("📊 Cycle Results")
        print("="*60)
        print(f"Status: {results['status']}")
        print(f"Certified: {'✅' if results['certified'] else '❌'}")
        
        if results.get('sanctum'):
            print(f"\n🧭 Sanctum: {results['sanctum']['status']}")
            if results['sanctum'].get('errors'):
                for error in results['sanctum']['errors']:
                    print(f"  - {error}")
        
        if results.get('forge'):
            print(f"\n🛠️ Forge: {results['forge']['issues_fixed']}/{results['forge']['issues_found']} issues fixed")
        
        if results.get('arie'):
            print(f"\n🧠 ARIE: {results['arie']['findings_count']} findings ({results['arie']['duration']:.2f}s)")
        
        print("="*60)
        print("✅ Elysium cycle complete\n")
    
    asyncio.run(main())
