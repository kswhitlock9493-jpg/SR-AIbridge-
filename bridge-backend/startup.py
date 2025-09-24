"""
SQLite Database Startup and Seeding Module for SR-AIbridge
Handles initial database seeding with sample data for dashboard pre-population
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from db import db_manager

logger = logging.getLogger(__name__)

async def seed_initial_data() -> Dict[str, Any]:
    """
    Seed the database with initial demo data
    - 1 test Admiral
    - 3 sample agents
    - 1 mission
    - 2 fleet members online
    """
    seeded_items = []
    
    try:
        # Check if data already exists to avoid duplicates
        existing_agents = await db_manager.get_agents()
        existing_missions = await db_manager.get_missions()
        
        if len(existing_agents) >= 3 and len(existing_missions) >= 1:
            return {
                "status": "success",
                "message": "Demo data already exists",
                "seeded_items": [],
                "skipped": True
            }
        
        # Seed 3 sample agents
        sample_agents = [
            {
                "name": "Agent-Alpha-001",
                "status": "online",
                "capabilities": "reconnaissance,infiltration",
                "last_seen": datetime.utcnow(),
                "health_score": 95.0,
                "location": "Sector 7-G"
            },
            {
                "name": "Agent-Beta-002", 
                "status": "online",
                "capabilities": "combat,tactical-analysis",
                "last_seen": datetime.utcnow(),
                "health_score": 88.0,
                "location": "Outpost Delta"
            },
            {
                "name": "Agent-Gamma-003",
                "status": "standby",
                "capabilities": "support,logistics",
                "last_seen": datetime.utcnow() - timedelta(minutes=15),
                "health_score": 92.0,
                "location": "Base Station"
            }
        ]
        
        for agent_data in sample_agents:
            try:
                result = await db_manager.create_agent(agent_data)
                if result["status"] == "success":
                    seeded_items.append(f"Agent: {agent_data['name']}")
                    logger.info(f"✅ Seeded agent: {agent_data['name']}")
            except Exception as e:
                logger.warning(f"Failed to seed agent {agent_data['name']}: {e}")
        
        # Seed 1 sample mission
        sample_mission = {
            "title": "Operation Starlight",
            "description": "Reconnaissance mission to survey uncharted sectors and establish communication relays",
            "status": "active",
            "priority": "high",
            "assigned_agents": '["Agent-Alpha-001", "Agent-Beta-002"]',  # JSON string
            "start_time": datetime.utcnow() - timedelta(hours=2),
            "estimated_completion": datetime.utcnow() + timedelta(hours=6),
            "objectives": '["Survey sectors 7-G through 7-J", "Deploy 3 communication relays", "Report back with findings"]'  # JSON string
        }
        
        try:
            result = await db_manager.create_mission(sample_mission)
            if result["status"] == "success":
                seeded_items.append(f"Mission: {sample_mission['title']}")
                logger.info(f"✅ Seeded mission: {sample_mission['title']}")
        except Exception as e:
            logger.warning(f"Failed to seed mission: {e}")
        
        # Create Admiral user entry (stored as a special guardian)
        admiral_data = {
            "name": "Admiral Marcus Chen",
            "status": "active",
            "last_selftest": datetime.utcnow(),
            "last_action": "Dashboard review and mission assignment",
            "health_score": 100.0,
            "active": True
        }
        
        try:
            # Check if admiral already exists
            existing_guardians = await db_manager.get_guardians()
            admiral_exists = any(g.get("name") == admiral_data["name"] for g in existing_guardians)
            
            if not admiral_exists:
                result = await db_manager.create_guardian(admiral_data)
                if result["status"] == "success":
                    seeded_items.append(f"Admiral: {admiral_data['name']}")
                    logger.info(f"✅ Seeded admiral: {admiral_data['name']}")
        except Exception as e:
            logger.warning(f"Failed to seed admiral: {e}")
        
        # Seed some vault logs for activity
        sample_logs = [
            {
                "agent_name": "Agent-Alpha-001",
                "action": "mission_start",
                "details": "Commenced Operation Starlight reconnaissance",
                "log_level": "info",
                "timestamp": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "agent_name": "System",
                "action": "fleet_status",
                "details": "Fleet communications established with 2 active vessels",
                "log_level": "info", 
                "timestamp": datetime.utcnow() - timedelta(minutes=30)
            },
            {
                "agent_name": "Agent-Beta-002",
                "action": "tactical_update",
                "details": "Sector sweep completed, all clear for advance",
                "log_level": "info",
                "timestamp": datetime.utcnow() - timedelta(minutes=45)
            }
        ]
        
        for log_data in sample_logs:
            try:
                result = await db_manager.create_vault_log(log_data)
                if result["status"] == "success":
                    seeded_items.append(f"Log: {log_data['action']}")
            except Exception as e:
                logger.warning(f"Failed to seed log: {e}")
        
        return {
            "status": "success",
            "message": f"Successfully seeded {len(seeded_items)} items",
            "seeded_items": seeded_items,
            "admiral": "Admiral Marcus Chen",
            "agents_count": len([item for item in seeded_items if item.startswith("Agent:")]),
            "missions_count": len([item for item in seeded_items if item.startswith("Mission:")]),
            "fleet_online": 2  # Hard-coded for now, will be dynamic with fleet data
        }
        
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        return {
            "status": "error",
            "message": f"Seeding failed: {str(e)}",
            "seeded_items": seeded_items
        }

def get_fleet_data() -> list:
    """
    Return sample fleet data for the fleet endpoint
    This simulates 2 online fleet members as mentioned in requirements
    """
    return [
        {
            "id": "fleet-vessel-001",
            "name": "SSC Endeavor",
            "class": "Scout",
            "status": "online",
            "location": "Patrol Route Alpha",
            "crew_count": 12,
            "last_contact": datetime.utcnow().isoformat(),
            "health_status": "nominal",
            "current_mission": "perimeter_patrol"
        },
        {
            "id": "fleet-vessel-002", 
            "name": "SSC Guardian",
            "class": "Frigate",
            "status": "online",
            "location": "Station Orbit",
            "crew_count": 45,
            "last_contact": datetime.utcnow().isoformat(),
            "health_status": "nominal",
            "current_mission": "base_defense"
        }
    ]

async def get_system_status() -> Dict[str, Any]:
    """
    Get comprehensive system status for dashboard
    Includes Admiral, agents, missions, fleet, and vault logs
    """
    try:
        # Get all data counts
        agents = await db_manager.get_agents()
        missions = await db_manager.get_missions()
        vault_logs = await db_manager.get_vault_logs()
        guardians = await db_manager.get_guardians()
        fleet = get_fleet_data()
        
        # Find admiral
        admiral = next((g for g in guardians if g.get("name", "").startswith("Admiral")), None)
        admiral_name = admiral["name"] if admiral else "System Guardian"
        
        # Count online agents
        agents_online = len([a for a in agents if a.get("status") == "online"])
        
        # Count active missions  
        active_missions = len([m for m in missions if m.get("status") == "active"])
        
        # Count online fleet
        fleet_online = len([f for f in fleet if f.get("status") == "online"])
        
        return {
            "admiral": admiral_name,
            "agents_online": agents_online,
            "total_agents": len(agents),
            "active_missions": active_missions,
            "total_missions": len(missions),
            "fleet_count": fleet_online,
            "fleet_total": len(fleet),
            "vault_logs": len(vault_logs),
            "system_health": "nominal"
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "admiral": "Unknown",
            "agents_online": 0,
            "total_agents": 0,
            "active_missions": 0,
            "total_missions": 0,
            "fleet_count": 0,
            "fleet_total": 0,
            "vault_logs": 0,
            "system_health": "error"
        }