"""
Port Guard — Environment PORT visibility for deploy diagnostics
"""
import os


def describe_port_env():
    """Log PORT environment state for troubleshooting"""
    target = os.environ.get("PORT")
    print(f"INFO:bridge_backend.main:[BOOT] Target PORT={target or '∅'} (Render sets this automatically)")
