"""
TDE-X v2 Deploy Orchestrator
Resumable deployment stages with Genesis integration

Stages:
1. post_boot - Fast essential initialization
2. warm_caches - Cache warming and preloading
3. index_assets - Asset indexing and embeddings
4. scan_federation - Federation discovery and sync
"""
import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Configuration
TDE_MAX_STAGE_RUNTIME_SECS = int(os.getenv("TDE_MAX_STAGE_RUNTIME_SECS", "900"))  # 15 minutes
TDE_RESUME_ON_BOOT = os.getenv("TDE_RESUME_ON_BOOT", "true").lower() == "true"
TDE_STATE_PATH = Path("bridge_backend/.genesis/tde_state.json")

# Ensure state directory exists
TDE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


class StageStatus:
    """Stage status constants"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TDEOrchestrator:
    """
    TDE-X v2 orchestrator with resumable stages
    
    Features:
    - Background execution (doesn't block boot)
    - Resumable stages (survives restarts)
    - Genesis event integration
    - Auto-healing on failure
    - Progress persistence
    """
    
    def __init__(self):
        self._stages = ["post_boot", "warm_caches", "index_assets", "scan_federation"]
        self._state: Dict[str, Any] = {
            "stages": {stage: {"status": StageStatus.PENDING} for stage in self._stages},
            "started_at": None,
            "completed_at": None,
        }
        self._load_state()
    
    def _load_state(self):
        """Load persisted state"""
        if TDE_STATE_PATH.exists():
            try:
                self._state = json.loads(TDE_STATE_PATH.read_text())
                logger.info(f"📂 Loaded TDE-X state: {len(self._state['stages'])} stages")
            except Exception as e:
                logger.error(f"❌ Failed to load TDE-X state: {e}")
    
    def _save_state(self):
        """Persist current state"""
        try:
            TDE_STATE_PATH.write_text(json.dumps(self._state, indent=2))
            logger.debug("💾 Saved TDE-X state")
        except Exception as e:
            logger.error(f"❌ Failed to save TDE-X state: {e}")
    
    async def run(self):
        """
        Run all deployment stages in background
        
        This is called during app startup but doesn't block.
        Heavy work is deferred to background tasks.
        """
        logger.info("🚀 TDE-X v2 orchestrator starting...")
        
        # Emit deploy.tde.orchestrator.started
        try:
            from bridge_backend.genesis.adapters import emit_control
            await emit_control(
                topic="deploy.tde.orchestrator.started",
                source="deploy.tde",
                payload={"stages": self._stages}
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to emit orchestrator start event: {e}")
        
        self._state["started_at"] = datetime.now(timezone.utc).isoformat()
        self._save_state()
        
        # Run stages sequentially in background
        asyncio.create_task(self._run_stages())
        
        logger.info("✅ TDE-X v2 orchestrator initialized (stages running in background)")
    
    async def _run_stages(self):
        """Execute all stages sequentially"""
        for stage_name in self._stages:
            await self._run_stage(stage_name)
        
        self._state["completed_at"] = datetime.now(timezone.utc).isoformat()
        self._save_state()
        
        # Emit completion
        try:
            from bridge_backend.genesis.adapters import emit_control
            await emit_control(
                topic="deploy.tde.orchestrator.completed",
                source="deploy.tde",
                payload={
                    "stages": {k: v["status"] for k, v in self._state["stages"].items()},
                    "duration_secs": (
                        datetime.now(timezone.utc) - 
                        datetime.fromisoformat(self._state["started_at"])
                    ).total_seconds() if self._state["started_at"] else None
                }
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to emit orchestrator completion event: {e}")
        
        logger.info("🎉 TDE-X v2 orchestration complete")
    
    async def _run_stage(self, stage_name: str):
        """Execute a single stage"""
        stage = self._state["stages"][stage_name]
        
        # Check if already completed
        if TDE_RESUME_ON_BOOT and stage["status"] == StageStatus.COMPLETED:
            logger.info(f"⏭️ Skipping completed stage: {stage_name}")
            return
        
        # Mark as running
        stage["status"] = StageStatus.RUNNING
        stage["started_at"] = datetime.now(timezone.utc).isoformat()
        self._save_state()
        
        # Emit stage started
        try:
            from bridge_backend.genesis.adapters import deploy_stage_started
            await deploy_stage_started(stage_name, {"attempt": stage.get("attempts", 0) + 1})
        except Exception as e:
            logger.warning(f"⚠️ Failed to emit stage start event: {e}")
        
        logger.info(f"▶️ Running stage: {stage_name}")
        
        # Execute stage
        try:
            await asyncio.wait_for(
                self._execute_stage(stage_name),
                timeout=TDE_MAX_STAGE_RUNTIME_SECS
            )
            
            # Mark as completed
            stage["status"] = StageStatus.COMPLETED
            stage["completed_at"] = datetime.now(timezone.utc).isoformat()
            stage["attempts"] = stage.get("attempts", 0) + 1
            self._save_state()
            
            # Emit stage completed
            try:
                from bridge_backend.genesis.adapters import deploy_stage_completed
                await deploy_stage_completed(stage_name)
            except Exception as e:
                logger.warning(f"⚠️ Failed to emit stage completion event: {e}")
            
            logger.info(f"✅ Stage completed: {stage_name}")
            
        except asyncio.TimeoutError:
            stage["status"] = StageStatus.FAILED
            stage["error"] = f"Timeout after {TDE_MAX_STAGE_RUNTIME_SECS}s"
            stage["attempts"] = stage.get("attempts", 0) + 1
            self._save_state()
            
            logger.error(f"❌ Stage timeout: {stage_name}")
            
            # Emit heal event
            try:
                from bridge_backend.genesis.adapters import deploy_failed
                await deploy_failed(stage_name, {"error": "timeout", "timeout_secs": TDE_MAX_STAGE_RUNTIME_SECS})
            except Exception as e:
                logger.warning(f"⚠️ Failed to emit heal event: {e}")
            
        except Exception as e:
            stage["status"] = StageStatus.FAILED
            stage["error"] = str(e)
            stage["attempts"] = stage.get("attempts", 0) + 1
            self._save_state()
            
            logger.error(f"❌ Stage failed: {stage_name}: {e}")
            
            # Emit heal event
            try:
                from bridge_backend.genesis.adapters import deploy_failed
                await deploy_failed(stage_name, {"error": str(e), "stage": stage_name})
            except Exception as ex:
                logger.warning(f"⚠️ Failed to emit heal event: {ex}")
    
    async def _execute_stage(self, stage_name: str):
        """Execute stage logic"""
        # Import stage module and run
        try:
            if stage_name == "post_boot":
                from .stages.post_boot import run_post_boot
                await run_post_boot()
            elif stage_name == "warm_caches":
                from .stages.warm_caches import run_warm_caches
                await run_warm_caches()
            elif stage_name == "index_assets":
                from .stages.index_assets import run_index_assets
                await run_index_assets()
            elif stage_name == "scan_federation":
                from .stages.scan_federation import run_scan_federation
                await run_scan_federation()
            else:
                logger.warning(f"⚠️ Unknown stage: {stage_name}")
        except ImportError as e:
            logger.warning(f"⚠️ Stage {stage_name} not implemented: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            "stages": self._state["stages"],
            "started_at": self._state.get("started_at"),
            "completed_at": self._state.get("completed_at"),
            "resume_on_boot": TDE_RESUME_ON_BOOT,
            "max_stage_runtime_secs": TDE_MAX_STAGE_RUNTIME_SECS,
        }


# Global orchestrator instance
tde_orchestrator = TDEOrchestrator()
