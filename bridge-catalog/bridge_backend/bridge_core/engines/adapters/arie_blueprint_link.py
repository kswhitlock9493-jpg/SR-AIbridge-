"""
ARIE Blueprint Link - Record structural edits to BlueprintRegistry
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ARIEBlueprintLink:
    """
    Blueprint integration for ARIE
    
    Records structural edits:
    - Route map changes
    - Module ownership updates
    - Engine manifest updates
    """
    
    def __init__(self, blueprint_registry=None):
        self.blueprint_registry = blueprint_registry
    
    async def record_structural_changes(self, summary):
        """
        Record structural changes from ARIE fixes to Blueprint
        
        Args:
            summary: ARIE Summary object with fix results
        """
        if not self.blueprint_registry:
            logger.info("[ARIE Blueprint] No Blueprint registry available")
            return
        
        logger.info(f"[ARIE Blueprint] Recording structural changes for run {summary.run_id}")
        
        try:
            # Check for route-related fixes
            route_fixes = [
                f for f in summary.findings 
                if f.category == "route_integrity"
            ]
            
            if route_fixes:
                await self._update_route_maps(route_fixes)
            
            # Check for module-level changes
            module_changes = self._extract_module_changes(summary)
            if module_changes:
                await self._update_module_registry(module_changes)
            
            logger.info(f"[ARIE Blueprint] Recorded {len(route_fixes)} route fixes, {len(module_changes)} module changes")
        
        except Exception as e:
            logger.exception(f"[ARIE Blueprint] Error recording changes: {e}")
    
    async def _update_route_maps(self, route_fixes):
        """Update route maps in Blueprint"""
        for fix in route_fixes:
            logger.info(f"[ARIE Blueprint] Would update route map for {fix.file_path}")
            # Placeholder for actual Blueprint update
    
    def _extract_module_changes(self, summary) -> list:
        """Extract module-level changes from summary"""
        changes = []
        
        for patch in summary.patches:
            for file_path in patch.files_modified:
                # Determine module from file path
                if 'engines' in file_path:
                    parts = file_path.split('/')
                    if 'engines' in parts:
                        idx = parts.index('engines')
                        if idx + 1 < len(parts):
                            engine_name = parts[idx + 1]
                            changes.append({
                                "module": engine_name,
                                "file": file_path,
                                "patch_id": patch.id
                            })
        
        return changes
    
    async def _update_module_registry(self, changes):
        """Update module ownership in Blueprint"""
        if not self.blueprint_registry:
            return
        
        for change in changes:
            logger.info(f"[ARIE Blueprint] Would update module registry: {change['module']}")
            # Placeholder for actual Blueprint update
