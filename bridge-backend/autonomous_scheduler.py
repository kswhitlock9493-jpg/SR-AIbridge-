"""
Autonomous Bridge Scheduler

This module implements the autonomous mission progression system for SR-AIbridge.
Agents self-assign missions, progress through statuses, and generate reports automatically.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class AutonomousScheduler:
    """Manages autonomous mission progression and agent behaviors"""
    
    def __init__(self, storage, websocket_manager=None):
        self.storage = storage
        self.websocket_manager = websocket_manager
        self.running = False
        self.task = None
        
        # Autonomous behavior settings
        self.mission_progression_interval = 15  # seconds
        self.agent_report_interval = 30  # seconds
        self.fleet_movement_interval = 45  # seconds
        self.npc_chat_interval = 60  # seconds
        
        # Mission progression probabilities
        self.success_probability = 0.7
        self.failure_probability = 0.1
        self.progress_probability = 0.5
        
    async def start(self):
        """Start the autonomous scheduler"""
        if self.running:
            return
            
        self.running = True
        logger.info("🤖 Starting autonomous scheduler")
        
        # Start all autonomous tasks
        self.task = asyncio.create_task(self._run_scheduler())
        
    async def stop(self):
        """Stop the autonomous scheduler"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                logger.info("🔄 Autonomous scheduler stopped")
    
    async def _run_scheduler(self):
        """Main scheduler loop"""
        mission_timer = 0
        agent_timer = 0
        fleet_timer = 0
        chat_timer = 0
        
        try:
            while self.running:
                await asyncio.sleep(1)  # 1 second tick
                
                mission_timer += 1
                agent_timer += 1
                fleet_timer += 1
                chat_timer += 1
                
                # Mission progression
                if mission_timer >= self.mission_progression_interval:
                    await self._process_missions()
                    mission_timer = 0
                
                # Agent reports
                if agent_timer >= self.agent_report_interval:
                    await self._generate_agent_reports()
                    agent_timer = 0
                
                # Fleet movements
                if fleet_timer >= self.fleet_movement_interval:
                    await self._update_fleet_movements()
                    fleet_timer = 0
                
                # NPC chat
                if chat_timer >= self.npc_chat_interval:
                    await self._generate_npc_chat()
                    chat_timer = 0
                    
        except asyncio.CancelledError:
            logger.info("Scheduler cancelled")
            raise
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            
    async def _process_missions(self):
        """Process autonomous mission progression"""
        active_missions = [m for m in self.storage.missions if m.get('status') == 'active']
        
        for mission in active_missions:
            # Assign agents to unassigned missions
            if not mission.get('assigned_agent_id'):
                await self._auto_assign_agent(mission)
            
            # Progress mission status
            await self._progress_mission(mission)
    
    async def _auto_assign_agent(self, mission):
        """Automatically assign available agents to missions"""
        available_agents = [a for a in self.storage.agents if a.get('status') == 'online']
        
        if available_agents:
            agent = random.choice(available_agents)
            mission['assigned_agent_id'] = agent['id']
            mission['updated_at'] = datetime.utcnow()
            
            # Generate assignment log
            await self._add_vault_log(
                agent_name=agent['name'],
                action="mission_assignment",
                details=f"Auto-assigned to mission: {mission['title']}",
                log_level="info"
            )
            
            # Notify via WebSocket
            if self.websocket_manager:
                await self.websocket_manager.broadcast({
                    "type": "mission_updated",
                    "mission": mission
                })
    
    async def _progress_mission(self, mission):
        """Progress mission through statuses autonomously"""
        rand = random.random()
        
        if rand < self.failure_probability:
            # Mission fails
            mission['status'] = 'failed'
            mission['updated_at'] = datetime.utcnow()
            
            agent_name = self._get_agent_name(mission.get('assigned_agent_id'))
            await self._add_vault_log(
                agent_name=agent_name,
                action="mission_failed",
                details=f"Mission failed: {mission['title']} - System malfunction detected",
                log_level="warning"
            )
            
        elif rand < self.success_probability:
            # Mission succeeds
            mission['status'] = 'completed'
            mission['updated_at'] = datetime.utcnow()
            
            agent_name = self._get_agent_name(mission.get('assigned_agent_id'))
            await self._add_vault_log(
                agent_name=agent_name,
                action="mission_completed",
                details=f"Mission successfully completed: {mission['title']}",
                log_level="info"
            )
            
        elif rand < self.progress_probability:
            # Mission progresses (generate progress log)
            agent_name = self._get_agent_name(mission.get('assigned_agent_id'))
            progress_messages = [
                f"Making progress on {mission['title']} - 25% complete",
                f"Halfway through {mission['title']} objectives",
                f"Final phase of {mission['title']} initiated",
                f"Gathering intelligence for {mission['title']}",
                f"Coordinating resources for {mission['title']}"
            ]
            
            await self._add_vault_log(
                agent_name=agent_name,
                action="mission_progress",
                details=random.choice(progress_messages),
                log_level="info"
            )
        
        # Broadcast mission updates
        if self.websocket_manager:
            await self.websocket_manager.broadcast({
                "type": "mission_updated",
                "mission": mission
            })
    
    async def _generate_agent_reports(self):
        """Generate autonomous agent activity reports"""
        online_agents = [a for a in self.storage.agents if a.get('status') == 'online']
        
        for agent in online_agents:
            if random.random() < 0.3:  # 30% chance per interval
                report_types = [
                    ("system_check", "Routine system diagnostics completed - all systems nominal"),
                    ("sector_scan", f"Completed sector scan - {random.randint(0, 5)} anomalies detected"),
                    ("resource_update", f"Resource levels at {random.randint(70, 100)}% capacity"),
                    ("communication_check", "Communication array functioning within normal parameters"),
                    ("navigation_update", f"Navigation systems recalibrated for sector {random.choice(['Alpha', 'Beta', 'Gamma', 'Delta'])}"),
                ]
                
                action, details = random.choice(report_types)
                await self._add_vault_log(
                    agent_name=agent['name'],
                    action=action,
                    details=details,
                    log_level="info"
                )
    
    async def _update_fleet_movements(self):
        """Update fleet ship positions and statuses"""
        sectors = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Omega"]
        statuses = ["online", "offline", "maintenance", "patrol"]
        
        for ship in self.storage.armada_fleet:
            if random.random() < 0.4:  # 40% chance of movement
                ship['location'] = f"Sector {random.choice(sectors)}"
                ship['updated_at'] = datetime.utcnow()
                
            if random.random() < 0.2:  # 20% chance of status change
                ship['status'] = random.choice(statuses)
                
                # Generate fleet log
                await self._add_vault_log(
                    agent_name="Fleet Command",
                    action="fleet_update",
                    details=f"{ship['name']} status changed to {ship['status']} at {ship['location']}",
                    log_level="info"
                )
        
        # Broadcast fleet updates
        if self.websocket_manager:
            await self.websocket_manager.broadcast({
                "type": "fleet_updated",
                "fleet": self.storage.armada_fleet
            })
    
    async def _generate_npc_chat(self):
        """Generate NPC captain conversations"""
        npc_captains = ["Captain Torres", "Captain Singh", "Captain Chen", "Captain Rodriguez"]
        chat_templates = [
            "Sector {sector} patrol complete. All clear.",
            "Requesting permission to dock at Station {station}.",
            "Anomalous readings detected in quadrant {quad}. Investigating.",
            "Supply run to {location} completed successfully.",
            "Weather patterns showing storm activity in {sector}. Adjusting course.",
            "Long-range sensors picking up unidentified signals.",
            "All crew reporting ready for next assignment.",
        ]
        
        if random.random() < 0.6:  # 60% chance
            captain = random.choice(npc_captains)
            template = random.choice(chat_templates)
            
            # Fill template variables
            message = template.format(
                sector=f"Sector {random.choice(['Alpha', 'Beta', 'Gamma'])}",
                station=f"Alpha-{random.randint(1, 9)}",
                quad=f"Q{random.randint(1, 4)}",
                location=random.choice(["Outpost Delta", "Mining Station", "Research Facility"])
            )
            
            # Add to captain messages
            npc_message = {
                "id": self.storage.get_next_id(),
                "from_": captain,
                "to": "Bridge Command",
                "message": message,
                "timestamp": datetime.utcnow()
            }
            
            self.storage.captain_messages.append(npc_message)
            
            # Broadcast chat update
            if self.websocket_manager:
                await self.websocket_manager.broadcast({
                    "type": "chat_message",
                    "message": npc_message
                })
    
    async def _add_vault_log(self, agent_name: str, action: str, details: str, log_level: str = "info"):
        """Add a log entry to vault logs"""
        log_entry = {
            "id": self.storage.get_next_id(),
            "agent_name": agent_name,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow(),
            "log_level": log_level
        }
        
        self.storage.vault_logs.append(log_entry)
        
        # Broadcast log update
        if self.websocket_manager:
            await self.websocket_manager.broadcast({
                "type": "vault_log",
                "log": log_entry
            })
    
    def _get_agent_name(self, agent_id):
        """Get agent name by ID"""
        if not agent_id:
            return "System"
            
        for agent in self.storage.agents:
            if agent.get('id') == agent_id:
                return agent.get('name', 'Unknown Agent')
        
        return "Unknown Agent"