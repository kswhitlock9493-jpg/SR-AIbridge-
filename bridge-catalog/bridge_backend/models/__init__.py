from .core import Base, User  # re-export
__all__ = ["Base", "User"]

# Re-export models from top-level models.py if available
# Use late binding to avoid circular imports at module load time
def __getattr__(name):
    """Lazy import for models to avoid circular imports"""
    if name in ("Blueprint", "AgentJob", "Mission", "Agent", "Guardian", "VaultLog"):
        try:
            # Import directly from the models.py module, not bridge_backend.models package
            import importlib.util
            import os
            models_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models.py")
            spec = importlib.util.spec_from_file_location("_bridge_models", models_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return getattr(module, name)
        except (ImportError, AttributeError, FileNotFoundError):
            pass
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


