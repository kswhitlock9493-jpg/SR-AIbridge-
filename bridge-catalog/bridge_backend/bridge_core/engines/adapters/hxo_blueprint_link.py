"""
HXO Blueprint Link Adapter
Validates HXO job types against Blueprint schema contracts
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


# Define HXO job kinds and their schemas
HXO_JOB_KINDS = {
    "deploy.pack": {
        "description": "Pack backend files for deployment",
        "partitioners": ["by_filesize", "by_module"],
        "executors": ["pack_backend"],
        "safety_policy": {
            "allow_non_idempotent": False,
            "require_dry_run": False
        }
    },
    "deploy.migrate": {
        "description": "Execute database migrations",
        "partitioners": ["by_sql_batch"],
        "executors": ["sql_migrate"],
        "safety_policy": {
            "allow_non_idempotent": True,  # Migrations need special handling
            "require_dry_run": True
        }
    },
    "deploy.prime": {
        "description": "Prime registry and caches",
        "partitioners": ["by_module", "by_dag_depth"],
        "executors": ["warm_registry", "prime_caches"],
        "safety_policy": {
            "allow_non_idempotent": False,
            "require_dry_run": False
        }
    },
    "assets.index": {
        "description": "Index assets for search",
        "partitioners": ["by_asset_bucket", "by_filesize"],
        "executors": ["index_assets"],
        "safety_policy": {
            "allow_non_idempotent": False,
            "require_dry_run": False
        }
    },
    "assets.stage": {
        "description": "Stage assets for deployment",
        "partitioners": ["by_asset_bucket", "by_filesize"],
        "executors": ["index_assets"],
        "safety_policy": {
            "allow_non_idempotent": False,
            "require_dry_run": False
        }
    },
    "docs.index": {
        "description": "Index documentation for search",
        "partitioners": ["by_route_map"],
        "executors": ["docs_index"],
        "safety_policy": {
            "allow_non_idempotent": False,
            "require_dry_run": False
        }
    }
}


def get_job_kind_schema(kind: str) -> Optional[Dict[str, Any]]:
    """
    Get Blueprint schema for a job kind.
    
    Args:
        kind: Job kind (e.g., "deploy.pack")
        
    Returns:
        Schema dictionary or None if not found
    """
    return HXO_JOB_KINDS.get(kind)


def validate_stage(stage_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate a stage against Blueprint schema.
    
    Args:
        stage_data: Stage configuration
        
    Returns:
        (is_valid, error_message)
    """
    try:
        kind = stage_data.get("kind")
        if not kind:
            return False, "Stage kind is required"
        
        schema = get_job_kind_schema(kind)
        if not schema:
            return False, f"Unknown job kind: {kind}"
        
        # Validate partitioner
        partitioner = stage_data.get("partitioner")
        if partitioner:
            allowed_partitioners = schema.get("partitioners", [])
            if partitioner not in allowed_partitioners:
                return False, f"Partitioner '{partitioner}' not allowed for job kind '{kind}'"
        
        # Validate executor
        executor = stage_data.get("executor")
        if executor:
            allowed_executors = schema.get("executors", [])
            if executor not in allowed_executors:
                return False, f"Executor '{executor}' not allowed for job kind '{kind}'"
        
        # Validate safety policy
        safety = schema.get("safety_policy", {})
        if not safety.get("allow_non_idempotent", False):
            # Ensure stage is idempotent
            if stage_data.get("non_idempotent", False):
                return False, f"Non-idempotent operations not allowed for job kind '{kind}'"
        
        return True, None
        
    except Exception as e:
        logger.error(f"[HXO Blueprint Link] Validation error: {e}")
        return False, str(e)


async def register_hxo_job_kinds():
    """
    Register HXO job kinds with Blueprint registry.
    """
    try:
        from bridge_backend.genesis.bus import genesis_bus
        
        if not genesis_bus.is_enabled():
            logger.debug("[HXO Blueprint Link] Genesis bus disabled")
            return
        
        # Publish job kind schemas
        await genesis_bus.publish("blueprint.events", {
            "type": "hxo.job_kinds.registered",
            "job_kinds": list(HXO_JOB_KINDS.keys()),
            "schemas": HXO_JOB_KINDS
        })
        
        logger.info(f"[HXO Blueprint Link] Registered {len(HXO_JOB_KINDS)} job kinds")
        
    except ImportError:
        logger.debug("[HXO Blueprint Link] Genesis bus not available")
    except Exception as e:
        logger.error(f"[HXO Blueprint Link] Failed to register job kinds: {e}")


async def validate_plan(plan_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate an entire HXO plan against Blueprint schemas.
    
    Args:
        plan_data: Plan configuration
        
    Returns:
        (is_valid, error_message)
    """
    try:
        stages = plan_data.get("stages", [])
        if not stages:
            return False, "Plan must have at least one stage"
        
        # Validate each stage
        for i, stage in enumerate(stages):
            is_valid, error = validate_stage(stage)
            if not is_valid:
                return False, f"Stage {i} ({stage.get('id', 'unknown')}): {error}"
        
        return True, None
        
    except Exception as e:
        logger.error(f"[HXO Blueprint Link] Plan validation error: {e}")
        return False, str(e)
