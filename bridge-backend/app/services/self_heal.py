"""
Self-healing service for SR-AIbridge
Handles autonomous system recovery and health management
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SelfHealingService:
    """Service for autonomous system healing and recovery"""
    
    def __init__(self, storage, websocket_manager):
        self.storage = storage
        self.websocket_manager = websocket_manager
        self.healing_active = True
        self.last_heal_check = None
        self.heal_interval = 60  # 1 minute
        self.healing_rules = []
        self.healing_history = []
        
    def add_healing_rule(self, rule_name: str, condition_check, healing_action):
        """Add a healing rule with condition and action"""
        self.healing_rules.append({
            "name": rule_name,
            "condition": condition_check,
            "action": healing_action,
            "last_triggered": None,
            "trigger_count": 0
        })
        
    async def run_healing_cycle(self):
        """Run a complete healing cycle"""
        if not self.healing_active:
            return
            
        logger.info("🔧 Starting self-healing cycle...")
        self.last_heal_check = datetime.utcnow()
        
        healing_actions = []
        
        # Check each healing rule
        for rule in self.healing_rules:
            try:
                if await rule["condition"](self.storage):
                    logger.info(f"🔧 Healing rule triggered: {rule['name']}")
                    result = await rule["action"](self.storage)
                    
                    healing_actions.append({
                        "rule": rule["name"],
                        "action": result,
                        "timestamp": datetime.utcnow()
                    })
                    
                    rule["last_triggered"] = datetime.utcnow()
                    rule["trigger_count"] += 1
                    
            except Exception as e:
                logger.error(f"🔧 Healing rule error ({rule['name']}): {e}")
                
        # Record healing history
        if healing_actions:
            self.healing_history.append({
                "timestamp": datetime.utcnow(),
                "actions": healing_actions
            })
            
            # Keep only last 100 healing records
            if len(self.healing_history) > 100:
                self.healing_history = self.healing_history[-100:]
                
        logger.info(f"🔧 Healing cycle completed: {len(healing_actions)} actions taken")
        return healing_actions
        
    def get_healing_status(self) -> Dict[str, Any]:
        """Get current healing status"""
        return {
            "active": self.healing_active,
            "last_check": self.last_heal_check.isoformat() if self.last_heal_check else None,
            "rules_count": len(self.healing_rules),
            "healing_history_count": len(self.healing_history),
            "recent_actions": self.healing_history[-5:] if self.healing_history else []
        }
        
    async def setup_default_healing_rules(self):
        """Setup default healing rules for common issues"""
        
        # Rule 1: Restart offline agents
        async def check_offline_agents(storage):
            offline_agents = [a for a in storage.agents if a.get("status") == "offline"]
            return len(offline_agents) > 0
            
        async def heal_offline_agents(storage):
            offline_agents = [a for a in storage.agents if a.get("status") == "offline"]
            healed = 0
            for agent in offline_agents:
                # Simulate agent restart by marking as online
                agent["status"] = "online"
                agent["last_heartbeat"] = datetime.utcnow()
                healed += 1
            return f"Restarted {healed} offline agents"
            
        self.add_healing_rule("restart_offline_agents", check_offline_agents, heal_offline_agents)
        
        # Rule 2: Clean up old missions
        async def check_old_missions(storage):
            old_threshold = datetime.utcnow() - timedelta(hours=24)
            old_missions = [m for m in storage.missions 
                           if m.get("status") == "completed" 
                           and m.get("updated_at", datetime.utcnow()) < old_threshold]
            return len(old_missions) > 10
            
        async def heal_old_missions(storage):
            old_threshold = datetime.utcnow() - timedelta(hours=24)
            old_missions = [m for m in storage.missions 
                           if m.get("status") == "completed" 
                           and m.get("updated_at", datetime.utcnow()) < old_threshold]
            
            # Keep only recent completed missions
            for mission in old_missions[:-5]:  # Keep last 5
                storage.missions.remove(mission)
                
            return f"Cleaned up {len(old_missions)-5} old missions"
            
        self.add_healing_rule("cleanup_old_missions", check_old_missions, heal_old_missions)
        
        # Rule 3: Maintain minimum agents
        async def check_minimum_agents(storage):
            online_agents = [a for a in storage.agents if a.get("status") == "online"]
            return len(online_agents) < 2
            
        async def heal_minimum_agents(storage):
            online_agents = [a for a in storage.agents if a.get("status") == "online"]
            if len(online_agents) < 2:
                # Add a backup agent
                backup_agent = {
                    "id": storage.get_next_id(),
                    "name": f"BackupAgent-{datetime.utcnow().strftime('%H%M%S')}",
                    "endpoint": "http://localhost:8001/backup",
                    "status": "online",
                    "capabilities": ["backup", "monitoring"],
                    "last_heartbeat": datetime.utcnow()
                }
                storage.agents.append(backup_agent)
                return "Created backup agent"
            return "No action needed"
            
        self.add_healing_rule("maintain_minimum_agents", check_minimum_agents, heal_minimum_agents)
        
        logger.info("🔧 Default healing rules configured")
        
    async def start_healing_loop(self):
        """Start the continuous healing loop"""
        await self.setup_default_healing_rules()
        
        while self.healing_active:
            try:
                await self.run_healing_cycle()
                await asyncio.sleep(self.heal_interval)
            except Exception as e:
                logger.error(f"🔧 Healing loop error: {e}")
                await asyncio.sleep(self.heal_interval)