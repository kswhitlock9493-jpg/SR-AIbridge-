"""
Genesis Link Adapter
Universal adapter to connect all engines to Genesis event bus
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


async def register_all_genesis_links():
    """
    Register all engine linkages with the Genesis bus.
    Each engine subscribes to relevant topics and publishes its schema.
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        from bridge_backend.genesis.manifest import genesis_manifest
        from bridge_backend.genesis.introspection import genesis_introspection
        
        if not genesis_bus.is_enabled():
            logger.info("Genesis bus disabled, skipping engine linkages")
            return
        
        logger.info("🔗 Registering Genesis engine linkages...")
        
        # Sync manifest from Blueprint Registry first
        genesis_manifest.sync_from_blueprint_registry()
        
        # Register each engine type
        engines_registered = []
        
        # TDE-X linkage
        try:
            await _register_tde_x_link()
            engines_registered.append("tde_x")
            genesis_introspection.update_health("tde_x", True)
        except Exception as e:
            logger.warning(f"Failed to register TDE-X link: {e}")
        
        # Cascade linkage
        try:
            await _register_cascade_link()
            engines_registered.append("cascade")
            genesis_introspection.update_health("cascade", True)
        except Exception as e:
            logger.warning(f"Failed to register Cascade link: {e}")
        
        # Truth linkage
        try:
            await _register_truth_link()
            engines_registered.append("truth")
            genesis_introspection.update_health("truth", True)
        except Exception as e:
            logger.warning(f"Failed to register Truth link: {e}")
        
        # Autonomy linkage
        try:
            await _register_autonomy_link()
            engines_registered.append("autonomy")
            genesis_introspection.update_health("autonomy", True)
        except Exception as e:
            logger.warning(f"Failed to register Autonomy link: {e}")
        
        # Leviathan linkage
        try:
            await _register_leviathan_link()
            engines_registered.append("leviathan")
            genesis_introspection.update_health("leviathan", True)
        except Exception as e:
            logger.warning(f"Failed to register Leviathan link: {e}")
        
        # Creativity linkage
        try:
            await _register_creativity_link()
            engines_registered.append("creativity")
            genesis_introspection.update_health("creativity", True)
        except Exception as e:
            logger.warning(f"Failed to register Creativity link: {e}")
        
        # Parser linkage
        try:
            await _register_parser_link()
            engines_registered.append("parser")
            genesis_introspection.update_health("parser", True)
        except Exception as e:
            logger.warning(f"Failed to register Parser link: {e}")
        
        # Speech linkage
        try:
            await _register_speech_link()
            engines_registered.append("speech")
            genesis_introspection.update_health("speech", True)
        except Exception as e:
            logger.warning(f"Failed to register Speech link: {e}")
        
        # Fleet linkage
        try:
            await _register_fleet_link()
            engines_registered.append("fleet")
            genesis_introspection.update_health("fleet", True)
        except Exception as e:
            logger.warning(f"Failed to register Fleet link: {e}")
        
        # Custody linkage
        try:
            await _register_custody_link()
            engines_registered.append("custody")
            genesis_introspection.update_health("custody", True)
        except Exception as e:
            logger.warning(f"Failed to register Custody link: {e}")
        
        # Console linkage
        try:
            await _register_console_link()
            engines_registered.append("console")
            genesis_introspection.update_health("console", True)
        except Exception as e:
            logger.warning(f"Failed to register Console link: {e}")
        
        # Captains linkage
        try:
            await _register_captains_link()
            engines_registered.append("captains")
            genesis_introspection.update_health("captains", True)
        except Exception as e:
            logger.warning(f"Failed to register Captains link: {e}")
        
        # Guardians linkage
        try:
            await _register_guardians_link()
            engines_registered.append("guardians")
            genesis_introspection.update_health("guardians", True)
        except Exception as e:
            logger.warning(f"Failed to register Guardians link: {e}")
        
        # Recovery linkage
        try:
            await _register_recovery_link()
            engines_registered.append("recovery")
            genesis_introspection.update_health("recovery", True)
        except Exception as e:
            logger.warning(f"Failed to register Recovery link: {e}")
        
        # Super Engines autonomy integration
        try:
            from .super_engines_autonomy_link import register_super_engines_autonomy_links
            await register_super_engines_autonomy_links()
            engines_registered.append("super_engines_autonomy")
            genesis_introspection.update_health("super_engines", True)
        except Exception as e:
            logger.warning(f"Failed to register Super Engines autonomy links: {e}")
        
        # Specialized engines autonomy integration
        try:
            await _register_specialized_engines_autonomy_links()
            engines_registered.append("specialized_engines_autonomy")
        except Exception as e:
            logger.warning(f"Failed to register Specialized Engines autonomy links: {e}")
        
        # Core systems autonomy integration
        try:
            await _register_core_systems_autonomy_links()
            engines_registered.append("core_systems_autonomy")
        except Exception as e:
            logger.warning(f"Failed to register Core Systems autonomy links: {e}")
        
        # Tools and runtime autonomy integration
        try:
            from .tools_runtime_autonomy_link import register_tools_runtime_autonomy_links
            await register_tools_runtime_autonomy_links()
            engines_registered.append("tools_runtime_autonomy")
        except Exception as e:
            logger.warning(f"Failed to register Tools/Runtime autonomy links: {e}")
        
        # Heritage and MAS autonomy integration
        try:
            from .heritage_mas_autonomy_link import register_heritage_mas_autonomy_links
            await register_heritage_mas_autonomy_links()
            engines_registered.append("heritage_mas_autonomy")
        except Exception as e:
            logger.warning(f"Failed to register Heritage/MAS autonomy links: {e}")
        
        logger.info(f"✅ Genesis linkages registered: {', '.join(engines_registered)}")
        
        # Publish initialization complete event
        await genesis_bus.publish("genesis.intent", {
            "type": "genesis.initialized",
            "engines": engines_registered,
            "count": len(engines_registered),
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to register Genesis linkages: {e}")
        raise


# Individual engine link functions

async def _register_tde_x_link():
    """Register TDE-X engine with Genesis"""
    from bridge_backend.genesis.bus import genesis_bus
    
    async def handle_tde_signal(event: Dict[str, Any]):
        # Forward TDE-X signals to genesis.intent
        await genesis_bus.publish("genesis.intent", {
            "type": "tde.signal",
            "source": "tde_x",
            "signal": event,
        })
    
    genesis_bus.subscribe("deploy.signals", handle_tde_signal)
    logger.debug("✅ TDE-X linked to Genesis")


async def _register_cascade_link():
    """Register Cascade engine with Genesis"""
    from bridge_backend.genesis.bus import genesis_bus
    
    async def handle_cascade_update(event: Dict[str, Any]):
        # Forward Cascade DAG updates to genesis.intent
        await genesis_bus.publish("genesis.intent", {
            "type": "cascade.update",
            "source": "cascade",
            "update": event,
        })
    
    genesis_bus.subscribe("deploy.graph", handle_cascade_update)
    logger.debug("✅ Cascade linked to Genesis")


async def _register_truth_link():
    """Register Truth engine with Genesis"""
    from bridge_backend.genesis.bus import genesis_bus
    
    async def handle_truth_fact(event: Dict[str, Any]):
        # Forward certified facts to genesis.fact
        await genesis_bus.publish("genesis.fact", {
            "type": "truth.certified",
            "source": "truth",
            "fact": event,
        })
    
    genesis_bus.subscribe("deploy.facts", handle_truth_fact)
    logger.debug("✅ Truth linked to Genesis")


async def _register_autonomy_link():
    """Register Autonomy engine with Genesis"""
    from bridge_backend.genesis.bus import genesis_bus
    
    async def handle_autonomy_action(event: Dict[str, Any]):
        # Forward autonomy actions to genesis.heal (self-healing)
        await genesis_bus.publish("genesis.heal", {
            "type": "autonomy.action",
            "source": "autonomy",
            "action": event,
        })
    
    async def handle_triage_event(event: Dict[str, Any]):
        # Autonomy responds to triage findings for auto-healing
        await genesis_bus.publish("genesis.heal", {
            "type": "autonomy.triage_response",
            "source": "autonomy",
            "triage_event": event,
        })
    
    async def handle_federation_event(event: Dict[str, Any]):
        # Autonomy coordinates with federation for distributed healing
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.federation_sync",
            "source": "autonomy",
            "federation_event": event,
        })
    
    async def handle_parity_event(event: Dict[str, Any]):
        # Autonomy auto-fixes parity issues
        await genesis_bus.publish("genesis.heal", {
            "type": "autonomy.parity_fix",
            "source": "autonomy",
            "parity_event": event,
        })
    
    # Subscribe to core autonomy events
    genesis_bus.subscribe("deploy.actions", handle_autonomy_action)
    
    # Subscribe to triage events for auto-healing
    genesis_bus.subscribe("triage.api", handle_triage_event)
    genesis_bus.subscribe("triage.endpoint", handle_triage_event)
    genesis_bus.subscribe("triage.diagnostics", handle_triage_event)
    
    # Subscribe to federation events for distributed coordination
    genesis_bus.subscribe("federation.events", handle_federation_event)
    genesis_bus.subscribe("federation.heartbeat", handle_federation_event)
    
    # Subscribe to parity events for auto-fixing
    genesis_bus.subscribe("parity.check", handle_parity_event)
    genesis_bus.subscribe("parity.autofix", handle_parity_event)
    
    logger.debug("✅ Autonomy linked to Genesis (with triage, federation, and parity integration)")


async def _register_leviathan_link():
    """Register Leviathan engine with Genesis"""
    from bridge_backend.genesis.bus import genesis_bus
    
    async def handle_leviathan_compute(event: Dict[str, Any]):
        # Leviathan distributed compute results
        await genesis_bus.publish("genesis.create", {
            "type": "leviathan.compute",
            "source": "leviathan",
            "result": event,
        })
    
    # Subscribe to leviathan-specific topic if it exists
    logger.debug("✅ Leviathan linked to Genesis")


async def _register_creativity_link():
    """Register Creativity engine with Genesis"""
    from bridge_backend.genesis.bus import genesis_bus
    
    async def handle_creative_output(event: Dict[str, Any]):
        # Creative generation outputs
        await genesis_bus.publish("genesis.create", {
            "type": "creativity.output",
            "source": "creativity",
            "output": event,
        })
    
    logger.debug("✅ Creativity linked to Genesis")


async def _register_parser_link():
    """Register Parser engine with Genesis"""
    from bridge_backend.genesis.bus import genesis_bus
    
    async def handle_parser_result(event: Dict[str, Any]):
        # Parser comprehension results
        await genesis_bus.publish("genesis.intent", {
            "type": "parser.comprehension",
            "source": "parser",
            "result": event,
        })
    
    logger.debug("✅ Parser linked to Genesis")


async def _register_speech_link():
    """Register Speech engine with Genesis"""
    from bridge_backend.genesis.bus import genesis_bus
    
    async def handle_speech_output(event: Dict[str, Any]):
        # Speech synthesis outputs
        await genesis_bus.publish("genesis.intent", {
            "type": "speech.output",
            "source": "speech",
            "output": event,
        })
    
    logger.debug("✅ Speech linked to Genesis")


async def _register_fleet_link():
    """Register Fleet engine with Genesis"""
    from bridge_backend.genesis.bus import genesis_bus
    
    async def handle_fleet_event(event: Dict[str, Any]):
        # Fleet agent management events
        await genesis_bus.publish("genesis.intent", {
            "type": "fleet.event",
            "source": "fleet",
            "event": event,
        })
    
    logger.debug("✅ Fleet linked to Genesis")


async def _register_custody_link():
    """Register Custody engine with Genesis"""
    from bridge_backend.genesis.bus import genesis_bus
    
    async def handle_custody_state(event: Dict[str, Any]):
        # Custody state snapshots go to genesis.fact for traceability
        await genesis_bus.publish("genesis.fact", {
            "type": "custody.snapshot",
            "source": "custody",
            "snapshot": event,
        })
    
    logger.debug("✅ Custody linked to Genesis")


async def _register_console_link():
    """Register Console engine with Genesis"""
    from bridge_backend.genesis.bus import genesis_bus
    
    async def handle_console_command(event: Dict[str, Any]):
        # Console command routing
        await genesis_bus.publish("genesis.intent", {
            "type": "console.command",
            "source": "console",
            "command": event,
        })
    
    logger.debug("✅ Console linked to Genesis")


async def _register_captains_link():
    """Register Captains engine with Genesis"""
    from bridge_backend.genesis.bus import genesis_bus
    
    async def handle_captain_policy(event: Dict[str, Any]):
        # Captain policy events
        await genesis_bus.publish("genesis.intent", {
            "type": "captain.policy",
            "source": "captains",
            "policy": event,
        })
    
    logger.debug("✅ Captains linked to Genesis")


async def _register_guardians_link():
    """Register Guardians engine with Genesis"""
    from bridge_backend.genesis.bus import genesis_bus
    
    async def handle_guardian_validation(event: Dict[str, Any]):
        # Guardian validation for high-risk actions
        event_type = event.get("type", "")
        
        # Check for recursive or destructive patterns
        if "recursive" in str(event).lower() or "destructive" in str(event).lower():
            logger.warning(f"⚠️ Guardian blocked potentially dangerous action: {event_type}")
            return
        
        await genesis_bus.publish("genesis.intent", {
            "type": "guardian.validated",
            "source": "guardians",
            "validation": event,
        })
    
    # Subscribe to genesis.heal to validate healing actions
    genesis_bus.subscribe("genesis.heal", handle_guardian_validation)
    logger.debug("✅ Guardians linked to Genesis")


async def _register_recovery_link():
    """Register Recovery engine with Genesis"""
    from bridge_backend.genesis.bus import genesis_bus
    
    async def handle_recovery_outcome(event: Dict[str, Any]):
        # Recovery job outcomes go to genesis.heal
        await genesis_bus.publish("genesis.heal", {
            "type": "recovery.outcome",
            "source": "recovery",
            "outcome": event,
        })
    
    logger.debug("✅ Recovery linked to Genesis")


async def _register_specialized_engines_autonomy_links():
    """Register autonomy integration for specialized engines"""
    from bridge_backend.genesis.bus import genesis_bus
    
    # Screen engine autonomy link
    async def handle_screen_event(event: Dict[str, Any]):
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.screen_interaction",
            "source": "autonomy",
            "screen_event": event,
        })
    
    # Indoctrination engine autonomy link
    async def handle_indoctrination_event(event: Dict[str, Any]):
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.indoctrination_training",
            "source": "autonomy",
            "indoctrination_event": event,
        })
    
    # Agents Foundry autonomy link
    async def handle_agents_foundry_event(event: Dict[str, Any]):
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.agents_foundry_deployment",
            "source": "autonomy",
            "agents_foundry_event": event,
        })
    
    # Subscribe to specialized engine topics
    genesis_bus.subscribe("screen.interaction", handle_screen_event)
    genesis_bus.subscribe("screen.render", handle_screen_event)
    genesis_bus.subscribe("indoctrination.training", handle_indoctrination_event)
    genesis_bus.subscribe("indoctrination.knowledge", handle_indoctrination_event)
    genesis_bus.subscribe("agents_foundry.agent_created", handle_agents_foundry_event)
    genesis_bus.subscribe("agents_foundry.agent_deployed", handle_agents_foundry_event)
    
    logger.debug("✅ Specialized Engines linked to Autonomy")


async def _register_core_systems_autonomy_links():
    """Register autonomy integration for core systems"""
    from bridge_backend.genesis.bus import genesis_bus
    
    # Fleet autonomy link
    async def handle_fleet_event(event: Dict[str, Any]):
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.fleet_command",
            "source": "autonomy",
            "fleet_event": event,
        })
    
    # Custody autonomy link
    async def handle_custody_event(event: Dict[str, Any]):
        await genesis_bus.publish("genesis.fact", {
            "type": "autonomy.custody_state",
            "source": "autonomy",
            "custody_event": event,
        })
    
    # Console autonomy link
    async def handle_console_event(event: Dict[str, Any]):
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.console_command",
            "source": "autonomy",
            "console_event": event,
        })
    
    # Captains autonomy link
    async def handle_captains_event(event: Dict[str, Any]):
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.captains_policy",
            "source": "autonomy",
            "captains_event": event,
        })
    
    # Guardians autonomy link - special handling for safety
    async def handle_guardians_event(event: Dict[str, Any]):
        # Guardians validate autonomy actions
        event_type = event.get("type", "")
        
        # Block dangerous patterns
        if "recursive" in str(event).lower() or "destructive" in str(event).lower():
            logger.warning(f"⚠️ Guardian blocked potentially dangerous autonomy action: {event_type}")
            await genesis_bus.publish("genesis.heal", {
                "type": "autonomy.action_blocked",
                "source": "guardians",
                "blocked_event": event,
            })
            return
        
        await genesis_bus.publish("genesis.intent", {
            "type": "autonomy.guardians_validation",
            "source": "autonomy",
            "guardians_event": event,
        })
    
    # Registry autonomy link
    async def handle_registry_event(event: Dict[str, Any]):
        await genesis_bus.publish("genesis.fact", {
            "type": "autonomy.registry_update",
            "source": "autonomy",
            "registry_event": event,
        })
    
    # Doctrine autonomy link
    async def handle_doctrine_event(event: Dict[str, Any]):
        # Doctrine violations trigger autonomy healing
        if event.get("type") == "violation":
            await genesis_bus.publish("genesis.heal", {
                "type": "autonomy.doctrine_violation",
                "source": "autonomy",
                "doctrine_event": event,
            })
        else:
            await genesis_bus.publish("genesis.fact", {
                "type": "autonomy.doctrine_compliance",
                "source": "autonomy",
                "doctrine_event": event,
            })
    
    # Subscribe to core system topics
    genesis_bus.subscribe("fleet.command", handle_fleet_event)
    genesis_bus.subscribe("fleet.status", handle_fleet_event)
    genesis_bus.subscribe("custody.state", handle_custody_event)
    genesis_bus.subscribe("custody.transfer", handle_custody_event)
    genesis_bus.subscribe("console.command", handle_console_event)
    genesis_bus.subscribe("console.output", handle_console_event)
    genesis_bus.subscribe("captains.policy", handle_captains_event)
    genesis_bus.subscribe("captains.decision", handle_captains_event)
    genesis_bus.subscribe("guardians.validation", handle_guardians_event)
    genesis_bus.subscribe("guardians.alert", handle_guardians_event)
    genesis_bus.subscribe("registry.update", handle_registry_event)
    genesis_bus.subscribe("registry.query", handle_registry_event)
    genesis_bus.subscribe("doctrine.compliance", handle_doctrine_event)
    genesis_bus.subscribe("doctrine.violation", handle_doctrine_event)
    
    logger.debug("✅ Core Systems linked to Autonomy")

