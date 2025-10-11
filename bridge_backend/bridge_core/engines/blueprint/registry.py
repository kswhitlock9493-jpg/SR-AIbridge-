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
            },
            "leviathan": {
                "name": "Leviathan Solver",
                "description": "Unified solver engine integrating all super engines for complex problem decomposition",
                "schema": {
                    "solver": {
                        "purpose": "Decompose complex queries into sub-tasks",
                        "inputs": ["query", "intents"],
                        "outputs": ["proof_artifact", "sub_tasks", "requirements"]
                    },
                    "super_engines": {
                        "purpose": "Coordinate CalculusCore, QHelmSingularity, AuroraForge, ChronicleLoom, ScrollTongue, CommerceForge",
                        "outputs": ["integrated_solution", "engine_results"]
                    }
                },
                "topics": ["solver.tasks", "solver.results"],
                "dependencies": ["truth", "parser", "autonomy"]
            },
            "auroraforge": {
                "name": "AuroraForge",
                "description": "Visual and creative content generation engine",
                "schema": {
                    "visual_synthesis": {
                        "purpose": "Generate visual assets and creative content",
                        "inputs": ["visual_type", "style_type", "specifications"],
                        "outputs": ["visual_assets", "render_metadata"]
                    },
                    "creative_processing": {
                        "purpose": "Process and enhance creative content",
                        "outputs": ["enhanced_assets", "quality_metrics"]
                    }
                },
                "topics": ["creative.assets", "creative.render"],
                "dependencies": []
            },
            "calculuscore": {
                "name": "CalculusCore",
                "description": "Advanced mathematical and calculus computation engine",
                "schema": {
                    "differentiation": {
                        "purpose": "Compute symbolic derivatives",
                        "inputs": ["equation", "variable", "order"],
                        "outputs": ["derivative", "evaluation"]
                    },
                    "integration": {
                        "purpose": "Compute symbolic integrals",
                        "inputs": ["equation", "variable", "bounds"],
                        "outputs": ["integral", "evaluation"]
                    },
                    "analysis": {
                        "purpose": "Perform limit, series, and optimization analysis",
                        "outputs": ["limits", "series", "extrema"]
                    }
                },
                "topics": ["math.calculus", "math.proofs"],
                "dependencies": []
            },
            "scrolltongue": {
                "name": "ScrollTongue",
                "description": "Natural language processing and linguistic analysis engine",
                "schema": {
                    "linguistic_analysis": {
                        "purpose": "Analyze text for linguistic patterns",
                        "inputs": ["text", "language_type", "analysis_type"],
                        "outputs": ["analysis_results", "complexity_score"]
                    },
                    "translation": {
                        "purpose": "Translate between language types",
                        "outputs": ["translated_text", "confidence"]
                    }
                },
                "topics": ["language.analysis", "language.translation"],
                "dependencies": []
            },
            "commerceforge": {
                "name": "CommerceForge",
                "description": "Economic modeling and trade analysis engine",
                "schema": {
                    "market_simulation": {
                        "purpose": "Simulate market conditions and trading",
                        "inputs": ["market_type", "assets", "parameters"],
                        "outputs": ["market_state", "trade_results"]
                    },
                    "economic_analysis": {
                        "purpose": "Analyze economic trends and opportunities",
                        "outputs": ["insights", "recommendations"]
                    }
                },
                "topics": ["commerce.markets", "commerce.trades"],
                "dependencies": []
            },
            "chronicleloom": {
                "name": "ChronicleLoom",
                "description": "Temporal narrative weaving and chronicle management engine",
                "schema": {
                    "narrative_weaving": {
                        "purpose": "Weave chronicles into temporal narratives",
                        "inputs": ["chronicle_ids", "thread_title", "narrative_type"],
                        "outputs": ["narrative_thread", "connections"]
                    },
                    "pattern_detection": {
                        "purpose": "Identify recurring patterns in chronicles",
                        "outputs": ["patterns", "insights"]
                    }
                },
                "topics": ["chronicle.narratives", "chronicle.patterns"],
                "dependencies": []
            },
            "qhelmsingularity": {
                "name": "QHelmSingularity",
                "description": "Quantum navigation and spacetime physics engine",
                "schema": {
                    "quantum_navigation": {
                        "purpose": "Navigate quantum states and spacetime",
                        "inputs": ["navigation_mode", "target_state"],
                        "outputs": ["navigation_path", "probability"]
                    },
                    "singularity_analysis": {
                        "purpose": "Analyze spacetime singularities",
                        "outputs": ["singularity_data", "stability_metrics"]
                    }
                },
                "topics": ["quantum.navigation", "quantum.singularities"],
                "dependencies": []
            },
            "creativity": {
                "name": "Creativity Bay",
                "description": "Creative asset ingestion and management engine",
                "schema": {
                    "asset_ingestion": {
                        "purpose": "Ingest and catalog creative assets",
                        "inputs": ["title", "text", "tags", "source"],
                        "outputs": ["creative_asset", "sha_hash"]
                    },
                    "asset_retrieval": {
                        "purpose": "Search and retrieve creative assets",
                        "outputs": ["assets", "metadata"]
                    }
                },
                "topics": ["creativity.ingest", "creativity.assets"],
                "dependencies": []
            },
            "indoctrination": {
                "name": "Indoctrination Engine",
                "description": "Agent onboarding, certification, and doctrine management",
                "schema": {
                    "onboarding": {
                        "purpose": "Onboard new agents with roles and specialties",
                        "inputs": ["name", "role", "specialties"],
                        "outputs": ["agent_record", "agent_id"]
                    },
                    "certification": {
                        "purpose": "Certify agents with doctrines",
                        "inputs": ["agent_id", "doctrine"],
                        "outputs": ["certificate", "status"]
                    }
                },
                "topics": ["agents.onboard", "agents.certify"],
                "dependencies": []
            },
            "screen": {
                "name": "Screen Engine",
                "description": "Screen sharing and collaborative session management",
                "schema": {
                    "session_management": {
                        "purpose": "Create and manage screen sharing sessions",
                        "inputs": ["mode", "project", "captain", "permissions"],
                        "outputs": ["session", "session_id"]
                    },
                    "signaling": {
                        "purpose": "Handle WebRTC signaling for screen sharing",
                        "outputs": ["signals", "connection_state"]
                    }
                },
                "topics": ["screen.sessions", "screen.signaling"],
                "dependencies": []
            },
            "speech": {
                "name": "Speech Engine",
                "description": "Text-to-speech and speech-to-text processing",
                "schema": {
                    "tts": {
                        "purpose": "Convert text to speech audio",
                        "inputs": ["text", "voice"],
                        "outputs": ["audio_file", "audio_metadata"]
                    },
                    "stt": {
                        "purpose": "Convert speech audio to text",
                        "inputs": ["audio_file"],
                        "outputs": ["transcription", "confidence"]
                    }
                },
                "topics": ["speech.tts", "speech.stt"],
                "dependencies": []
            },
            "recovery": {
                "name": "Recovery Orchestrator",
                "description": "Recovery coordination between autonomy and parser engines",
                "schema": {
                    "orchestration": {
                        "purpose": "Dispatch tasks and ingest content simultaneously",
                        "inputs": ["project", "captain", "objective", "raw_text"],
                        "outputs": ["task", "manifest", "linkage"]
                    }
                },
                "topics": ["recovery.tasks", "recovery.linkage"],
                "dependencies": ["autonomy", "parser"]
            },
            "agents_foundry": {
                "name": "Agents Foundry",
                "description": "Agent creation and archetype management engine",
                "schema": {
                    "agent_creation": {
                        "purpose": "Create agents with archetypes and constitutions",
                        "inputs": ["name", "archetype", "roles", "permissions"],
                        "outputs": ["agent", "agent_id", "constitution"]
                    },
                    "archetype_management": {
                        "purpose": "Manage starter archetypes (Jarvis, Poe, Aeon)",
                        "outputs": ["archetypes", "system_prompts"]
                    }
                },
                "topics": ["agents.create", "agents.archetypes"],
                "dependencies": []
            },
            "filing": {
                "name": "Filing Engine",
                "description": "File management and organization engine",
                "schema": {
                    "file_operations": {
                        "purpose": "Manage file storage and retrieval",
                        "inputs": ["operation", "file_path", "content"],
                        "outputs": ["result", "file_metadata"]
                    }
                },
                "topics": ["files.operations"],
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
