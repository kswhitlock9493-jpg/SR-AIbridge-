"""
EnvRecon ↔ Autonomy Engine & Genesis Bus Adapter
Links EnvRecon environment reconciliation with the Autonomy orchestration layer
and Genesis event bus for coordinated infrastructure management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

log = logging.getLogger(__name__)

class EnvReconAutonomyLink:
    """
    Adapter that connects EnvRecon to Autonomy Engine and Genesis Bus.
    
    Enables:
    - Autonomy-triggered environment reconciliation
    - Genesis event notifications on env drift detection
    - Coordinated environment healing workflows
    - Integration with deployment events
    """
    
    def __init__(self):
        self.autonomy_enabled = False
        self.genesis_enabled = False
        self._initialize()
    
    def _initialize(self):
        """Initialize connections to Autonomy and Genesis if available"""
        try:
            from bridge_backend.bridge_core.engines.autonomy.service import AutonomyEngine
            self.autonomy_enabled = True
            log.info("[EnvRecon→Autonomy] Link established")
        except ImportError:
            log.debug("[EnvRecon→Autonomy] Autonomy engine not available")
        
        try:
            from bridge_backend.genesis.bus import genesis_bus
            self.genesis_enabled = True
            log.info("[EnvRecon→Genesis] Link established")
        except ImportError:
            log.debug("[EnvRecon→Genesis] Genesis bus not available")
    
    async def notify_drift_detected(self, report: Dict[str, Any]) -> None:
        """
        Notify Genesis bus when environment drift is detected
        
        Args:
            report: EnvRecon reconciliation report with drift information
        """
        if not self.genesis_enabled:
            return
        
        try:
            from bridge_backend.genesis.bus import genesis_bus
            
            # Calculate drift metrics
            missing_render = len(report.get("missing_in_render", []))
            missing_netlify = len(report.get("missing_in_netlify", []))
            missing_github = len(report.get("missing_in_github", []))
            conflicts = len(report.get("conflicts", {}))
            
            total_drift = missing_render + missing_netlify + missing_github + conflicts
            
            if total_drift > 0:
                await genesis_bus.publish("genesis.heal.env", {
                    "type": "ENVRECON_DRIFT_DETECTED",
                    "source": "envrecon.core",
                    "missing_in_render": missing_render,
                    "missing_in_netlify": missing_netlify,
                    "missing_in_github": missing_github,
                    "conflicts": conflicts,
                    "total_drift": total_drift,
                    "timestamp": report.get("timestamp"),
                    "summary": report.get("summary", {})
                })
                log.info(f"[EnvRecon→Genesis] Drift notification sent: {total_drift} issues detected")
        except Exception as e:
            log.warning(f"[EnvRecon→Genesis] Failed to notify drift: {e}")
    
    async def notify_reconciliation_complete(self, report: Dict[str, Any]) -> None:
        """
        Notify Genesis bus when reconciliation completes
        
        Args:
            report: EnvRecon reconciliation report
        """
        if not self.genesis_enabled:
            return
        
        try:
            from bridge_backend.genesis.bus import genesis_bus
            
            await genesis_bus.publish("genesis.echo", {
                "type": "ENVRECON_AUDIT_COMPLETE",
                "source": "envrecon.core",
                "total_keys": report.get("summary", {}).get("total_keys", 0),
                "platform_counts": {
                    "local": report.get("summary", {}).get("local_count", 0),
                    "render": report.get("summary", {}).get("render_count", 0),
                    "netlify": report.get("summary", {}).get("netlify_count", 0),
                    "github": report.get("summary", {}).get("github_count", 0),
                },
                "timestamp": report.get("timestamp")
            })
            log.info("[EnvRecon→Genesis] Audit complete notification sent")
        except Exception as e:
            log.warning(f"[EnvRecon→Genesis] Failed to notify completion: {e}")
    
    async def notify_heal_complete(self, heal_result: Dict[str, Any], report: Dict[str, Any]) -> None:
        """
        Notify Genesis bus when auto-healing completes
        
        Args:
            heal_result: Result from auto-heal operation
            report: EnvRecon reconciliation report
        """
        if not self.genesis_enabled:
            return
        
        try:
            from bridge_backend.genesis.bus import genesis_bus
            
            healed_count = len(heal_result.get("healed", []))
            
            if healed_count > 0:
                await genesis_bus.publish("genesis.heal.env", {
                    "type": "ENVRECON_HEAL_COMPLETE",
                    "source": "envrecon.autoheal",
                    "healed_count": healed_count,
                    "healed_variables": heal_result.get("healed", []),
                    "depth": heal_result.get("depth", 0),
                    "timestamp": report.get("timestamp")
                })
                log.info(f"[EnvRecon→Genesis] Heal complete notification sent: {healed_count} variables healed")
        except Exception as e:
            log.warning(f"[EnvRecon→Genesis] Failed to notify heal complete: {e}")
    
    async def register_autonomy_trigger(self) -> None:
        """
        Register EnvRecon as an Autonomy-triggered task
        Allows Autonomy engine to trigger env reconciliation on-demand
        """
        if not self.autonomy_enabled:
            return
        
        try:
            # Register with Genesis for deployment events
            if self.genesis_enabled:
                from bridge_backend.genesis.bus import genesis_bus
                
                # Subscribe to deployment success events to trigger reconciliation
                await genesis_bus.subscribe("deploy.platform.success", self._on_deployment_success)
                log.info("[EnvRecon→Autonomy] Registered deployment event handlers")
        except Exception as e:
            log.warning(f"[EnvRecon→Autonomy] Failed to register: {e}")
    
    async def _on_deployment_success(self, event: Dict[str, Any]) -> None:
        """
        Handle deployment success events by triggering environment reconciliation
        
        Args:
            event: Deployment success event from Genesis bus
        """
        platform = event.get("platform", "unknown")
        log.info(f"[EnvRecon→Autonomy] Deployment success detected on {platform}, triggering reconciliation")
        
        try:
            # Trigger reconciliation audit
            from bridge_backend.engines.envrecon.core import EnvReconEngine
            engine = EnvReconEngine()
            report = await engine.reconcile()
            
            # Notify about the audit
            await self.notify_reconciliation_complete(report)
            
            # Check for drift and notify if found
            await self.notify_drift_detected(report)
            
        except Exception as e:
            log.error(f"[EnvRecon→Autonomy] Failed to handle deployment event: {e}")
    
    async def trigger_emergency_sync(self) -> Dict[str, Any]:
        """
        Trigger immediate environment reconciliation (emergency mode)
        
        Returns:
            Reconciliation report
        """
        log.info("[EnvRecon→Autonomy] Emergency sync triggered")
        
        try:
            from bridge_backend.engines.envrecon.core import EnvReconEngine
            from bridge_backend.engines.envrecon.autoheal import autoheal
            
            # Run reconciliation
            engine = EnvReconEngine()
            report = await engine.reconcile()
            
            # Attempt auto-heal
            heal_result = await autoheal.heal_environment(report)
            report["autofixed"] = heal_result.get("healed", [])
            engine.save_report(report)
            
            # Notify Genesis
            await self.notify_reconciliation_complete(report)
            await self.notify_drift_detected(report)
            await self.notify_heal_complete(heal_result, report)
            
            return {
                "success": True,
                "report": report,
                "heal_summary": heal_result
            }
        except Exception as e:
            log.error(f"[EnvRecon→Autonomy] Emergency sync failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Singleton instance
envrecon_autonomy_link = EnvReconAutonomyLink()
