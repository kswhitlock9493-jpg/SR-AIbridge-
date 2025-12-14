"""
Forge Core - GitHub Repository-Based Engine Integration
v1.9.7f - Cascade Synchrony: Universal Healing Protocol

The Forge introspects the repository structure and integrates engines
directly from the codebase without needing external API or webhook dependencies.
"""

import os
import json
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Path to the bridge forge registry
BRIDGE_FORGE_REGISTRY = Path(".github/bridge_forge.json")


def certify(operation: str, data: Dict[str, Any]) -> None:
    """
    Interface to Truth certification system.
    Certifies Forge operations for RBAC compliance.
    """
    try:
        # Import Truth certification if available
        from bridge_backend.bridge_core.engines.truth.utils import certify as truth_certify
        truth_certify(operation, data)
    except ImportError:
        logger.debug(f"[Forge] Truth certification not available, logging operation: {operation}")
        logger.info(f"[Forge] Operation certified: {operation} - {data}")


def load_forge_registry() -> Dict[str, str]:
    """
    Load the bridge forge registry from .github/bridge_forge.json
    
    Returns:
        Dictionary mapping engine names to their file paths
    """
    registry_path = Path(BRIDGE_FORGE_REGISTRY)
    
    if not registry_path.exists():
        logger.warning(f"[Forge] Registry not found at {registry_path}, returning empty registry")
        return {}
    
    try:
        with open(registry_path, "r") as f:
            forge_map = json.load(f)
            logger.info(f"[Forge] Loaded registry with {len(forge_map)} engine mappings")
            return forge_map
    except Exception as e:
        logger.error(f"[Forge] Failed to load registry: {e}")
        return {}


def get_engine_registry() -> List[Dict[str, Any]]:
    """
    Get the list of all registered engines from Genesis activation.
    
    Returns:
        List of engine definitions
    """
    try:
        from bridge_backend.genesis.activation import ENGINE_REGISTRY
        return ENGINE_REGISTRY
    except ImportError:
        logger.warning("[Forge] Could not import ENGINE_REGISTRY from genesis.activation")
        return []


def discover_engine_paths() -> Dict[str, str]:
    """
    Discover engine paths by scanning the bridge_backend directory structure.
    
    Returns:
        Dictionary mapping engine names to discovered paths
    """
    discovered = {}
    base_path = Path("bridge_backend")
    
    # Common engine locations
    engine_locations = [
        base_path / "bridge_core" / "engines",
        base_path / "engines",
    ]
    
    for location in engine_locations:
        if location.exists() and location.is_dir():
            for engine_dir in location.iterdir():
                if engine_dir.is_dir() and (engine_dir / "__init__.py").exists():
                    engine_name = engine_dir.name
                    discovered[engine_name] = str(engine_dir / "__init__.py")
    
    logger.info(f"[Forge] Discovered {len(discovered)} engine paths")
    return discovered


def integrate_engine(engine_name: str, engine_path: str) -> bool:
    """
    Attempt to integrate a single engine by importing its module.
    
    Args:
        engine_name: Name of the engine
        engine_path: Path to the engine's __init__.py
    
    Returns:
        True if integration successful, False otherwise
    """
    try:
        # Convert path to module name
        # e.g., bridge_backend/engines/arie/__init__.py -> bridge_backend.engines.arie
        path_obj = Path(engine_path)
        parts = path_obj.parts
        
        # Find bridge_backend in the path
        if "bridge_backend" in parts:
            idx = parts.index("bridge_backend")
            module_parts = parts[idx:-1]  # Exclude __init__.py
            module_name = ".".join(module_parts)
            
            # Try to import the module
            importlib.import_module(module_name)
            logger.info(f"[Forge] ✅ Successfully integrated engine: {engine_name}")
            return True
        else:
            logger.warning(f"[Forge] Invalid path structure for {engine_name}: {engine_path}")
            return False
            
    except Exception as e:
        logger.debug(f"[Forge] Failed to integrate {engine_name}: {e}")
        return False


def forge_integrate_engines() -> Dict[str, Any]:
    """
    Forge introspection: scans repo & activates engines directly from the repository.
    
    This is the main entry point for the Forge system. It:
    1. Loads the bridge_forge.json registry
    2. Discovers additional engines from the directory structure
    3. Attempts to integrate each engine
    4. Certifies the integration with Truth
    
    Returns:
        Dictionary with integration results
    """
    logger.info("🔥 [Forge] Starting Cascade Synchrony engine integration")
    
    # Check if Forge mode is enabled
    forge_mode = os.getenv("FORGE_MODE", "disabled").lower()
    if forge_mode != "enabled":
        logger.info("[Forge] Forge mode not enabled, skipping integration")
        return {
            "forge_mode": "disabled",
            "engines_integrated": [],
            "message": "Set FORGE_MODE=enabled to activate"
        }
    
    # Load the forge registry
    forge_map = load_forge_registry()
    
    # Discover engines from directory structure
    discovered_paths = discover_engine_paths()
    
    # Merge forge registry with discovered paths (registry takes precedence)
    all_engines = {**discovered_paths, **forge_map}
    
    # Get engine registry to cross-reference
    engine_registry = get_engine_registry()
    registry_names = {e.get("name", "").lower(): e for e in engine_registry}
    
    integrated = []
    failed = []
    
    for engine_name, engine_path in all_engines.items():
        # Check if path exists
        if not os.path.exists(engine_path):
            logger.warning(f"[Forge] Engine path does not exist: {engine_name} -> {engine_path}")
            failed.append({"name": engine_name, "reason": "path_not_found"})
            continue
        
        # Try to integrate
        if integrate_engine(engine_name, engine_path):
            integrated.append(engine_name)
        else:
            failed.append({"name": engine_name, "reason": "import_failed"})
    
    # Certify the integration with Truth
    result = {
        "forge_mode": forge_mode,
        "engines_discovered": len(all_engines),
        "engines_integrated": integrated,
        "engines_failed": failed,
        "integration_count": len(integrated),
        "failure_count": len(failed),
    }
    
    certify("forge.integration", result)
    
    logger.info(f"🔥 [Forge] Integration complete: {len(integrated)} engines integrated, {len(failed)} failed")
    
    return result


def get_forge_status() -> Dict[str, Any]:
    """
    Get current status of the Forge system.
    
    Returns:
        Dictionary with Forge status information
    """
    return {
        "forge_mode": os.getenv("FORGE_MODE", "disabled"),
        "forge_self_heal": os.getenv("FORGE_SELF_HEAL", "false"),
        "cascade_sync": os.getenv("CASCADE_SYNC", "false"),
        "arie_propagation": os.getenv("ARIE_PROPAGATION", "false"),
        "umbra_memory_sync": os.getenv("UMBRA_MEMORY_SYNC", "false"),
        "truth_certification": os.getenv("TRUTH_CERTIFICATION", "true"),
        "registry_exists": BRIDGE_FORGE_REGISTRY.exists(),
    }
