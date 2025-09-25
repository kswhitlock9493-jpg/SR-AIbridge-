"""
Robust seeding functionality for SR-AIbridge backend
Provides initial demo data and system initialization
"""
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from db import db_manager


logger = logging.getLogger(__name__)


class DataSeeder:
    """Handles seeding of initial demo data"""
    
    def __init__(self):
        self.db = db_manager
        
    async def seed_initial_data(self) -> Dict[str, Any]:
        """
        Seed initial demo data including guardians, agents, missions, and logs
        Returns detailed seeding results
        """
        try:
            logger.info("🌱 Starting initial data seeding...")
            
            # Check if data already exists
            existing_data = await self._check_existing_data()
            if existing_data["has_data"]:
                logger.info("ℹ️ Demo data already exists, skipping seeding")
                return {
                    "status": "success",
                    "skipped": True,
                    "message": "Demo data already exists",
                    "existing_counts": existing_data["counts"]
                }
            
            # Seed data step by step
            results = {}
            
            # 1. Seed Guardians
            guardian_result = await self._seed_guardians()
            results["guardians"] = guardian_result
            
            # 2. Seed Agents
            agents_result = await self._seed_agents()
            results["agents"] = agents_result
            
            # 3. Seed Missions
            missions_result = await self._seed_missions()
            results["missions"] = missions_result
            
            # 4. Seed Vault Logs
            logs_result = await self._seed_vault_logs()
            results["vault_logs"] = logs_result
            
            # Compile final results
            seeded_items = []
            total_created = 0
            
            for category, result in results.items():
                if result.get("created", 0) > 0:
                    seeded_items.append(f"{result['created']} {category}")
                    total_created += result["created"]
            
            logger.info(f"✅ Seeding completed: {total_created} items created")
            
            # Get system status for response
            system_status = await self._get_system_summary()
            
            return {
                "status": "success",
                "skipped": False,
                "message": "Initial demo data seeded successfully",
                "seeded_items": seeded_items,
                "total_created": total_created,
                "results": results,
                **system_status
            }
            
        except Exception as e:
            logger.error(f"❌ Seeding failed: {e}")
            return {
                "status": "error",
                "message": f"Seeding failed: {str(e)}",
                "error": str(e)
            }
    
    async def _check_existing_data(self) -> Dict[str, Any]:
        """Check if demo data already exists"""
        try:
            guardians = await self.db.get_guardians()
            agents = await self.db.get_agents()
            missions = await self.db.get_missions()
            logs = await self.db.get_vault_logs(limit=1)
            
            counts = {
                "guardians": len(guardians),
                "agents": len(agents),
                "missions": len(missions),
                "vault_logs": len(logs)
            }
            
            has_data = any(count > 0 for count in counts.values())
            
            return {
                "has_data": has_data,
                "counts": counts
            }
        except Exception as e:
            logger.warning(f"Could not check existing data: {e}")
            return {"has_data": False, "counts": {}}
    
    async def _seed_guardians(self) -> Dict[str, Any]:
        """Seed initial guardian data"""
        try:
            logger.info("🛡️ Seeding guardians...")
            
            guardian_data = {
                "name": "System Guardian Alpha",
                "status": "active",
                "health_score": 95.0,
                "last_action": "System initialization and monitoring activated"
            }
            
            result = await self.db.create_guardian(guardian_data)
            if result["status"] == "success":
                logger.info(f"✅ Created guardian: {guardian_data['name']}")
                return {"created": 1, "guardian": result["guardian"]}
            else:
                logger.warning(f"⚠️ Guardian creation failed: {result.get('error', 'Unknown error')}")
                return {"created": 0, "error": result.get("error")}
                
        except Exception as e:
            logger.error(f"❌ Guardian seeding failed: {e}")
            return {"created": 0, "error": str(e)}
    
    async def _seed_agents(self) -> Dict[str, Any]:
        """Seed initial agent data"""
        try:
            logger.info("🤖 Seeding agents...")
            
            agents_data = [
                {
                    "name": "Agent Alpha",
                    "endpoint": "http://agent-alpha:8001",
                    "capabilities": '["navigation", "reconnaissance", "tactical_analysis"]',
                    "status": "online",
                    "location": "Sector 7-G",
                    "health_score": 98.5
                },
                {
                    "name": "Agent Beta", 
                    "endpoint": "http://agent-beta:8002",
                    "capabilities": '["communications", "data_processing", "sensor_array"]',
                    "status": "online",
                    "location": "Sector 12-A",
                    "health_score": 96.2
                },
                {
                    "name": "Agent Gamma",
                    "endpoint": "http://agent-gamma:8003",
                    "capabilities": '["logistics", "coordination", "supply_management"]',
                    "status": "online", 
                    "location": "Central Hub",
                    "health_score": 94.8
                }
            ]
            
            created_count = 0
            created_agents = []
            
            for agent_data in agents_data:
                result = await self.db.create_agent(agent_data)
                if result["status"] == "success":
                    created_count += 1
                    created_agents.append(result["agent"])
                    logger.info(f"✅ Created agent: {agent_data['name']}")
                else:
                    logger.warning(f"⚠️ Agent creation failed for {agent_data['name']}: {result.get('error')}")
            
            return {"created": created_count, "agents": created_agents}
            
        except Exception as e:
            logger.error(f"❌ Agent seeding failed: {e}")
            return {"created": 0, "error": str(e)}
    
    async def _seed_missions(self) -> Dict[str, Any]:
        """Seed initial mission data"""
        try:
            logger.info("🎯 Seeding missions...")
            
            missions_data = [
                {
                    "title": "Nebula Survey Alpha-7",
                    "description": "Investigate unusual energy readings in the Alpha-7 nebula cluster. Priority mission requiring tactical analysis and reconnaissance capabilities.",
                    "status": "active",
                    "priority": "high",
                    "progress": 25,
                    "objectives": '["Scan nebula perimeter", "Analyze energy signatures", "Report findings to command"]'
                },
                {
                    "title": "Supply Chain Optimization",
                    "description": "Optimize logistics routes between stations Beta-3 and Gamma-9. Focus on reducing transit time and resource efficiency.",
                    "status": "active", 
                    "priority": "normal",
                    "progress": 60,
                    "objectives": '["Route analysis", "Resource calculation", "Implementation planning"]'
                },
                {
                    "title": "Communication Array Maintenance",
                    "description": "Routine maintenance and calibration of deep space communication arrays in sectors 10-15.",
                    "status": "completed",
                    "priority": "normal",
                    "progress": 100,
                    "objectives": '["Array inspection", "Signal calibration", "Performance testing"]'
                }
            ]
            
            created_count = 0
            created_missions = []
            
            for mission_data in missions_data:
                result = await self.db.create_mission(mission_data)
                if result["status"] == "success":
                    created_count += 1
                    created_missions.append(result["mission"])
                    logger.info(f"✅ Created mission: {mission_data['title']}")
                else:
                    logger.warning(f"⚠️ Mission creation failed for {mission_data['title']}: {result.get('error')}")
            
            return {"created": created_count, "missions": created_missions}
            
        except Exception as e:
            logger.error(f"❌ Mission seeding failed: {e}")
            return {"created": 0, "error": str(e)}
    
    async def _seed_vault_logs(self) -> Dict[str, Any]:
        """Seed initial vault log data"""
        try:
            logger.info("📝 Seeding vault logs...")
            
            logs_data = [
                {
                    "agent_name": "System Guardian Alpha",
                    "action": "system_initialization",
                    "details": "SR-AIbridge backend system successfully initialized with SQLite database",
                    "log_level": "info"
                },
                {
                    "agent_name": "Agent Alpha",
                    "action": "mission_assignment",
                    "details": "Assigned to Nebula Survey Alpha-7 mission. Beginning reconnaissance preparations.",
                    "log_level": "info"
                },
                {
                    "agent_name": "Agent Beta",
                    "action": "communication_established",
                    "details": "Communication array successfully connected. All channels operational.",
                    "log_level": "info"
                },
                {
                    "agent_name": "Agent Gamma",
                    "action": "logistics_optimized",
                    "details": "Supply chain routes optimized. Efficiency improved by 15%.",
                    "log_level": "info"
                },
                {
                    "agent_name": "System",
                    "action": "demo_data_seeded",
                    "details": "Initial demo data successfully seeded into the system",
                    "log_level": "info"
                }
            ]
            
            created_count = 0
            created_logs = []
            
            for log_data in logs_data:
                result = await self.db.create_vault_log(log_data)
                if result["status"] == "success":
                    created_count += 1
                    created_logs.append(result["log"])
                    logger.info(f"✅ Created vault log: {log_data['action']}")
                else:
                    logger.warning(f"⚠️ Vault log creation failed for {log_data['action']}: {result.get('error')}")
            
            return {"created": created_count, "logs": created_logs}
            
        except Exception as e:
            logger.error(f"❌ Vault log seeding failed: {e}")
            return {"created": 0, "error": str(e)}
    
    async def _get_system_summary(self) -> Dict[str, Any]:
        """Get system summary after seeding"""
        try:
            guardians = await self.db.get_guardians()
            agents = await self.db.get_agents()
            missions = await self.db.get_missions()
            
            active_guardians = [g for g in guardians if g.get("active", False)]
            online_agents = [a for a in agents if a.get("status") == "online"]
            active_missions = [m for m in missions if m.get("status") == "active"]
            
            return {
                "admiral": active_guardians[0].get("name", "System Guardian") if active_guardians else "Unknown",
                "agents_count": len(agents),
                "agents_online": len(online_agents),
                "missions_count": len(missions),
                "active_missions": len(active_missions),
                "fleet_online": len(online_agents)  # Using agents as fleet for demo
            }
        except Exception as e:
            logger.warning(f"Could not get system summary: {e}")
            return {
                "admiral": "Unknown",
                "agents_count": 0,
                "agents_online": 0,
                "missions_count": 0,
                "active_missions": 0,
                "fleet_online": 0
            }


# Global seeder instance
data_seeder = DataSeeder()


async def seed_initial_data() -> Dict[str, Any]:
    """
    Public function to seed initial data
    Used by main application startup
    """
    return await data_seeder.seed_initial_data()


def get_fleet_data() -> List[Dict[str, Any]]:
    """
    Get fleet data for frontend compatibility
    Uses agents as fleet ships for demo purposes
    """
    try:
        # Static fleet data for demo - in a real system this would come from database
        fleet_data = [
            {
                "id": 1,
                "name": "USS Enterprise",
                "class": "Galaxy",
                "captain": "Agent Alpha",
                "status": "online",
                "location": "Sector 7-G",
                "mission": "Nebula Survey Alpha-7"
            },
            {
                "id": 2,
                "name": "USS Voyager", 
                "class": "Intrepid",
                "captain": "Agent Beta",
                "status": "online",
                "location": "Sector 12-A",
                "mission": "Communication Array Maintenance"
            },
            {
                "id": 3,
                "name": "USS Defiant",
                "class": "Defiant",
                "captain": "Agent Gamma",
                "status": "online",
                "location": "Central Hub",
                "mission": "Supply Chain Optimization"
            }
        ]
        return fleet_data
    except Exception as e:
        logger.error(f"Error getting fleet data: {e}")
        return []


async def get_system_status() -> Dict[str, Any]:
    """
    Get comprehensive system status
    Used by status endpoints
    """
    try:
        guardians = await db_manager.get_guardians()
        agents = await db_manager.get_agents()
        missions = await db_manager.get_missions()
        logs = await db_manager.get_vault_logs(limit=1)
        
        active_guardians = [g for g in guardians if g.get("active", False)]
        online_agents = [a for a in agents if a.get("status") == "online"]
        active_missions = [m for m in missions if m.get("status") == "active"]
        
        fleet_data = get_fleet_data()
        online_fleet = [ship for ship in fleet_data if ship.get("status") == "online"]
        
        return {
            "admiral": active_guardians[0].get("name", "System Guardian") if active_guardians else "System Guardian Alpha",
            "agents_online": len(online_agents),
            "active_missions": len(active_missions),
            "total_agents": len(agents),
            "total_missions": len(missions),
            "fleet_count": len(fleet_data),
            "fleet_online": len(online_fleet),
            "vault_logs": len(logs) if logs else 0,
            "system_health": "healthy" if active_guardians else "warning"
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "admiral": "System Guardian Alpha",
            "agents_online": 0,
            "active_missions": 0,
            "total_agents": 0,
            "total_missions": 0,
            "fleet_count": 0,
            "fleet_online": 0,
            "vault_logs": 0,
            "system_health": "error"
        }