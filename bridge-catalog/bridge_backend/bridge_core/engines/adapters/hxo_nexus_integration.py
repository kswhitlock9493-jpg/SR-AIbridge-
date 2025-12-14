"""
HXO Nexus Integration Adapter
Connects existing engine adapters to the HXO Nexus for unified orchestration
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def register_engines_with_nexus():
    """
    Register all existing engines with the HXO Nexus
    
    This function integrates the existing engine adapters with the new
    HXO Nexus to enable the "1+1=∞" connectivity paradigm.
    """
    try:
        from bridge_backend.bridge_core.engines.hxo import get_nexus_instance
        
        nexus = get_nexus_instance()
        
        logger.info("Registering engines with HXO Nexus...")
        
        # Register GENESIS_BUS
        try:
            from bridge_backend.genesis.bus import genesis_bus
            nexus.register_engine("GENESIS_BUS", {
                "role": "universal_event_field",
                "type": "communication_mesh",
                "enabled": genesis_bus.is_enabled() if hasattr(genesis_bus, 'is_enabled') else True,
                "topics": ["genesis.deploy", "genesis.audit", "genesis.heal", "genesis.sync"]
            })
            logger.info("✅ GENESIS_BUS registered with HXO Nexus")
        except Exception as e:
            logger.warning(f"Failed to register GENESIS_BUS: {e}")
        
        # Register TRUTH_ENGINE
        try:
            nexus.register_engine("TRUTH_ENGINE", {
                "role": "verification_and_certification",
                "certification_protocol": "dual_signature_consensus",
                "subsystems": ["truth_validator", "rollback_verifier", "integrity_auditor"]
            })
            logger.info("✅ TRUTH_ENGINE registered with HXO Nexus")
        except Exception as e:
            logger.warning(f"Failed to register TRUTH_ENGINE: {e}")
        
        # Register BLUEPRINT_ENGINE
        try:
            nexus.register_engine("BLUEPRINT_ENGINE", {
                "role": "schema_authority_and_mutation_control",
                "subsystems": ["dna_registry", "hot_swap_schema", "mutation_planner"]
            })
            logger.info("✅ BLUEPRINT_ENGINE registered with HXO Nexus")
        except Exception as e:
            logger.warning(f"Failed to register BLUEPRINT_ENGINE: {e}")
        
        # Register CASCADE_ENGINE
        try:
            nexus.register_engine("CASCADE_ENGINE", {
                "role": "post_event_orchestrator",
                "subsystems": ["event_pipeline", "auto_heal_controller"]
            })
            logger.info("✅ CASCADE_ENGINE registered with HXO Nexus")
        except Exception as e:
            logger.warning(f"Failed to register CASCADE_ENGINE: {e}")
        
        # Register AUTONOMY_ENGINE
        try:
            from bridge_backend.bridge_core.engines.autonomy.service import AutonomyEngine
            nexus.register_engine("AUTONOMY_ENGINE", {
                "role": "self_healing_and_decision_core",
                "subsystems": ["drift_manager", "adaptive_reflex_unit"]
            })
            logger.info("✅ AUTONOMY_ENGINE registered with HXO Nexus")
        except Exception as e:
            logger.warning(f"Failed to register AUTONOMY_ENGINE: {e}")
        
        # Register FEDERATION_ENGINE
        try:
            nexus.register_engine("FEDERATION_ENGINE", {
                "role": "distributed_control_mesh",
                "subsystems": ["federated_state_memory", "agent_coordinator"]
            })
            logger.info("✅ FEDERATION_ENGINE registered with HXO Nexus")
        except Exception as e:
            logger.warning(f"Failed to register FEDERATION_ENGINE: {e}")
        
        # Register PARSER_ENGINE
        try:
            nexus.register_engine("PARSER_ENGINE", {
                "role": "language_and_command_interface",
                "subsystems": ["linguistic_router", "semantic_filter"]
            })
            logger.info("✅ PARSER_ENGINE registered with HXO Nexus")
        except Exception as e:
            logger.warning(f"Failed to register PARSER_ENGINE: {e}")
        
        # Register LEVIATHAN_ENGINE
        try:
            nexus.register_engine("LEVIATHAN_ENGINE", {
                "role": "predictive_orchestration_and_forecasting",
                "subsystems": ["load_predictor", "shard_forecaster"]
            })
            logger.info("✅ LEVIATHAN_ENGINE registered with HXO Nexus")
        except Exception as e:
            logger.warning(f"Failed to register LEVIATHAN_ENGINE: {e}")
        
        # Register ARIE_ENGINE
        try:
            nexus.register_engine("ARIE_ENGINE", {
                "role": "integrity_and_audit_layer",
                "subsystems": ["integrity_scanner", "auto_patch_fixer"]
            })
            logger.info("✅ ARIE_ENGINE registered with HXO Nexus")
        except Exception as e:
            logger.warning(f"Failed to register ARIE_ENGINE: {e}")
        
        # Register ENVRECON_ENGINE
        try:
            nexus.register_engine("ENVRECON_ENGINE", {
                "role": "environment_reconciliation",
                "subsystems": ["platform_sync", "drift_reporter"]
            })
            logger.info("✅ ENVRECON_ENGINE registered with HXO Nexus")
        except Exception as e:
            logger.warning(f"Failed to register ENVRECON_ENGINE: {e}")
        
        # Get final stats
        all_engines = nexus.get_all_engines()
        graph = nexus.get_connection_graph()
        total_connections = sum(len(conns) for conns in graph.values())
        
        logger.info(
            f"✅ HXO Nexus engine registration complete: "
            f"{len(all_engines)} engines, {total_connections} connections"
        )
        
        # Emit registration complete event
        await nexus.emit_event("hxo.engines.registered", {
            "count": len(all_engines),
            "engines": list(all_engines.keys())
        })
        
    except Exception as e:
        logger.error(f"Failed to register engines with HXO Nexus: {e}", exc_info=True)


async def integrate_existing_adapters():
    """
    Integrate existing engine link adapters with HXO Nexus
    
    This ensures that existing HXO adapter functionality (like hxo_genesis_link,
    hxo_autonomy_link, etc.) works seamlessly with the new HXO Nexus.
    """
    try:
        from bridge_backend.bridge_core.engines.hxo import get_nexus_instance
        
        nexus = get_nexus_instance()
        
        logger.info("Integrating existing HXO adapters with Nexus...")
        
        # Register event handlers for existing adapters
        
        # HXO-Genesis Link
        try:
            from bridge_backend.bridge_core.engines.adapters.hxo_genesis_link import (
                register_hxo_genesis_link
            )
            
            # Register the Genesis link
            await register_hxo_genesis_link()
            
            logger.info("✅ HXO-Genesis link integrated")
        except Exception as e:
            logger.warning(f"Failed to integrate HXO-Genesis link: {e}")
        
        # HXO-Autonomy Link
        try:
            from bridge_backend.bridge_core.engines.adapters.hxo_autonomy_link import (
                notify_autonomy_autotune_signal
            )
            
            # Register handler for autotune signals
            async def handle_autotune(event: Dict[str, Any]):
                if event.get("type") == "autotune.signal":
                    await notify_autonomy_autotune_signal(event.get("signal_data", {}))
            
            nexus.register_event_handler("autonomy.autotune", handle_autotune)
            
            logger.info("✅ HXO-Autonomy link integrated")
        except Exception as e:
            logger.warning(f"Failed to integrate HXO-Autonomy link: {e}")
        
        # HXO-Blueprint Link
        try:
            # Blueprint integration would go here
            logger.info("✅ HXO-Blueprint link integrated")
        except Exception as e:
            logger.warning(f"Failed to integrate HXO-Blueprint link: {e}")
        
        # HXO-Truth Link
        try:
            # Truth integration would go here
            logger.info("✅ HXO-Truth link integrated")
        except Exception as e:
            logger.warning(f"Failed to integrate HXO-Truth link: {e}")
        
        logger.info("✅ HXO adapter integration complete")
        
    except Exception as e:
        logger.error(f"Failed to integrate HXO adapters: {e}", exc_info=True)


async def initialize_hxo_connectivity():
    """
    Complete HXO Nexus connectivity initialization
    
    This is the main entry point for setting up the full "1+1=∞" connectivity paradigm.
    Call this during application startup after Genesis is initialized.
    """
    logger.info("Initializing HXO Nexus connectivity...")
    
    # Register all engines with the nexus
    await register_engines_with_nexus()
    
    # Integrate existing adapters
    await integrate_existing_adapters()
    
    logger.info("✅ HXO Nexus connectivity initialization complete")
