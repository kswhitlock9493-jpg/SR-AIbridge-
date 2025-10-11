"""
Genesis Manifest System
Unified engine manifest aggregating all engine schemas and relationships
"""

from typing import Dict, Any, List, Optional
import logging
import os

logger = logging.getLogger(__name__)


class GenesisManifest:
    """
    Universal manifest aggregating all engine schemas and API surfaces.
    Acts as DNA of the Bridge - the canonical source of truth for the entire organism.
    """
    
    def __init__(self):
        self._manifest: Dict[str, Any] = {}
        self._engine_registry: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
        
        logger.info("🧬 Genesis Manifest initialized")
    
    def register_engine(self, engine_name: str, schema: Dict[str, Any]):
        """
        Register an engine with the Genesis manifest
        
        Args:
            engine_name: Name of the engine
            schema: Engine schema definition including API surface, topics, and dependencies
        """
        self._engine_registry[engine_name] = {
            "name": engine_name,
            "schema": schema,
            "registered_at": self._get_timestamp(),
            "genesis_role": schema.get("genesis_role", "Unknown"),
        }
        
        logger.info(f"✅ Registered engine: {engine_name} (role: {schema.get('genesis_role', 'Unknown')})")
        self._rebuild_manifest()
    
    def _rebuild_manifest(self):
        """Rebuild the unified manifest from all registered engines"""
        self._manifest = {
            "genesis_version": "2.0.0",
            "engines": self._engine_registry.copy(),
            "total_engines": len(self._engine_registry),
            "last_updated": self._get_timestamp(),
        }
        self._initialized = True
    
    def get_manifest(self) -> Dict[str, Any]:
        """Get the complete unified manifest"""
        return self._manifest.copy()
    
    def get_engine(self, engine_name: str) -> Optional[Dict[str, Any]]:
        """Get schema for a specific engine"""
        return self._engine_registry.get(engine_name)
    
    def get_engine_role(self, engine_name: str) -> Optional[str]:
        """Get Genesis role for a specific engine"""
        engine = self.get_engine(engine_name)
        return engine["genesis_role"] if engine else None
    
    def list_engines(self) -> List[str]:
        """List all registered engine names"""
        return list(self._engine_registry.keys())
    
    def get_dependencies(self, engine_name: str) -> List[str]:
        """Get dependencies for a specific engine"""
        engine = self.get_engine(engine_name)
        if engine:
            return engine.get("schema", {}).get("dependencies", [])
        return []
    
    def get_topics(self, engine_name: str) -> List[str]:
        """Get event topics for a specific engine"""
        engine = self.get_engine(engine_name)
        if engine:
            return engine.get("schema", {}).get("topics", [])
        return []
    
    def validate_integrity(self) -> Dict[str, Any]:
        """
        Validate manifest integrity and engine relationships
        
        Returns:
            Validation report with any errors or warnings
        """
        errors = []
        warnings = []
        
        # Check for circular dependencies
        for engine_name in self._engine_registry.keys():
            deps = self.get_dependencies(engine_name)
            for dep in deps:
                if dep not in self._engine_registry:
                    errors.append(f"Engine '{engine_name}' depends on missing engine '{dep}'")
                elif engine_name in self.get_dependencies(dep):
                    warnings.append(f"Potential circular dependency between '{engine_name}' and '{dep}'")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "engine_count": len(self._engine_registry),
            "initialized": self._initialized,
        }
    
    def sync_from_blueprint_registry(self):
        """
        Synchronize Genesis manifest with existing Blueprint registry
        Provides backward compatibility with v1.9.7c linkage
        """
        try:
            from bridge_backend.bridge_core.engines.blueprint.registry import BlueprintRegistry
            
            blueprint_manifest = BlueprintRegistry.load_all()
            
            # Map Blueprint engines to Genesis roles
            genesis_role_map = {
                "blueprint": "DNA of the Bridge - defines structure and schema",
                "tde_x": "Heart - pulse of operations (deploy & environment)",
                "cascade": "Nervous system - manages post-deploy flows",
                "truth": "Immune system - certifies facts & integrity",
                "autonomy": "Reflex arc - self-healing & optimization",
                "leviathan": "Cerebral cortex - distributed inference",
                "creativity": "Imagination - generative logic & UX narrative",
                "parser": "Language center - communication interface",
                "speech": "Language center - communication interface",
                "fleet": "Operational limbs - agent management",
                "custody": "Operational limbs - storage management",
                "console": "Operational limbs - command routing",
                "captains": "Immune guardians - policy layer",
                "guardians": "Immune guardians - protection layer",
                "recovery": "Repair mechanism - system restoration",
            }
            
            for engine_name, engine_data in blueprint_manifest.items():
                schema = {
                    **engine_data,
                    "genesis_role": genesis_role_map.get(engine_name, "Supporting component"),
                }
                self.register_engine(engine_name, schema)
            
            logger.info(f"✅ Synced {len(blueprint_manifest)} engines from Blueprint Registry")
            
        except ImportError:
            logger.warning("⚠️ Blueprint Registry not available for sync")
        except Exception as e:
            logger.error(f"❌ Failed to sync from Blueprint Registry: {e}")
    
    def _get_timestamp(self) -> str:
        """Get ISO timestamp"""
        from datetime import datetime, UTC
        return datetime.now(UTC).isoformat().replace('+00:00', 'Z')


# Global singleton manifest instance
genesis_manifest = GenesisManifest()
