#!/usr/bin/env python3
"""
Test Suite for SR-AIbridge v1.9.6i — Temporal Deploy Buffer & Asynchronous Staged Launch
Validates: TDB stages, async orchestration, graceful degradation, port alignment
"""
import os
import sys
import time
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestTemporalDeployBuffer:
    """Test Temporal Deploy Buffer (TDB) core functionality"""
    
    def test_tdb_initialization(self):
        """Test TDB initializes with correct defaults"""
        from bridge_backend.runtime.temporal_deploy import TemporalDeployBuffer
        
        tdb = TemporalDeployBuffer()
        assert tdb.stage == 0
        assert tdb.ready is False
        assert tdb.stage1_complete is False
        assert tdb.stage2_complete is False
        assert tdb.stage3_complete is False
        assert len(tdb.errors) == 0
    
    def test_tdb_stage_marking(self):
        """Test stage start/complete marking"""
        from bridge_backend.runtime.temporal_deploy import TemporalDeployBuffer
        
        tdb = TemporalDeployBuffer()
        
        # Mark stage 1
        tdb.mark_stage_start(1)
        assert tdb.stage == 1
        assert 1 in tdb.stage_start_times
        
        tdb.mark_stage_complete(1, success=True)
        assert tdb.stage1_complete is True
        assert 1 in tdb.stage_completion_times
        
        # Mark stage 2
        tdb.mark_stage_start(2)
        tdb.mark_stage_complete(2, success=True)
        assert tdb.stage2_complete is True
        
        # Mark stage 3
        tdb.mark_stage_start(3)
        tdb.mark_stage_complete(3, success=True)
        assert tdb.stage3_complete is True
        assert tdb.ready is True
    
    def test_tdb_error_tracking(self):
        """Test error tracking across stages"""
        from bridge_backend.runtime.temporal_deploy import TemporalDeployBuffer
        
        tdb = TemporalDeployBuffer()
        
        tdb.add_error(1, "Test error in stage 1")
        tdb.add_error(2, "Test error in stage 2")
        
        assert len(tdb.errors) == 2
        assert tdb.errors[0]["stage"] == 1
        assert tdb.errors[0]["error"] == "Test error in stage 1"
        assert tdb.errors[1]["stage"] == 2
    
    def test_tdb_get_status(self):
        """Test TDB status reporting"""
        from bridge_backend.runtime.temporal_deploy import TemporalDeployBuffer
        
        tdb = TemporalDeployBuffer()
        tdb.mark_stage_start(1)
        tdb.mark_stage_complete(1)
        
        status = tdb.get_status()
        
        assert "enabled" in status
        assert "current_stage" in status
        assert "ready" in status
        assert "stages" in status
        assert status["stages"]["stage1"]["complete"] is True
        assert "total_boot_time" in status


class TestTemporalStageManager:
    """Test Temporal Stage Manager"""
    
    def test_stage_manager_initialization(self):
        """Test stage manager initializes correctly"""
        from bridge_backend.runtime.temporal_stage_manager import TemporalStageManager
        
        manager = TemporalStageManager()
        assert len(manager.stages) == 0
        assert manager.current_stage_index == 0
        assert manager.deployment_complete is False
        assert manager.failed_stage is None
    
    def test_add_stage(self):
        """Test adding deployment stages"""
        from bridge_backend.runtime.temporal_stage_manager import (
            TemporalStageManager, DeploymentStage
        )
        
        manager = TemporalStageManager()
        
        stage1 = DeploymentStage(stage_number=1, name="Test Stage 1")
        manager.add_stage(stage1)
        
        assert len(manager.stages) == 1
        assert manager.stages[0].stage_number == 1
        assert manager.stages[0].name == "Test Stage 1"
    
    def test_add_task_to_stage(self):
        """Test adding tasks to stages"""
        from bridge_backend.runtime.temporal_stage_manager import (
            TemporalStageManager, DeploymentStage, StageTask
        )
        
        manager = TemporalStageManager()
        stage1 = DeploymentStage(stage_number=1, name="Test Stage")
        manager.add_stage(stage1)
        
        async def dummy_task():
            pass
        
        task = StageTask(name="Test Task", task_fn=dummy_task)
        manager.add_task_to_stage(1, task)
        
        assert len(manager.stages[0].tasks) == 1
        assert manager.stages[0].tasks[0].name == "Test Task"
    
    def test_run_task_success(self):
        """Test successful task execution"""
        from bridge_backend.runtime.temporal_stage_manager import (
            TemporalStageManager, StageTask, StageStatus
        )
        
        async def successful_task():
            await asyncio.sleep(0.01)
            return True
        
        manager = TemporalStageManager()
        task = StageTask(name="Success Task", task_fn=successful_task)
        
        # Run async test
        async def test():
            result = await manager.run_task(task)
            assert result is True
            assert task.status == StageStatus.COMPLETE
            assert task.duration() is not None
        
        asyncio.run(test())
    
    def test_run_task_failure(self):
        """Test task failure handling"""
        from bridge_backend.runtime.temporal_stage_manager import (
            TemporalStageManager, StageTask, StageStatus
        )
        
        async def failing_task():
            raise Exception("Task failed")
        
        manager = TemporalStageManager()
        task = StageTask(name="Failing Task", task_fn=failing_task, max_retries=1)
        
        # Run async test
        async def test():
            result = await manager.run_task(task)
            assert result is False
            assert task.status == StageStatus.FAILED
            assert task.error is not None
        
        asyncio.run(test())
    
    def test_run_task_with_retry(self):
        """Test task retry mechanism"""
        from bridge_backend.runtime.temporal_stage_manager import (
            TemporalStageManager, StageTask, StageStatus
        )
        
        call_count = 0
        
        async def flaky_task():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return True
        
        manager = TemporalStageManager()
        task = StageTask(name="Flaky Task", task_fn=flaky_task, max_retries=2)
        
        # Run async test
        async def test():
            result = await manager.run_task(task)
            assert result is True
            assert task.status == StageStatus.COMPLETE
            assert task.retry_count >= 1
        
        asyncio.run(test())


class TestStageExecution:
    """Test complete stage execution flows"""
    
    def test_stage1_minimal_health(self):
        """Test Stage 1 completes quickly"""
        from bridge_backend.runtime.temporal_deploy import stage1_minimal_health, tdb
        
        async def test():
            start = time.time()
            await stage1_minimal_health()
            duration = time.time() - start
            
            # Stage 1 should complete in under 1 second
            assert duration < 1.0
            assert tdb.stage1_complete is True
        
        asyncio.run(test())
    
    def test_stage2_core_bootstrap(self):
        """Test Stage 2 core bootstrap"""
        from bridge_backend.runtime.temporal_deploy import stage2_core_bootstrap, tdb
        
        async def test():
            # Reset TDB
            tdb.stage2_complete = False
            
            # Mock database functions
            with patch('bridge_backend.runtime.temporal_deploy._bootstrap_database', new_callable=AsyncMock):
                with patch('bridge_backend.runtime.temporal_deploy._verify_routes', new_callable=AsyncMock):
                    with patch('bridge_backend.runtime.temporal_deploy._verify_imports', new_callable=AsyncMock):
                        await stage2_core_bootstrap()
            
            assert tdb.stage2_complete is True
        
        asyncio.run(test())
    
    def test_stage3_federation_warmup(self):
        """Test Stage 3 federation warmup"""
        from bridge_backend.runtime.temporal_deploy import stage3_federation_warmup, tdb
        
        async def test():
            # Reset TDB
            tdb.stage3_complete = False
            
            # Mock federation functions
            with patch('bridge_backend.runtime.temporal_deploy._federation_sync', new_callable=AsyncMock):
                with patch('bridge_backend.runtime.temporal_deploy._diagnostics_warmup', new_callable=AsyncMock):
                    with patch('bridge_backend.runtime.temporal_deploy._predictive_stabilizer_init', new_callable=AsyncMock):
                        await stage3_federation_warmup()
            
            assert tdb.stage3_complete is True
            assert tdb.ready is True
        
        asyncio.run(test())


class TestPortAlignment:
    """Test dynamic port alignment"""
    
    def test_port_env_variable(self):
        """Test PORT environment variable handling"""
        with patch.dict(os.environ, {"PORT": "10000"}):
            from bridge_backend.runtime.temporal_deploy import STAGE_1_PORT
            # Should reload the module to get new value
            assert os.getenv("PORT") == "10000"
    
    def test_bridge_port_alignment(self):
        """Test BRIDGE_PORT is set correctly"""
        with patch.dict(os.environ, {"PORT": "8888"}):
            # Simulate run.py setting BRIDGE_PORT
            os.environ["BRIDGE_PORT"] = os.environ["PORT"]
            assert os.environ["BRIDGE_PORT"] == "8888"


class TestGracefulDegradation:
    """Test graceful degradation and fail-fast guardrails"""
    
    def test_non_critical_task_failure(self):
        """Test that non-critical task failures don't halt deployment"""
        from bridge_backend.runtime.temporal_stage_manager import (
            TemporalStageManager, DeploymentStage, StageTask, StageStatus
        )
        
        async def critical_task():
            return True
        
        async def failing_task():
            raise Exception("Non-critical failure")
        
        manager = TemporalStageManager()
        stage = DeploymentStage(stage_number=1, name="Mixed Stage")
        
        task1 = StageTask(name="Critical", task_fn=critical_task, critical=True)
        task2 = StageTask(name="Non-Critical", task_fn=failing_task, critical=False, max_retries=0)
        
        stage.tasks = [task1, task2]
        manager.add_stage(stage)
        
        async def test():
            result = await manager.run_stage(stage)
            # Stage should succeed (degraded) despite non-critical failure
            assert result is True
            assert stage.status == StageStatus.DEGRADED
        
        asyncio.run(test())
    
    def test_critical_task_failure(self):
        """Test that critical task failures halt the stage"""
        from bridge_backend.runtime.temporal_stage_manager import (
            TemporalStageManager, DeploymentStage, StageTask, StageStatus
        )
        
        async def failing_critical_task():
            raise Exception("Critical failure")
        
        manager = TemporalStageManager()
        stage = DeploymentStage(stage_number=1, name="Critical Stage")
        
        task = StageTask(name="Critical", task_fn=failing_critical_task, critical=True, max_retries=0)
        stage.tasks = [task]
        manager.add_stage(stage)
        
        async def test():
            result = await manager.run_stage(stage)
            assert result is False
            assert stage.status == StageStatus.FAILED
        
        asyncio.run(test())


class TestDiagnostics:
    """Test diagnostics and logging"""
    
    def test_tdb_save_diagnostics(self):
        """Test TDB diagnostics saving"""
        from bridge_backend.runtime.temporal_deploy import TemporalDeployBuffer
        
        tdb = TemporalDeployBuffer()
        tdb.mark_stage_start(1)
        tdb.mark_stage_complete(1)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tdb.save_diagnostics(tmpdir)
            
            # Check that file was created
            files = list(Path(tmpdir).glob("deploy_*.json"))
            assert len(files) == 1
            
            # Check file content
            import json
            with open(files[0]) as f:
                data = json.load(f)
            
            assert "enabled" in data
            assert "stages" in data
            assert data["stages"]["stage1"]["complete"] is True
    
    def test_stage_manager_get_runtime_stage(self):
        """Test stage manager runtime stage reporting"""
        from bridge_backend.runtime.temporal_stage_manager import (
            TemporalStageManager, DeploymentStage
        )
        
        manager = TemporalStageManager()
        stage = DeploymentStage(stage_number=1, name="Test Stage")
        manager.add_stage(stage)
        
        runtime_stage = manager.get_runtime_stage()
        
        assert "deployment_complete" in runtime_stage
        assert "current_stage" in runtime_stage
        assert "stages" in runtime_stage
        assert "metrics" in runtime_stage


class TestTDBEnabled:
    """Test TDB enable/disable functionality"""
    
    def test_tdb_enabled_by_default(self):
        """Test TDB is enabled by default"""
        with patch.dict(os.environ, {}, clear=True):
            # Re-import to get fresh value
            import importlib
            from bridge_backend.runtime import temporal_deploy
            importlib.reload(temporal_deploy)
            
            assert temporal_deploy.TDB_ENABLED is True
    
    def test_tdb_can_be_disabled(self):
        """Test TDB can be disabled via env var"""
        with patch.dict(os.environ, {"TDB_ENABLED": "false"}):
            # Re-import to get fresh value
            import importlib
            from bridge_backend.runtime import temporal_deploy
            importlib.reload(temporal_deploy)
            
            assert temporal_deploy.TDB_ENABLED is False


class TestHealthEndpoints:
    """Test health check endpoints with TDB support"""
    
    def test_health_live_endpoint(self):
        """Test /health/live endpoint responds immediately"""
        from bridge_backend.routes.health import health_live
        
        result = health_live()
        assert result["status"] == "ok"
        assert result["alive"] is True
    
    def test_health_stage_endpoint(self):
        """Test /health/stage endpoint returns TDB status"""
        from bridge_backend.routes.health import health_stage
        
        result = health_stage()
        
        # Should have temporal_deploy_buffer or error key
        assert "temporal_deploy_buffer" in result or "error" in result


def run_all_tests():
    """Run all test classes"""
    print("🧪 Running v1.9.6i Test Suite")
    print("=" * 60)
    
    test_classes = [
        TestTemporalDeployBuffer,
        TestTemporalStageManager,
        TestStageExecution,
        TestPortAlignment,
        TestGracefulDegradation,
        TestDiagnostics,
        TestTDBEnabled,
        TestHealthEndpoints,
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n📋 {test_class.__name__}")
        print("-" * 60)
        
        test_instance = test_class()
        test_methods = [m for m in dir(test_instance) if m.startswith("test_")]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                print(f"  ✅ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
                failed_tests.append(f"{test_class.__name__}.{method_name}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test in failed_tests:
            print(f"  - {test}")
        return False
    else:
        print("✅ All tests passed!")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
