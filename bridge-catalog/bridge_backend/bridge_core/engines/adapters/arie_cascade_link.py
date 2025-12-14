"""
ARIE Cascade Link - Post-fix flow integration
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ARIECascadeLink:
    """
    Cascade integration for ARIE
    
    Post-fix flows:
    - Re-run unit tests
    - Warm caches
    - Ping deploy parity
    - Notify EnvRecon
    """
    
    def __init__(self, cascade_engine=None, bus=None):
        self.cascade_engine = cascade_engine
        self.bus = bus
    
    async def trigger_post_fix_cascade(self, summary):
        """
        Trigger cascade flows after ARIE applies fixes
        
        Args:
            summary: ARIE Summary object with fix results
        """
        if not summary.fixes_applied:
            logger.info("[ARIE Cascade] No fixes applied, skipping cascade")
            return
        
        logger.info(f"[ARIE Cascade] Triggering post-fix cascade for run {summary.run_id}")
        
        try:
            # Step 1: Re-run unit tests for modified files
            await self._run_tests(summary)
            
            # Step 2: Warm caches if needed
            await self._warm_caches(summary)
            
            # Step 3: Check deploy parity
            await self._check_parity(summary)
            
            # Step 4: Notify EnvRecon of potential env changes
            await self._notify_envrecon(summary)
            
            logger.info(f"[ARIE Cascade] Post-fix cascade completed for run {summary.run_id}")
        
        except Exception as e:
            logger.exception(f"[ARIE Cascade] Error in post-fix cascade: {e}")
    
    async def _run_tests(self, summary):
        """Re-run unit tests for modified files"""
        if not self.cascade_engine:
            logger.info("[ARIE Cascade] No Cascade engine, skipping tests")
            return
        
        # Extract test files related to modified files
        test_files = []
        for patch in summary.patches:
            for file_path in patch.files_modified:
                # Find corresponding test file
                if file_path.endswith('.py'):
                    # Look for test_<module>.py
                    test_path = file_path.replace('.py', '_test.py')
                    if 'test_' not in file_path:
                        parts = file_path.split('/')
                        if len(parts) > 0:
                            module_name = parts[-1].replace('.py', '')
                            test_files.append(f"tests/test_{module_name}.py")
        
        if test_files:
            logger.info(f"[ARIE Cascade] Would run tests: {test_files}")
            # Placeholder for actual test execution
    
    async def _warm_caches(self, summary):
        """Warm relevant caches after fixes"""
        logger.info("[ARIE Cascade] Cache warming (placeholder)")
        # Placeholder for cache warming logic
    
    async def _check_parity(self, summary):
        """Check deploy parity after fixes"""
        if self.bus:
            await self.bus.publish("parity.check", {
                "trigger": "arie_fix",
                "run_id": summary.run_id,
                "timestamp": summary.timestamp
            })
        logger.info("[ARIE Cascade] Parity check triggered")
    
    async def _notify_envrecon(self, summary):
        """Notify EnvRecon of potential env var changes"""
        # Check if any config smell fixes were applied
        config_fixes = sum(
            1 for finding in summary.findings 
            if finding.category == "config_smell"
        )
        
        if config_fixes > 0 and self.bus:
            await self.bus.publish("envrecon.scan", {
                "trigger": "arie_config_fix",
                "run_id": summary.run_id,
                "config_fixes": config_fixes
            })
            logger.info(f"[ARIE Cascade] EnvRecon notified of {config_fixes} config fixes")
