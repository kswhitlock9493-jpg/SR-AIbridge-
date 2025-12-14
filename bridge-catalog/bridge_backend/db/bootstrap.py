"""
Database Bootstrap Module for SR-AIbridge v1.9.7s-SOVEREIGN

Auto-creates database schemas if missing on startup.
Ensures seamless deployment without manual migration steps.
Includes Forge Dominion root key validation and generation.
"""
import os
import logging
from pathlib import Path

# Import secret forge for sovereign secret retrieval
try:
    from bridge_backend.bridge_core.token_forge_dominion.secret_forge import retrieve_environment
except ImportError:
    # Fallback if module not available
    def retrieve_environment(key: str, default=None):
        return os.getenv(key, default)

logger = logging.getLogger(__name__)


async def auto_sync_schema():
    """
    Auto-synchronize database schema.
    Creates all tables if they don't exist.
    Safe to call on every startup - only creates missing tables.
    """
    try:
        from bridge_backend.utils.db import engine
        from bridge_backend.models import Base as ModelsBase

        async with engine.begin() as conn:
            await conn.run_sync(ModelsBase.metadata.create_all)

        logger.info("[DB Bootstrap] ✅ Schema auto-sync complete")
        return True
    except Exception as e:
        logger.warning(f"[DB Bootstrap] ⚠️ Schema sync failed (non-fatal): {e}")
        return False


def validate_forge_dominion_root():
    """
    Validate or generate FORGE_DOMINION_ROOT key.
    
    This function ensures that the sovereign cryptographic root key exists.
    If not found in environment, generates and saves to state file for local development.
    
    Returns:
        bool: True if root key is valid or generated
    """
    try:
        from bridge_backend.bridge_core.token_forge_dominion import generate_root_key
        
        # Use forge to retrieve environment variable
        root_key = retrieve_environment("FORGE_DOMINION_ROOT")
        
        if root_key:
            logger.info("[Forge Dominion] ✅ Root key found in environment")
            return True
        
        # For local development, generate and save to state file
        logger.info("[Forge Dominion] 🔑 Generating sovereign root key for local development")
        
        new_key = generate_root_key()
        
        # Save to .alik/forge_state.json for persistence
        state_dir = Path(".alik")
        state_dir.mkdir(exist_ok=True)
        
        state_file = state_dir / "forge_state.json"
        
        import json
        from datetime import datetime
        
        state = {}
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
        
        state["local_root_key"] = new_key
        state["generated_at"] = datetime.utcnow().isoformat() + "Z"
        state["mode"] = "local_development"
        state["resonance_score"] = 75.0
        state["health_status"] = "normal"
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"[Forge Dominion] 💾 Root key saved to {state_file}")
        logger.warning("[Forge Dominion] ⚠️  For production, set FORGE_DOMINION_ROOT environment variable")
        
        # Set in current environment for this session
        os.environ["FORGE_DOMINION_ROOT"] = new_key
        
        return True
        
    except Exception as e:
        logger.error(f"[Forge Dominion] ❌ Root key validation failed: {e}")
        return False
