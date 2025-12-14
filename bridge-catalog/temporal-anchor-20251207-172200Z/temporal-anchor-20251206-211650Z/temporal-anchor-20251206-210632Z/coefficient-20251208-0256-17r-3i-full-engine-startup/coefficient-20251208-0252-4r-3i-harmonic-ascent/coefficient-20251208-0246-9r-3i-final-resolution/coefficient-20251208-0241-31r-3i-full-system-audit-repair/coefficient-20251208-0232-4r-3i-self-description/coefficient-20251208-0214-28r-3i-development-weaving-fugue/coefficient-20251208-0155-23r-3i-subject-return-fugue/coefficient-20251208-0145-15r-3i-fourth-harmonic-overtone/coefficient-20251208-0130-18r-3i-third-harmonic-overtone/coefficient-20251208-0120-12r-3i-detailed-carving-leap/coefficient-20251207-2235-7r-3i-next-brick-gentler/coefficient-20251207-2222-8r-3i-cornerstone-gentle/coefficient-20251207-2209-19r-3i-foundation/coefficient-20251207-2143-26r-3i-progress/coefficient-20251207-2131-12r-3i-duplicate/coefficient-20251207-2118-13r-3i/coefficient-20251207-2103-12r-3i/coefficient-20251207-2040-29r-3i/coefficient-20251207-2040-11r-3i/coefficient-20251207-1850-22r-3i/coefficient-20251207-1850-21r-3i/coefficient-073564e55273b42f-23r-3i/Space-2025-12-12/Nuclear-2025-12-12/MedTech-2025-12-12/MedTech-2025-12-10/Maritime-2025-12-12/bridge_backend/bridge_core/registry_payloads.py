"""
Registry Payloads - Default agent registry payloads
Provides standardized payload structures for agent registration and management
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from enum import Enum

class AgentType(Enum):
    """Types of agents in the system"""
    SCOUT = "scout"
    GUARDIAN = "guardian"
    ANALYST = "analyst"
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"
    MAINTENANCE = "maintenance"


class AgentCapability(Enum):
    """Standard agent capabilities"""
    RECONNAISSANCE = "reconnaissance"
    COMBAT = "combat"
    ANALYSIS = "analysis"
    COMMUNICATION = "communication"
    REPAIR = "repair"
    LOGISTICS = "logistics"
    COORDINATION = "coordination"
    MONITORING = "monitoring"


class AgentStatus(Enum):
    """Agent operational status"""
    ACTIVE = "active"
    STANDBY = "standby"
    MAINTENANCE = "maintenance" 
    OFFLINE = "offline"
    DEPLOYED = "deployed"
    RETURNING = "returning"


def create_agent_payload(agent_type: AgentType, name: str, 
                        capabilities: List[AgentCapability] = None,
                        location: str = None,
                        custom_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create a standardized agent registration payload
    
    Args:
        agent_type: Type of agent
        name: Agent name/identifier
        capabilities: List of agent capabilities
        location: Agent location/position
        custom_data: Additional custom data
        
    Returns:
        Dict containing standardized agent payload
    """
    if capabilities is None:
        capabilities = _get_default_capabilities(agent_type)
    
    payload = {
        "name": name,
        "type": agent_type.value,
        "capabilities": [cap.value for cap in capabilities] if capabilities else [],
        "status": AgentStatus.STANDBY.value,
        "location": location or "Unknown",
        "health_score": 100.0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "agent_class": agent_type.value,
            "initialization_time": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0"
        }
    }
    
    if custom_data:
        payload["metadata"].update(custom_data)
    
    return payload


def _get_default_capabilities(agent_type: AgentType) -> List[AgentCapability]:
    """Get default capabilities for an agent type"""
    capability_map = {
        AgentType.SCOUT: [
            AgentCapability.RECONNAISSANCE,
            AgentCapability.COMMUNICATION,
            AgentCapability.MONITORING
        ],
        AgentType.GUARDIAN: [
            AgentCapability.COMBAT,
            AgentCapability.MONITORING,
            AgentCapability.COORDINATION
        ],
        AgentType.ANALYST: [
            AgentCapability.ANALYSIS,
            AgentCapability.COMMUNICATION,
            AgentCapability.MONITORING
        ],
        AgentType.COORDINATOR: [
            AgentCapability.COORDINATION,
            AgentCapability.COMMUNICATION,
            AgentCapability.LOGISTICS
        ],
        AgentType.SPECIALIST: [
            AgentCapability.ANALYSIS,
            AgentCapability.REPAIR,
            AgentCapability.LOGISTICS
        ],
        AgentType.MAINTENANCE: [
            AgentCapability.REPAIR,
            AgentCapability.MONITORING
        ]
    }
    
    return capability_map.get(agent_type, [])


# Current registry payloads - Pre-defined agents for the SR-AIbridge system
current_registry_payloads = {
    "agents": [
        create_agent_payload(
            agent_type=AgentType.SCOUT,
            name="Agent Alpha",
            location="Sector 7-Alpha",
            custom_data={
                "specialization": "long_range_reconnaissance",
                "sensor_array": "enhanced",
                "endurance_rating": "high"
            }
        ),
        
        create_agent_payload(
            agent_type=AgentType.GUARDIAN,
            name="Agent Beta",
            location="Central Command",
            custom_data={
                "armor_class": "heavy",
                "weapon_systems": ["plasma_cannon", "shield_generator"],
                "defensive_rating": "maximum"
            }
        ),
        
        create_agent_payload(
            agent_type=AgentType.ANALYST,
            name="Agent Gamma",
            location="Data Processing Center",
            custom_data={
                "processing_power": "quantum_enhanced",
                "analysis_modules": ["pattern_recognition", "predictive_modeling"],
                "clearance_level": "classified"
            }
        ),
        
        create_agent_payload(
            agent_type=AgentType.COORDINATOR,
            name="Agent Delta",
            location="Operations Hub",
            custom_data={
                "command_authority": "tactical",
                "communication_range": "system_wide",
                "coordination_protocols": ["fleet_command", "resource_allocation"]
            }
        ),
        
        create_agent_payload(
            agent_type=AgentType.SPECIALIST,
            name="Agent Epsilon",
            location="Engineering Bay",
            custom_data={
                "specialization": "xenoarchaeology",
                "tools": ["quantum_scanner", "temporal_analyzer"],
                "expertise_level": "expert"
            }
        ),
        
        create_agent_payload(
            agent_type=AgentType.MAINTENANCE,
            name="Agent Zeta",
            location="Maintenance Deck",
            custom_data={
                "repair_systems": ["nano_repair", "structural_welding"],
                "maintenance_scope": "ship_wide",
                "diagnostic_capabilities": "full_spectrum"
            }
        )
    ],
    
    "mission_templates": [
        {
            "title": "Nebula Survey Alpha-7",
            "description": "Comprehensive survey of the Alpha-7 nebula system for strategic resources and potential threats",
            "priority": "high",
            "estimated_duration": "72 hours",
            "required_capabilities": [
                AgentCapability.RECONNAISSANCE.value,
                AgentCapability.ANALYSIS.value,
                AgentCapability.COMMUNICATION.value
            ],
            "objectives": [
                "Map nebula structure and composition",
                "Scan for strategic resources",
                "Assess potential threats",
                "Establish communication relay points"
            ],
            "risk_level": "medium"
        },
        
        {
            "title": "Supply Chain Optimization",
            "description": "Optimize supply chain logistics for maximum efficiency and resource allocation",
            "priority": "normal",
            "estimated_duration": "48 hours",
            "required_capabilities": [
                AgentCapability.LOGISTICS.value,
                AgentCapability.ANALYSIS.value,
                AgentCapability.COORDINATION.value
            ],
            "objectives": [
                "Analyze current supply routes",
                "Identify optimization opportunities", 
                "Implement improved logistics protocols",
                "Monitor performance metrics"
            ],
            "risk_level": "low"
        },
        
        {
            "title": "Communication Array Maintenance",
            "description": "Routine maintenance and upgrade of long-range communication systems",
            "priority": "normal",
            "estimated_duration": "24 hours",
            "required_capabilities": [
                AgentCapability.REPAIR.value,
                AgentCapability.MONITORING.value,
                AgentCapability.COMMUNICATION.value
            ],
            "objectives": [
                "Inspect communication array components",
                "Replace worn or damaged parts",
                "Upgrade signal processing units",
                "Test communication range and clarity"
            ],
            "risk_level": "low"
        },
        
        {
            "title": "Threat Assessment Protocol Gamma",
            "description": "Advanced threat assessment of unknown contacts in Sector 12",
            "priority": "critical",
            "estimated_duration": "36 hours",
            "required_capabilities": [
                AgentCapability.RECONNAISSANCE.value,
                AgentCapability.COMBAT.value,
                AgentCapability.ANALYSIS.value,
                AgentCapability.COORDINATION.value
            ],
            "objectives": [
                "Conduct stealth reconnaissance of unknown contacts",
                "Analyze threat capabilities and intentions",
                "Develop tactical response options",
                "Coordinate with fleet command"
            ],
            "risk_level": "high"
        }
    ],
    
    "vault_log_templates": [
        {
            "category": "system_initialization",
            "title": "SR-AIbridge System Initialization",
            "content": "Core systems online. All primary subsystems operational. Agent registry populated with standard deployment configuration.",
            "classification": "operational",
            "metadata": {
                "system_version": "2.0.0",
                "initialization_time": datetime.now(timezone.utc).isoformat(),
                "components_initialized": [
                    "agent_registry",
                    "mission_control",
                    "communication_array",
                    "defense_systems",
                    "life_support"
                ]
            }
        },
        
        {
            "category": "mission_assignment",
            "title": "Mission Assignment Protocol",
            "content": "Standard operating procedures for mission assignment and agent deployment. Includes capability matching and risk assessment protocols.",
            "classification": "tactical",
            "metadata": {
                "protocol_version": "3.1",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "approval_authority": "Fleet Command"
            }
        },
        
        {
            "category": "communication_established",
            "title": "Long-Range Communication Protocols",
            "content": "Quantum entanglement communication network established. Secure channels verified with Fleet Command and allied vessels.",
            "classification": "communication",
            "metadata": {
                "network_nodes": 12,
                "encryption_level": "quantum",
                "range": "system_wide"
            }
        },
        
        {
            "category": "logistics_optimized",
            "title": "Supply Chain Logistics Optimization",
            "content": "Resource allocation algorithms updated. Supply chain efficiency improved by 23%. Automated resupply protocols activated.",
            "classification": "logistical",
            "metadata": {
                "efficiency_gain": 0.23,
                "resources_managed": [
                    "energy_cells",
                    "raw_materials",
                    "food_supplies",
                    "medical_supplies",
                    "ammunition"
                ],
                "optimization_algorithm": "quantum_annealing_v2"
            }
        }
    ],
    
    "system_capabilities": [
        {
            "name": "agent_management",
            "description": "Comprehensive agent lifecycle management",
            "features": [
                "agent_registration",
                "capability_assessment",
                "performance_monitoring",
                "deployment_coordination"
            ]
        },
        
        {
            "name": "mission_control",
            "description": "Advanced mission planning and execution",
            "features": [
                "mission_planning",
                "resource_allocation",
                "progress_tracking",
                "risk_assessment"
            ]
        },
        
        {
            "name": "federation_support",
            "description": "Cross-bridge communication and coordination",
            "features": [
                "task_forwarding",
                "heartbeat_signaling",
                "load_balancing",
                "distributed_coordination"
            ]
        },
        
        {
            "name": "self_healing",
            "description": "Autonomous system recovery and adaptation",
            "features": [
                "error_detection",
                "automatic_recovery",
                "message_reconstruction",
                "fallback_protocols"
            ]
        }
    ],
    
    "metadata": {
        "version": "2.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "registry_type": "sr_aibridge_standard",
        "total_agents": 6,
        "total_mission_templates": 4,
        "total_vault_logs": 4,
        "capabilities_count": 4
    }
}


def get_agent_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get agent payload by name"""
    for agent in current_registry_payloads["agents"]:
        if agent["name"] == name:
            return agent
    return None


def get_agents_by_type(agent_type: AgentType) -> List[Dict[str, Any]]:
    """Get all agents of a specific type"""
    return [
        agent for agent in current_registry_payloads["agents"]
        if agent["type"] == agent_type.value
    ]


def get_agents_by_capability(capability: AgentCapability) -> List[Dict[str, Any]]:
    """Get all agents with a specific capability"""
    return [
        agent for agent in current_registry_payloads["agents"]
        if capability.value in agent["capabilities"]
    ]


def get_mission_template_by_title(title: str) -> Optional[Dict[str, Any]]:
    """Get mission template by title"""
    for mission in current_registry_payloads["mission_templates"]:
        if mission["title"] == title:
            return mission
    return None


def validate_agent_payload(payload: Dict[str, Any]) -> bool:
    """Validate that an agent payload has required fields"""
    required_fields = ["name", "type", "capabilities", "status", "location", "health_score"]
    
    for field in required_fields:
        if field not in payload:
            return False
    
    # Validate agent type
    try:
        AgentType(payload["type"])
    except ValueError:
        return False
    
    # Validate status
    try:
        AgentStatus(payload["status"])
    except ValueError:
        return False
    
    return True


def update_agent_health(agent_name: str, health_score: float) -> bool:
    """Update health score for an agent"""
    for agent in current_registry_payloads["agents"]:
        if agent["name"] == agent_name:
            agent["health_score"] = max(0.0, min(100.0, health_score))
            agent["metadata"]["last_health_update"] = datetime.now(timezone.utc).isoformat()
            return True
    return False


def update_agent_status(agent_name: str, status: AgentStatus) -> bool:
    """Update status for an agent"""
    for agent in current_registry_payloads["agents"]:
        if agent["name"] == agent_name:
            agent["status"] = status.value
            agent["metadata"]["last_status_update"] = datetime.now(timezone.utc).isoformat()
            return True
    return False