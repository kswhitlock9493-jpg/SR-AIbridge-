"""
SR-AIbridge Data Management Rituals

This module provides centralized data management operations for the SR-AIbridge backend.
Includes rituals for seeding, cleaning up, and reseeding demo data in the in-memory storage.

For future database upgrades, these rituals can be extended to work with actual database
operations while maintaining the same interface.
"""

from datetime import datetime
from typing import Dict, Any, Optional


class DataRituals:
    """
    Centralized data management rituals for SR-AIbridge.
    
    This class provides methods to manage demo data in the in-memory storage,
    with a clean interface that can be extended for database operations in the future.
    """
    
    def __init__(self, storage):
        """
        Initialize rituals with a storage instance.
        
        Args:
            storage: The storage instance to operate on (InMemoryStorage or future DB)
        """
        self.storage = storage
    
    def cleanup(self) -> Dict[str, Any]:
        """
        Clean up all data from storage.
        
        Returns:
            dict: Status information about the cleanup operation
        """
        # Store counts before cleanup for reporting
        before_counts = {
            "agents": len(self.storage.agents),
            "missions": len(self.storage.missions),
            "vault_logs": len(self.storage.vault_logs),
            "captain_messages": len(self.storage.captain_messages),
            "armada_fleet": len(self.storage.armada_fleet)
        }
        
        # Clear all storage
        self.storage.captain_messages.clear()
        self.storage.armada_fleet.clear()
        self.storage.agents.clear()
        self.storage.missions.clear()
        self.storage.vault_logs.clear()
        self.storage.next_id = 1
        
        return {
            "ok": True,
            "message": "All data cleaned up successfully",
            "cleared_counts": before_counts,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def seed(self) -> Dict[str, Any]:
        """
        Seed storage with demo data without clearing existing data.
        
        Returns:
            dict: Status information about the seed operation
        """
        # Store counts before seeding
        before_counts = {
            "agents": len(self.storage.agents),
            "missions": len(self.storage.missions),
            "vault_logs": len(self.storage.vault_logs),
            "captain_messages": len(self.storage.captain_messages),
            "armada_fleet": len(self.storage.armada_fleet)
        }
        
        # Seed armada fleet
        fleet_data = [
            {"id": self.storage.get_next_id(), "name": "Flagship Sovereign", "status": "online", "location": "Sector Alpha"},
            {"id": self.storage.get_next_id(), "name": "Frigate Horizon", "status": "offline", "location": "Sector Beta"},
            {"id": self.storage.get_next_id(), "name": "Scout Whisper", "status": "online", "location": "Sector Delta"},
            {"id": self.storage.get_next_id(), "name": "SR-Vanguard", "status": "online", "location": "Outer Rim"},
            {"id": self.storage.get_next_id(), "name": "SR-Oracle", "status": "online", "location": "Deep Space Node"},
        ]
        self.storage.armada_fleet.extend(fleet_data)
        
        # Seed agents
        agents_data = [
            {
                "id": self.storage.get_next_id(),
                "name": "Agent Alpha",
                "endpoint": "http://agent-alpha:8001",
                "capabilities": [
                    {"name": "reconnaissance", "version": "2.1", "description": "Advanced scouting operations"},
                    {"name": "communication", "version": "1.5", "description": "Secure communications relay"}
                ],
                "status": "online",
                "last_heartbeat": datetime.utcnow(),
                "created_at": datetime.utcnow()
            },
            {
                "id": self.storage.get_next_id(),
                "name": "Agent Beta",
                "endpoint": "http://agent-beta:8002",
                "capabilities": [
                    {"name": "analysis", "version": "3.0", "description": "Data analysis and pattern recognition"},
                    {"name": "threat-detection", "version": "1.8", "description": "Security threat identification"}
                ],
                "status": "online",
                "last_heartbeat": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
        ]
        self.storage.agents.extend(agents_data)
        
        # Seed missions
        missions_data = [
            {
                "id": self.storage.get_next_id(),
                "title": "Deep Space Reconnaissance",
                "description": "Survey unknown sectors for potential threats and resources",
                "status": "active",
                "priority": "high",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": self.storage.get_next_id(),
                "title": "Communication Array Setup",
                "description": "Establish secure communication relays in outer rim",
                "status": "completed",
                "priority": "normal",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": self.storage.get_next_id(),
                "title": "Defensive Perimeter Analysis",
                "description": "Assess current defensive capabilities and recommend improvements",
                "status": "planning",
                "priority": "medium",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        self.storage.missions.extend(missions_data)
        
        # Seed vault logs
        vault_logs_data = [
            {
                "id": self.storage.get_next_id(),
                "agent_name": "Agent Alpha",
                "action": "mission_start",
                "details": "Initiated reconnaissance mission in Sector Gamma",
                "timestamp": datetime.utcnow(),
                "log_level": "info"
            },
            {
                "id": self.storage.get_next_id(),
                "agent_name": "Agent Beta",
                "action": "data_analysis",
                "details": "Completed threat assessment for outer rim sectors",
                "timestamp": datetime.utcnow(),
                "log_level": "info"
            },
            {
                "id": self.storage.get_next_id(),
                "agent_name": "System",
                "action": "alert",
                "details": "Unknown vessel detected at coordinates 127.45, 89.12",
                "timestamp": datetime.utcnow(),
                "log_level": "warning"
            }
        ]
        self.storage.vault_logs.extend(vault_logs_data)
        
        # Seed captain messages
        captain_messages_data = [
            {
                "id": self.storage.get_next_id(),
                "from_": "Admiral Kyle",
                "to": "Captain Torres",
                "message": "Status report on outer rim patrol?",
                "timestamp": datetime.utcnow()
            },
            {
                "id": self.storage.get_next_id(),
                "from_": "Captain Torres",
                "to": "Admiral Kyle",
                "message": "All clear in sectors 7-12. Proceeding to deep space checkpoint.",
                "timestamp": datetime.utcnow()
            }
        ]
        self.storage.captain_messages.extend(captain_messages_data)
        
        # Calculate what was added
        after_counts = {
            "agents": len(self.storage.agents),
            "missions": len(self.storage.missions),
            "vault_logs": len(self.storage.vault_logs),
            "captain_messages": len(self.storage.captain_messages),
            "armada_fleet": len(self.storage.armada_fleet)
        }
        
        added_counts = {
            key: after_counts[key] - before_counts[key] 
            for key in after_counts.keys()
        }
        
        return {
            "ok": True,
            "message": "Demo data seeded successfully",
            "before_counts": before_counts,
            "after_counts": after_counts,
            "added_counts": added_counts,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def reseed(self) -> Dict[str, Any]:
        """
        Clean up all data and reseed with fresh demo data.
        
        This is a combination of cleanup() and seed() operations.
        
        Returns:
            dict: Status information about the reseed operation
        """
        cleanup_result = self.cleanup()
        seed_result = self.seed()
        
        return {
            "ok": True,
            "message": "Data reseeded successfully (cleanup + seed)",
            "cleanup": cleanup_result,
            "seed": seed_result,
            "final_counts": seed_result["after_counts"],
            "timestamp": datetime.utcnow().isoformat()
        }


def seed_demo_data(storage) -> Dict[str, Any]:
    """
    Convenience function to seed demo data using the rituals manager.
    
    This function provides backward compatibility with the existing seed_demo_data()
    function while using the new rituals system.
    
    Args:
        storage: The storage instance to seed
        
    Returns:
        dict: Status information about the seed operation
    """
    rituals = DataRituals(storage)
    return rituals.reseed()


# For backward compatibility, create a simple function that matches the original signature
def create_rituals_manager(storage):
    """
    Factory function to create a DataRituals instance.
    
    Args:
        storage: The storage instance to manage
        
    Returns:
        DataRituals: Configured rituals manager instance
    """
    return DataRituals(storage)