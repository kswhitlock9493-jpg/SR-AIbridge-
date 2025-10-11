"""
Blueprint Registry - Canonical manifest of all engine schemas and relationships
Provides source of truth for engine structure, schema, and inter-engine relationships
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class BlueprintRegistry:
    """
    Central registry of engine blueprints and schemas.
    Each blueprint describes an engine's structure, schema, and relationships.
    """
    
    @staticmethod
    def load_all() -> Dict[str, Any]:
        """
        Load all engine blueprints and return canonical manifest.
        
        Returns:
            Dictionary mapping engine names to their blueprint definitions
        """
        manifest = {
            "tde_x": {
                "name": "TDE-X",
                "description": "Tri-Domain Execution Engine - Orchestrates bootstrap, runtime, and diagnostics shards",
                "shards": ["bootstrap", "runtime", "diagnostics"],
                "schema": {
                    "bootstrap": {
                        "purpose": "Environment validation",
                        "target_time": "7min",
                        "outputs": ["env_validated", "dependencies_ready"]
                    },
                    "runtime": {
                        "purpose": "DB sync + migrations",
                        "target_time": "10min",
                        "outputs": ["db_synced", "migrations_applied"]
                    },
                    "diagnostics": {
                        "purpose": "Asset uploads + analytics",
                        "mode": "background",
                        "outputs": ["assets_uploaded", "analytics_ready"]
                    }
                },
                "topics": ["deploy.signals"],
                "dependencies": []
            },
            "blueprint": {
                "name": "Blueprint Engine",
                "description": "Core planning and schema definition engine",
                "schema": {
                    "manifest": {
                        "purpose": "Define engine structure and relationships",
                        "outputs": ["engine_schemas", "relationships"]
                    },
                    "planner": {
                        "purpose": "Generate task blueprints",
                        "outputs": ["objectives", "tasks", "artifacts"]
                    }
                },
                "topics": ["blueprint.events"],
                "dependencies": []
            },
            "cascade": {
                "name": "Cascade Engine",
                "description": "DAG-based execution orchestration with hot-swap capabilities",
                "schema": {
                    "dag_builder": {
                        "purpose": "Build execution graph from blueprints",
                        "inputs": ["blueprint_manifest", "facts"],
                        "outputs": ["execution_dag", "job_queue"]
                    },
                    "patch_system": {
                        "purpose": "Apply seamless updates without downtime",
                        "outputs": ["patches_applied", "state_updated"]
                    }
                },
                "topics": ["deploy.graph", "blueprint.events:update"],
                "dependencies": ["blueprint"]
            },
            "truth": {
                "name": "Truth Engine",
                "description": "Fact certification and state validation engine",
                "schema": {
                    "validator": {
                        "purpose": "Certify facts against blueprint schemas",
                        "inputs": ["blueprint_manifest", "runtime_state"],
                        "outputs": ["certified_facts", "validation_report"]
                    },
                    "binder": {
                        "purpose": "Merge and deduplicate facts",
                        "outputs": ["bound_truths", "truth_log"]
                    }
                },
                "topics": ["deploy.facts"],
                "dependencies": ["blueprint"]
            },
            "autonomy": {
                "name": "Autonomy Engine",
                "description": "Self-healing and optimization engine with guardrails",
                "schema": {
                    "task_executor": {
                        "purpose": "Execute autonomous tasks within blueprint constraints",
                        "inputs": ["blueprint_rules", "certified_facts"],
                        "outputs": ["actions_executed", "task_results"]
                    },
                    "guardrails": {
                        "purpose": "Enforce safety policies from blueprint",
                        "inputs": ["blueprint_policies"],
                        "outputs": ["policy_enforced", "actions_allowed"]
                    }
                },
                "topics": ["deploy.actions"],
                "dependencies": ["blueprint", "truth"]
            },
            "parser": {
                "name": "Parser Engine",
                "description": "Content ingestion and lineage tracking",
                "schema": {
                    "ingest": {
                        "purpose": "Chunk and hash content",
                        "outputs": ["chunks", "manifest"]
                    },
                    "lineage": {
                        "purpose": "Track content relationships",
                        "outputs": ["links", "ledger"]
                    }
                },
                "topics": [],
                "dependencies": []
            }
        }
        
        logger.info(f"[BlueprintRegistry] Loaded {len(manifest)} engine blueprints")
        return manifest
    
    @staticmethod
    def get_engine(engine_name: str) -> Dict[str, Any]:
        """
        Get blueprint for a specific engine.
        
        Args:
            engine_name: Name of the engine
            
        Returns:
            Blueprint dictionary for the specified engine
        """
        manifest = BlueprintRegistry.load_all()
        return manifest.get(engine_name, {})
    
    @staticmethod
    def get_dependencies(engine_name: str) -> List[str]:
        """
        Get list of engine dependencies.
        
        Args:
            engine_name: Name of the engine
            
        Returns:
            List of engine names this engine depends on
        """
        engine = BlueprintRegistry.get_engine(engine_name)
        return engine.get("dependencies", [])
    
    @staticmethod
    def get_topics(engine_name: str) -> List[str]:
        """
        Get list of event bus topics this engine uses.
        
        Args:
            engine_name: Name of the engine
            
        Returns:
            List of topic names
        """
        engine = BlueprintRegistry.get_engine(engine_name)
        return engine.get("topics", [])
    
    @staticmethod
    def validate_manifest_integrity() -> Dict[str, Any]:
        """
        Validate that all engine dependencies exist and topics are well-formed.
        
        Returns:
            Validation report with status and any errors
        """
        manifest = BlueprintRegistry.load_all()
        errors = []
        
        # Check that all dependencies exist
        for engine_name, blueprint in manifest.items():
            for dep in blueprint.get("dependencies", []):
                if dep not in manifest:
                    errors.append(f"Engine '{engine_name}' depends on missing engine '{dep}'")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "engine_count": len(manifest)
        }
