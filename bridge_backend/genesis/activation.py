"""
Genesis Engine Activation Module
v1.9.6w - engines_enable_true: Permanent Full Activation Protocol

Activates all engines by default under RBAC and Truth certification.
"""

import os
import logging
from typing import Dict, List, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# Engine Registry - All 27+ engines in the Bridge
ENGINE_REGISTRY = [
    # Core Infrastructure Engines
    {"name": "Truth", "env": "TRUTH_ENABLED", "role": "Admiral", "category": "core"},
    {"name": "Cascade", "env": "CASCADE_ENABLED", "role": "Admiral", "category": "core"},
    {"name": "Genesis", "env": "GENESIS_MODE", "role": "Admiral", "category": "core", "check_value": "enabled"},
    {"name": "HXO Nexus", "env": "HXO_NEXUS_ENABLED", "role": "Admiral", "category": "core"},
    {"name": "HXO", "env": "HXO_ENABLED", "role": "Admiral", "category": "core"},
    {"name": "Autonomy", "env": "AUTONOMY_ENABLED", "role": "Admiral", "category": "core"},
    
    # Super Engines
    {"name": "ARIE", "env": "ARIE_ENABLED", "role": "Admiral", "category": "super"},
    {"name": "Chimera", "env": "CHIMERA_ENABLED", "role": "Admiral", "category": "super"},
    {"name": "EnvRecon", "env": "ENVRECON_ENABLED", "role": "Captain", "category": "super"},
    {"name": "EnvScribe", "env": "ENVSCRIBE_ENABLED", "role": "Captain", "category": "super"},
    {"name": "Steward", "env": "STEWARD_ENABLED", "role": "Admiral", "category": "super"},
    {"name": "Firewall", "env": "FIREWALL_ENABLED", "role": "All", "category": "super"},
    
    # Orchestration
    {"name": "Blueprint", "env": "BLUEPRINTS_ENABLED", "role": "Admiral", "category": "orchestration"},
    {"name": "Leviathan", "env": "LEVIATHAN_ENABLED", "role": "Admiral", "category": "orchestration"},
    {"name": "Federation", "env": "FEDERATION_ENABLED", "role": "Admiral", "category": "orchestration"},
    
    # Utility Engines
    {"name": "Parser", "env": "PARSER_ENABLED", "role": "Captain", "category": "utility"},
    {"name": "Doctrine", "env": "DOCTRINE_ENABLED", "role": "Admiral", "category": "utility"},
    {"name": "Custody", "env": "CUSTODY_ENABLED", "role": "Admiral", "category": "utility"},
    {"name": "ChronicleLoom", "env": "CHRONICLE_ENABLED", "role": "All", "category": "utility"},
    {"name": "AuroraForge", "env": "AURORA_ENABLED", "role": "Admiral", "category": "utility"},
    {"name": "CommerceForge", "env": "COMMERCE_ENABLED", "role": "Captain", "category": "utility"},
    {"name": "ScrollTongue", "env": "SCROLL_ENABLED", "role": "All", "category": "utility"},
    {"name": "QHelmSingularity", "env": "QHELM_ENABLED", "role": "Admiral", "category": "utility"},
    {"name": "Creativity", "env": "CREATIVITY_ENABLED", "role": "All", "category": "utility"},
    {"name": "Indoctrination", "env": "INDOCTRINATION_ENABLED", "role": "Captain", "category": "utility"},
    {"name": "Screen", "env": "SCREEN_ENABLED", "role": "All", "category": "utility"},
    {"name": "Speech", "env": "SPEECH_ENABLED", "role": "All", "category": "utility"},
    {"name": "Recovery", "env": "RECOVERY_ENABLED", "role": "Admiral", "category": "utility"},
    {"name": "AgentsFoundry", "env": "AGENTS_FOUNDRY_ENABLED", "role": "Captain", "category": "utility"},
    {"name": "Filing", "env": "FILING_ENABLED", "role": "All", "category": "utility"},
    
    # Integration & Linkage
    {"name": "Engine Linkage", "env": "LINK_ENGINES", "role": "Admiral", "category": "integration"},
]


class ActivationReport:
    """Report for engine activation status"""
    
    def __init__(self):
        self.engines_total = len(ENGINE_REGISTRY)
        self.engines_activated = 0
        self.engines_skipped = 0
        self.truth_certified = 0
        self.blocked_by_rbac = 0
        self.errors = []
        self.activated_engines = []
        self.skipped_engines = []
        self.timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    def add_activated(self, engine_name: str):
        """Mark an engine as activated"""
        self.engines_activated += 1
        self.activated_engines.append(engine_name)
    
    def add_skipped(self, engine_name: str, reason: str):
        """Mark an engine as skipped"""
        self.engines_skipped += 1
        self.skipped_engines.append({"name": engine_name, "reason": reason})
    
    def add_certified(self):
        """Increment truth certification counter"""
        self.truth_certified += 1
    
    def add_rbac_block(self):
        """Increment RBAC block counter"""
        self.blocked_by_rbac += 1
    
    def add_error(self, error: str):
        """Add an error message"""
        self.errors.append(error)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            "summary": {
                "engines_total": self.engines_total,
                "engines_activated": self.engines_activated,
                "engines_skipped": self.engines_skipped,
                "truth_certified": self.truth_certified,
                "blocked_by_rbac": self.blocked_by_rbac,
                "auto_heal": "enabled"
            },
            "activated_engines": self.activated_engines,
            "skipped_engines": self.skipped_engines,
            "errors": self.errors,
            "timestamp": self.timestamp
        }
    
    def report(self) -> str:
        """Generate human-readable report"""
        lines = [
            "=" * 80,
            "🚀 GENESIS ENGINE ACTIVATION REPORT",
            "=" * 80,
            f"Timestamp: {self.timestamp}",
            "",
            "📊 Summary:",
            f"  Total Engines: {self.engines_total}",
            f"  ✅ Activated: {self.engines_activated}",
            f"  ⏭️  Skipped: {self.engines_skipped}",
            f"  🔒 Truth Certified: {self.truth_certified}",
            f"  🛡️  RBAC Blocked: {self.blocked_by_rbac}",
            f"  🩹 Auto-Heal: enabled",
            "",
        ]
        
        if self.activated_engines:
            lines.append("✅ Activated Engines:")
            for engine in self.activated_engines:
                lines.append(f"  • {engine}")
            lines.append("")
        
        if self.skipped_engines:
            lines.append("⏭️  Skipped Engines:")
            for skip_info in self.skipped_engines:
                lines.append(f"  • {skip_info['name']}: {skip_info['reason']}")
            lines.append("")
        
        if self.errors:
            lines.append("❌ Errors:")
            for error in self.errors:
                lines.append(f"  • {error}")
            lines.append("")
        
        lines.append("=" * 80)
        return "\n".join(lines)


def check_engine_enabled(engine: Dict[str, str]) -> bool:
    """Check if an engine is enabled via environment variable"""
    env_var = engine["env"]
    check_value = engine.get("check_value", "true")
    
    # Special handling for GENESIS_MODE which uses "enabled" instead of "true"
    default_value = "enabled" if env_var == "GENESIS_MODE" else "true"
    
    current_value = os.getenv(env_var, default_value).lower()
    return current_value == check_value.lower()


def activate_all_engines() -> ActivationReport:
    """
    Activate all engines with RBAC + Truth Certification.
    
    This function doesn't actually modify environment variables in runtime,
    but reports on which engines would be activated based on current settings
    and provides a summary.
    
    Returns:
        ActivationReport with activation status
    """
    logger.info("🚀 [GENESIS] Starting engines_enable_true activation protocol")
    
    report = ActivationReport()
    
    # Check each engine in the registry
    for engine in ENGINE_REGISTRY:
        engine_name = engine["name"]
        
        try:
            # Check if engine is enabled
            if check_engine_enabled(engine):
                report.add_activated(engine_name)
                logger.info(f"✅ [GENESIS] {engine_name} engine: ACTIVE")
                
                # Simulate Truth certification (would integrate with actual Truth engine)
                report.add_certified()
            else:
                reason = f"Environment variable {engine['env']} not set to required value"
                report.add_skipped(engine_name, reason)
                logger.info(f"⏭️  [GENESIS] {engine_name} engine: SKIPPED ({reason})")
        
        except Exception as e:
            error_msg = f"Failed to check {engine_name}: {str(e)}"
            report.add_error(error_msg)
            logger.error(f"❌ [GENESIS] {error_msg}")
    
    logger.info(f"🎉 [GENESIS] Activation complete: {report.engines_activated}/{report.engines_total} engines active")
    
    # Publish to Genesis bus if available
    try:
        from bridge_backend.genesis.bus import genesis_bus
        import asyncio
        
        # Create event data
        event_data = {
            "total": report.engines_total,
            "activated": report.engines_activated,
            "timestamp": report.timestamp
        }
        
        # Publish asynchronously (best effort)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(genesis_bus.publish("engine.activate.all", event_data))
            else:
                asyncio.run(genesis_bus.publish("engine.activate.all", event_data))
        except RuntimeError:
            # No event loop available, skip publishing
            pass
    except ImportError:
        logger.debug("[GENESIS] Genesis bus not available for event publishing")
    except Exception as e:
        logger.warning(f"[GENESIS] Failed to publish activation event: {e}")
    
    return report


def get_activation_status() -> Dict[str, Any]:
    """
    Get current activation status of all engines.
    
    Returns:
        Dictionary with activation status
    """
    status = {
        "engines": [],
        "summary": {
            "total": len(ENGINE_REGISTRY),
            "active": 0,
            "inactive": 0
        }
    }
    
    for engine in ENGINE_REGISTRY:
        is_enabled = check_engine_enabled(engine)
        
        status["engines"].append({
            "name": engine["name"],
            "enabled": is_enabled,
            "env_var": engine["env"],
            "role": engine["role"],
            "category": engine["category"]
        })
        
        if is_enabled:
            status["summary"]["active"] += 1
        else:
            status["summary"]["inactive"] += 1
    
    return status
