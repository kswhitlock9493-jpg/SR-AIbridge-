"""
HXO Parser Link Adapter
Translates human/CLI specs into formal HXO plans
"""

import logging
from typing import Dict, Any, List, Optional
import uuid

logger = logging.getLogger(__name__)


async def parse_plan_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse a high-level plan specification into a formal HXO plan.
    
    Args:
        spec: High-level specification
            - name: Plan name
            - intent: High-level description
            - stages: List of stage specifications (can be minimal)
            - constraints: Optional constraints
            
    Returns:
        Formal HXO plan data
    """
    try:
        # Generate plan ID if not provided
        plan_id = spec.get("plan_id", str(uuid.uuid4()))
        
        # Parse stages
        stages = []
        for stage_spec in spec.get("stages", []):
            stage = await _parse_stage_spec(stage_spec)
            stages.append(stage)
        
        # Apply default constraints
        constraints = spec.get("constraints", {})
        if "max_shards" not in constraints:
            constraints["max_shards"] = 1000000
        if "timebox_ms" not in constraints:
            constraints["timebox_ms"] = 600000  # 10 minutes
        
        # Create formal plan
        plan_data = {
            "plan_id": plan_id,
            "name": spec.get("name", "untitled_plan"),
            "stages": stages,
            "constraints": constraints,
            "submitted_by": spec.get("submitted_by", "parser")
        }
        
        logger.info(f"[HXO Parser Link] Parsed plan '{plan_data['name']}' with {len(stages)} stages")
        return plan_data
        
    except Exception as e:
        logger.error(f"[HXO Parser Link] Failed to parse plan spec: {e}")
        raise


async def _parse_stage_spec(stage_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse a stage specification into formal stage data.
    
    Args:
        stage_spec: Stage specification
            
    Returns:
        Formal stage data
    """
    # Required fields
    stage_id = stage_spec.get("id")
    if not stage_id:
        raise ValueError("Stage 'id' is required")
    
    kind = stage_spec.get("kind")
    if not kind:
        raise ValueError("Stage 'kind' is required")
    
    # Infer defaults based on kind
    defaults = _get_stage_defaults(kind)
    
    # Build stage data with defaults
    stage = {
        "id": stage_id,
        "kind": kind,
        "slo_ms": stage_spec.get("slo_ms", defaults.get("slo_ms", 120000)),
        "partitioner": stage_spec.get("partitioner", defaults.get("partitioner")),
        "executor": stage_spec.get("executor", defaults.get("executor")),
        "scheduler": stage_spec.get("scheduler", defaults.get("scheduler", "fair_round_robin")),
        "dependencies": stage_spec.get("dependencies", []),
        "config": stage_spec.get("config", {})
    }
    
    return stage


def _get_stage_defaults(kind: str) -> Dict[str, Any]:
    """
    Get default values for a stage based on its kind.
    
    Args:
        kind: Job kind
        
    Returns:
        Default values
    """
    defaults_map = {
        "deploy.pack": {
            "slo_ms": 120000,
            "partitioner": "by_filesize",
            "executor": "pack_backend"
        },
        "deploy.migrate": {
            "slo_ms": 30000,
            "partitioner": "by_sql_batch",
            "executor": "sql_migrate"
        },
        "deploy.prime": {
            "slo_ms": 45000,
            "partitioner": "by_module",
            "executor": "warm_registry"
        },
        "assets.index": {
            "slo_ms": 60000,
            "partitioner": "by_asset_bucket",
            "executor": "index_assets"
        },
        "assets.stage": {
            "slo_ms": 60000,
            "partitioner": "by_asset_bucket",
            "executor": "index_assets"
        },
        "docs.index": {
            "slo_ms": 30000,
            "partitioner": "by_route_map",
            "executor": "docs_index"
        }
    }
    
    return defaults_map.get(kind, {
        "slo_ms": 120000,
        "partitioner": "by_filesize",
        "executor": "pack_backend"
    })


async def parse_cli_command(command: str) -> Dict[str, Any]:
    """
    Parse a CLI command string into a plan specification.
    
    Args:
        command: CLI command (e.g., "hxo deploy --stages pack,migrate,prime")
        
    Returns:
        Plan specification
    """
    try:
        # Very simple parsing - in a real implementation, this would use argparse
        # or a proper CLI parser
        
        parts = command.split()
        if len(parts) < 2:
            raise ValueError("Invalid command format")
        
        # Extract plan name
        plan_name = parts[1] if len(parts) > 1 else "cli_plan"
        
        # Look for --stages flag
        stages = []
        if "--stages" in parts:
            idx = parts.index("--stages")
            if idx + 1 < len(parts):
                stage_names = parts[idx + 1].split(",")
                for stage_name in stage_names:
                    # Map stage name to kind
                    kind = _map_stage_name_to_kind(stage_name)
                    stages.append({
                        "id": stage_name,
                        "kind": kind
                    })
        
        spec = {
            "name": plan_name,
            "stages": stages
        }
        
        logger.info(f"[HXO Parser Link] Parsed CLI command to plan '{plan_name}' with {len(stages)} stages")
        return spec
        
    except Exception as e:
        logger.error(f"[HXO Parser Link] Failed to parse CLI command: {e}")
        raise


def _map_stage_name_to_kind(stage_name: str) -> str:
    """
    Map a short stage name to a full job kind.
    
    Args:
        stage_name: Short name (e.g., "pack", "migrate")
        
    Returns:
        Job kind (e.g., "deploy.pack", "deploy.migrate")
    """
    mapping = {
        "pack": "deploy.pack",
        "migrate": "deploy.migrate",
        "prime": "deploy.prime",
        "index": "assets.index",
        "stage": "assets.stage",
        "docs": "docs.index"
    }
    
    return mapping.get(stage_name, f"deploy.{stage_name}")
