# brh/recovery.py
"""
Recovery & Watchtower Module
Monitors container health and ensures consistency with leader state.
"""
import time
import threading
from brh import role

try:
    import docker
    DOCKER_AVAILABLE = True
    client = docker.from_env()
except ImportError:
    DOCKER_AVAILABLE = False
    client = None


def recovery_loop():
    """
    Continuous recovery monitoring loop.
    - Leaders restart failed containers
    - Witnesses release stray containers they don't own
    """
    if not DOCKER_AVAILABLE:
        print("[RECOVERY] Docker SDK not available, recovery disabled")
        return
    
    while True:
        try:
            if role.am_leader():
                # leader sanity check - restart stopped containers
                for c in client.containers.list(all=True):
                    if c.status != "running":
                        print(f"[RECOVERY] Restarting {c.name}")
                        try:
                            c.start()
                            # Log event
                            try:
                                from brh.api import log_event
                                log_event(f"RECOVERY: restarted container {c.name}")
                            except Exception:
                                pass
                        except Exception as e:
                            print(f"[RECOVERY] Failed to restart {c.name}: {e}")
            else:
                # witnesses verify they don't own any containers
                for c in client.containers.list(all=True):
                    if c.labels.get("brh.owner") == role.BRH_NODE_ID:
                        print(f"[RECOVERY] Witness releasing stray {c.name}")
                        try:
                            c.update(labels={k: v for k, v in c.labels.items() if k != "brh.owner"})
                            # Log event
                            try:
                                from brh.api import log_event
                                log_event(f"RECOVERY: witness released container {c.name}")
                            except Exception:
                                pass
                        except Exception as e:
                            print(f"[RECOVERY] Failed to release {c.name}: {e}")
        except Exception as e:
            print(f"[RECOVERY] error: {e}")
        time.sleep(120)  # every 2 min


def start():
    """
    Start recovery watchtower daemon.
    Runs in background thread if enabled via environment variables.
    """
    import os
    enabled = os.getenv("BRH_RECOVERY_ENABLED", "true").lower() == "true"
    if not enabled:
        print("[RECOVERY] Recovery watchtower disabled")
        return
    
    if not DOCKER_AVAILABLE:
        print("[RECOVERY] Docker SDK not available, recovery disabled")
        return
    
    print("[RECOVERY] Starting recovery watchtower")
    threading.Thread(target=recovery_loop, daemon=True).start()
    print("[RECOVERY] Recovery watchtower started")
