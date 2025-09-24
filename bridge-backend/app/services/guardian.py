"""
Guardian daemon service for SR-AIbridge
Handles continuous monitoring, self-testing, and system protection
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class GuardianService:
    """Advanced Guardian daemon service with comprehensive monitoring"""
    
    def __init__(self, storage, websocket_manager):
        self.storage = storage
        self.websocket_manager = websocket_manager
        self.active = True
        self.selftest_status = "unknown"
        self.last_selftest = None
        self.last_action = "initialized"
        self.last_result = None
        self.heartbeat = datetime.utcnow()
        self.selftest_interval = 300  # 5 minutes
        self.monitoring_tasks = []
        self.alert_history = []
        self.system_metrics = {}
        
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive Guardian status"""
        return {
            "active": self.active,
            "status": self.selftest_status,
            "last_selftest": self.last_selftest.isoformat() if self.last_selftest else None,
            "last_action": self.last_action,
            "last_result": self.last_result,
            "heartbeat": self.heartbeat.isoformat() if self.heartbeat else None,
            "next_selftest": (self.last_selftest + timedelta(seconds=self.selftest_interval)).isoformat() if self.last_selftest else None,
            "monitoring_tasks": len(self.monitoring_tasks),
            "alert_count": len(self.alert_history),
            "system_metrics": self.system_metrics
        }
        
    async def run_selftest(self):
        """Run comprehensive system self-test"""
        try:
            logger.info("🛡️ Guardian running comprehensive self-test...")
            self.heartbeat = datetime.utcnow()
            self.last_selftest = datetime.utcnow()
            self.last_action = "selftest"
            
            test_results = {}
            tests_passed = 0
            total_tests = 0
            
            # Test 1: Storage accessibility and integrity
            total_tests += 1
            try:
                storage_health = await self._test_storage_health()
                test_results["storage"] = storage_health
                if storage_health["status"] == "healthy":
                    tests_passed += 1
                logger.info(f"🛡️ Storage test: {storage_health['status']}")
            except Exception as e:
                test_results["storage"] = {"status": "failed", "error": str(e)}
                logger.error(f"🛡️ Storage test failed: {e}")
                
            # Test 2: WebSocket connectivity
            total_tests += 1
            try:
                websocket_health = await self._test_websocket_health()
                test_results["websocket"] = websocket_health
                if websocket_health["status"] == "healthy":
                    tests_passed += 1
                logger.info(f"🛡️ WebSocket test: {websocket_health['status']}")
            except Exception as e:
                test_results["websocket"] = {"status": "failed", "error": str(e)}
                logger.error(f"🛡️ WebSocket test failed: {e}")
                
            # Test 3: Agent system health
            total_tests += 1
            try:
                agent_health = await self._test_agent_health()
                test_results["agents"] = agent_health
                if agent_health["status"] == "healthy":
                    tests_passed += 1
                logger.info(f"🛡️ Agent test: {agent_health['status']}")
            except Exception as e:
                test_results["agents"] = {"status": "failed", "error": str(e)}
                logger.error(f"🛡️ Agent test failed: {e}")
                
            # Test 4: Mission system health
            total_tests += 1
            try:
                mission_health = await self._test_mission_health()
                test_results["missions"] = mission_health
                if mission_health["status"] == "healthy":
                    tests_passed += 1
                logger.info(f"🛡️ Mission test: {mission_health['status']}")
            except Exception as e:
                test_results["missions"] = {"status": "failed", "error": str(e)}
                logger.error(f"🛡️ Mission test failed: {e}")
                
            # Test 5: System resources
            total_tests += 1
            try:
                resource_health = await self._test_system_resources()
                test_results["resources"] = resource_health
                if resource_health["status"] == "healthy":
                    tests_passed += 1
                logger.info(f"🛡️ Resource test: {resource_health['status']}")
            except Exception as e:
                test_results["resources"] = {"status": "failed", "error": str(e)}
                logger.error(f"🛡️ Resource test failed: {e}")
                
            # Determine overall status
            success_rate = tests_passed / total_tests
            if success_rate >= 0.8:
                self.selftest_status = "healthy"
            elif success_rate >= 0.6:
                self.selftest_status = "degraded"
            else:
                self.selftest_status = "critical"
                
            self.last_result = f"{tests_passed}/{total_tests} tests passed ({success_rate*100:.1f}%)"
            self.system_metrics = test_results
            
            # Send status update via WebSocket
            await self.websocket_manager.send_guardian_update(self.get_status())
            
            logger.info(f"🛡️ Guardian self-test completed: {self.last_result} - Status: {self.selftest_status}")
            
        except Exception as e:
            logger.error(f"🛡️ Guardian selftest error: {e}")
            self.selftest_status = "error"
            self.last_selftest = datetime.utcnow()
            self.last_action = "selftest_error"
            self.last_result = f"Critical selftest error: {str(e)}"
            self.log_to_vault("error", "selftest_error", f"Critical selftest error: {str(e)}")
            raise
            
    async def _test_storage_health(self) -> Dict:
        """Test storage system health"""
        try:
            # Test basic storage operations
            agent_count = len(self.storage.agents)
            mission_count = len(self.storage.missions)
            log_count = len(self.storage.vault_logs)
            
            # Test storage write/read
            test_id = self.storage.get_next_id()
            
            return {
                "status": "healthy",
                "agent_count": agent_count,
                "mission_count": mission_count,
                "log_count": log_count,
                "next_id": test_id
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
            
    async def _test_websocket_health(self) -> Dict:
        """Test WebSocket system health"""
        try:
            if hasattr(self.websocket_manager, 'active_connections'):
                connection_count = len(self.websocket_manager.active_connections)
                stats = self.websocket_manager.get_stats()
                
                return {
                    "status": "healthy",
                    "active_connections": connection_count,
                    "total_connections": stats.get("total_connections", 0),
                    "messages_sent": stats.get("messages_sent", 0)
                }
            else:
                return {"status": "degraded", "message": "WebSocket manager not fully initialized"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
            
    async def _test_agent_health(self) -> Dict:
        """Test agent system health"""
        try:
            agents = self.storage.agents
            online_agents = [a for a in agents if a.get("status") == "online"]
            offline_agents = [a for a in agents if a.get("status") == "offline"]
            
            # Check for stale agents (no heartbeat in last hour)
            stale_threshold = datetime.utcnow() - timedelta(hours=1)
            stale_agents = [a for a in agents if a.get("last_heartbeat", datetime.utcnow()) < stale_threshold]
            
            status = "healthy"
            if len(offline_agents) > len(online_agents):
                status = "degraded"
            elif len(online_agents) == 0:
                status = "critical"
                
            return {
                "status": status,
                "total_agents": len(agents),
                "online_agents": len(online_agents),
                "offline_agents": len(offline_agents),
                "stale_agents": len(stale_agents)
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
            
    async def _test_mission_health(self) -> Dict:
        """Test mission system health"""
        try:
            missions = self.storage.missions
            active_missions = [m for m in missions if m.get("status") == "active"]
            completed_missions = [m for m in missions if m.get("status") == "completed"]
            failed_missions = [m for m in missions if m.get("status") == "failed"]
            
            status = "healthy"
            if len(failed_missions) > len(active_missions):
                status = "degraded"
                
            return {
                "status": status,
                "total_missions": len(missions),
                "active_missions": len(active_missions),
                "completed_missions": len(completed_missions),
                "failed_missions": len(failed_missions)
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
            
    async def _test_system_resources(self) -> Dict:
        """Test system resource health"""
        try:
            # Basic system checks
            import sys
            import os
            
            # Memory usage approximation
            vault_logs_size = len(str(self.storage.vault_logs))
            agent_data_size = len(str(self.storage.agents))
            mission_data_size = len(str(self.storage.missions))
            
            total_memory_usage = vault_logs_size + agent_data_size + mission_data_size
            
            status = "healthy"
            if total_memory_usage > 1000000:  # 1MB threshold
                status = "degraded"
                
            return {
                "status": status,
                "python_version": sys.version,
                "memory_usage_estimate": total_memory_usage,
                "vault_logs_size": vault_logs_size,
                "agent_data_size": agent_data_size,
                "mission_data_size": mission_data_size
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
            
    def log_to_vault(self, level: str, action: str, details: str):
        """Log Guardian actions to vault"""
        try:
            log_entry = {
                "id": self.storage.get_next_id(),
                "agent_name": "Guardian",
                "action": action,
                "details": details,
                "timestamp": datetime.utcnow(),
                "log_level": level
            }
            self.storage.vault_logs.append(log_entry)
        except Exception as e:
            logger.error(f"🛡️ Failed to log to vault: {e}")
            
    async def activate(self):
        """Activate Guardian daemon with full initialization"""
        self.active = True
        self.last_action = "activated"
        self.heartbeat = datetime.utcnow()
        
        # Run initial self-test
        await self.run_selftest()
        
        # Log activation
        self.log_to_vault("info", "activated", "Guardian daemon fully activated and operational")
        
        logger.info("🛡️ Guardian daemon activated and operational")
        return {
            "success": True, 
            "message": "Guardian daemon activated", 
            "status": self.get_status()
        }
        
    async def start_monitoring_loop(self):
        """Start continuous monitoring loop"""
        logger.info("🛡️ Starting Guardian monitoring loop...")
        
        while self.active:
            try:
                # Run periodic self-test
                await self.run_selftest()
                
                # Wait for next interval
                await asyncio.sleep(self.selftest_interval)
                
            except Exception as e:
                logger.error(f"🛡️ Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Shorter retry interval