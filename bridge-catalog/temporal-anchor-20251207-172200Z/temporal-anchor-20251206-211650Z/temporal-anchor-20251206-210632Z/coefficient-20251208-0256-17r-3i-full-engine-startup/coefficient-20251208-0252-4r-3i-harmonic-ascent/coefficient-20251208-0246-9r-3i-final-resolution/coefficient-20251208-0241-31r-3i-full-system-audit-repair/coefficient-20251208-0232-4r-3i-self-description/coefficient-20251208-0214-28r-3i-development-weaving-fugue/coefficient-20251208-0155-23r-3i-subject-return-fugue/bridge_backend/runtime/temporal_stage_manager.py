#!/usr/bin/env python3
"""
SR-AIbridge v1.9.6i — Temporal Stage Manager
Orchestrates asynchronous staged deployment with dependency tracking
"""
import os
import asyncio
import logging
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class StageStatus(Enum):
    """Stage execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    DEGRADED = "degraded"  # Partial success with errors

@dataclass
class StageTask:
    """Represents a single task within a deployment stage"""
    name: str
    task_fn: Callable
    critical: bool = False  # If True, stage fails if this task fails
    timeout: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 2
    status: StageStatus = StageStatus.PENDING
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def duration(self) -> Optional[float]:
        """Calculate task duration"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

@dataclass
class DeploymentStage:
    """Represents a deployment stage with multiple tasks"""
    stage_number: int
    name: str
    tasks: List[StageTask] = field(default_factory=list)
    status: StageStatus = StageStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    required: bool = True  # If False, failure doesn't halt deployment
    
    def duration(self) -> Optional[float]:
        """Calculate stage duration"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def is_complete(self) -> bool:
        """Check if all tasks are complete or degraded"""
        return self.status in (StageStatus.COMPLETE, StageStatus.DEGRADED)
    
    def has_critical_failure(self) -> bool:
        """Check if any critical task failed"""
        return any(
            task.critical and task.status == StageStatus.FAILED
            for task in self.tasks
        )

class TemporalStageManager:
    """
    Manages the execution of deployment stages with:
    - Dependency tracking
    - Parallel task execution within stages
    - Fail-fast with graceful degradation
    - Cross-healing and retry logic
    """
    
    def __init__(self):
        self.stages: List[DeploymentStage] = []
        self.current_stage_index = 0
        self.deployment_start = time.time()
        self.deployment_complete = False
        self.failed_stage: Optional[int] = None
        
        # Metrics
        self.total_tasks_run = 0
        self.total_tasks_failed = 0
        self.total_retries = 0
        
    def add_stage(self, stage: DeploymentStage):
        """Add a deployment stage"""
        self.stages.append(stage)
        logger.info(f"[STAGE_MGR] Registered stage {stage.stage_number}: {stage.name}")
        
    def add_task_to_stage(self, stage_number: int, task: StageTask):
        """Add a task to a specific stage"""
        for stage in self.stages:
            if stage.stage_number == stage_number:
                stage.tasks.append(task)
                logger.debug(f"[STAGE_MGR] Added task '{task.name}' to stage {stage_number}")
                return
        logger.warning(f"[STAGE_MGR] Stage {stage_number} not found, cannot add task")
        
    async def run_task(self, task: StageTask) -> bool:
        """
        Run a single task with retry logic
        
        Returns:
            True if task succeeded, False if failed
        """
        task.status = StageStatus.RUNNING
        task.start_time = time.time()
        
        for attempt in range(task.max_retries + 1):
            try:
                logger.info(f"[STAGE_MGR] Running task: {task.name} (attempt {attempt + 1})")
                
                # Apply timeout if specified
                if task.timeout:
                    await asyncio.wait_for(task.task_fn(), timeout=task.timeout)
                else:
                    await task.task_fn()
                
                # Success
                task.status = StageStatus.COMPLETE
                task.end_time = time.time()
                self.total_tasks_run += 1
                logger.info(f"[STAGE_MGR] ✅ Task complete: {task.name} ({task.duration():.2f}s)")
                return True
                
            except asyncio.TimeoutError:
                task.error = f"Timeout after {task.timeout}s"
                logger.warning(f"[STAGE_MGR] ⏱️ Task timeout: {task.name}")
                
            except Exception as e:
                task.error = str(e)
                logger.warning(f"[STAGE_MGR] ⚠️ Task error: {task.name} - {e}")
                
            # Retry logic
            if attempt < task.max_retries:
                task.retry_count += 1
                self.total_retries += 1
                backoff = 2 ** attempt  # Exponential backoff
                logger.info(f"[STAGE_MGR] Retrying {task.name} in {backoff}s...")
                await asyncio.sleep(backoff)
        
        # All retries exhausted
        task.status = StageStatus.FAILED
        task.end_time = time.time()
        self.total_tasks_failed += 1
        logger.error(f"[STAGE_MGR] ❌ Task failed: {task.name} after {task.max_retries + 1} attempts")
        return False
        
    async def run_stage(self, stage: DeploymentStage) -> bool:
        """
        Run all tasks in a stage concurrently
        
        Returns:
            True if stage succeeded, False if failed
        """
        stage.status = StageStatus.RUNNING
        stage.start_time = time.time()
        
        logger.info(f"[STAGE_MGR] 🚀 Starting stage {stage.stage_number}: {stage.name}")
        
        # Run all tasks concurrently
        task_results = await asyncio.gather(
            *[self.run_task(task) for task in stage.tasks],
            return_exceptions=True
        )
        
        stage.end_time = time.time()
        
        # Check results
        critical_failures = stage.has_critical_failure()
        all_tasks_succeeded = all(
            task.status == StageStatus.COMPLETE
            for task in stage.tasks
        )
        
        if critical_failures:
            stage.status = StageStatus.FAILED
            logger.error(f"[STAGE_MGR] ❌ Stage {stage.stage_number} failed (critical task failure)")
            return False
        elif all_tasks_succeeded:
            stage.status = StageStatus.COMPLETE
            logger.info(f"[STAGE_MGR] ✅ Stage {stage.stage_number} complete ({stage.duration():.2f}s)")
            return True
        else:
            # Some non-critical tasks failed
            stage.status = StageStatus.DEGRADED
            logger.warning(f"[STAGE_MGR] ⚠️ Stage {stage.stage_number} degraded (non-critical failures)")
            return True  # Continue with degraded functionality
            
    async def run_all_stages(self):
        """Execute all deployment stages in sequence"""
        logger.info("[STAGE_MGR] 🌊 Starting temporal deployment sequence")
        
        for i, stage in enumerate(self.stages):
            self.current_stage_index = i
            
            success = await self.run_stage(stage)
            
            if not success and stage.required:
                # Critical stage failed, halt deployment
                self.failed_stage = stage.stage_number
                logger.error(f"[STAGE_MGR] 🛑 Deployment halted at stage {stage.stage_number}")
                break
                
            # Add small delay between stages for stability
            await asyncio.sleep(0.5)
        
        self.deployment_complete = True
        total_time = time.time() - self.deployment_start
        
        if self.failed_stage is None:
            logger.info(f"[STAGE_MGR] 🎉 Deployment complete in {total_time:.2f}s")
        else:
            logger.error(f"[STAGE_MGR] ⚠️ Deployment incomplete (failed at stage {self.failed_stage})")
            
        self._log_summary()
        
    def _log_summary(self):
        """Log deployment summary"""
        logger.info(f"[STAGE_MGR] === Deployment Summary ===")
        logger.info(f"[STAGE_MGR] Total stages: {len(self.stages)}")
        logger.info(f"[STAGE_MGR] Total tasks run: {self.total_tasks_run}")
        logger.info(f"[STAGE_MGR] Total tasks failed: {self.total_tasks_failed}")
        logger.info(f"[STAGE_MGR] Total retries: {self.total_retries}")
        
        for stage in self.stages:
            status_icon = {
                StageStatus.COMPLETE: "✅",
                StageStatus.DEGRADED: "⚠️",
                StageStatus.FAILED: "❌",
                StageStatus.PENDING: "⏸️",
                StageStatus.RUNNING: "🏃"
            }.get(stage.status, "❓")
            
            duration = f"{stage.duration():.2f}s" if stage.duration() else "N/A"
            logger.info(f"[STAGE_MGR] Stage {stage.stage_number} ({stage.name}): {status_icon} {stage.status.value} ({duration})")
            
    def get_runtime_stage(self) -> Dict[str, Any]:
        """Get current runtime stage information for diagnostics"""
        current_stage = self.stages[self.current_stage_index] if self.current_stage_index < len(self.stages) else None
        
        return {
            "deployment_complete": self.deployment_complete,
            "current_stage": current_stage.stage_number if current_stage else None,
            "current_stage_name": current_stage.name if current_stage else None,
            "failed_stage": self.failed_stage,
            "total_deployment_time": time.time() - self.deployment_start,
            "stages": [
                {
                    "number": stage.stage_number,
                    "name": stage.name,
                    "status": stage.status.value,
                    "duration": stage.duration(),
                    "tasks": [
                        {
                            "name": task.name,
                            "status": task.status.value,
                            "duration": task.duration(),
                            "retries": task.retry_count,
                            "error": task.error
                        }
                        for task in stage.tasks
                    ]
                }
                for stage in self.stages
            ],
            "metrics": {
                "total_tasks_run": self.total_tasks_run,
                "total_tasks_failed": self.total_tasks_failed,
                "total_retries": self.total_retries
            }
        }
        
    def save_diagnostics(self, path: str = "bridge_backend/diagnostics/runtime_stage.json"):
        """Save stage diagnostics to file"""
        import json
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, "w") as f:
            json.dump(self.get_runtime_stage(), f, indent=2)
            
        logger.info(f"[STAGE_MGR] Diagnostics saved to {path}")

# Global stage manager instance
stage_manager = TemporalStageManager()
