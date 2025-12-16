# brh/chaos.py
"""
Chaos Injector Module
Simulates random container failures to validate failover and recovery mechanisms.
"""
import os
import random
import threading
import time

try:
    import docker
    DOCKER_AVAILABLE = True
    client = docker.from_env()
except ImportError:
    DOCKER_AVAILABLE = False
    client = None

INTERVAL = int(os.getenv("BRH_CHAOS_INTERVAL", "600"))  # every 10 min
KILL_PROB = float(os.getenv("BRH_KILL_PROB", "0.15"))   # 15% chance
TARGET_LABEL = "brh.service"


def chaos_loop():
    """
    Continuous chaos injection loop.
    Periodically kills random containers to test resilience.
    """
    if not DOCKER_AVAILABLE:
        print("[CHAOS] Docker SDK not available, chaos disabled")
        return
    
    while True:
        time.sleep(INTERVAL)
        if random.random() > KILL_PROB:
            continue
        try:
            containers = client.containers.list()
            if not containers:
                continue
            target = random.choice(containers)
            print(f"[CHAOS] 💣 Simulating failure in {target.name}")
            target.kill()
            
            # Log event
            try:
                from brh.api import log_event
                log_event(f"CHAOS: killed container {target.name}")
            except Exception:
                pass  # Event logging not required for chaos operation
        except Exception as e:
            print(f"[CHAOS] Error: {e}")


def start():
    """
    Start chaos injector daemon.
    Runs in background thread if enabled via environment variables.
    """
    enabled = os.getenv("BRH_CHAOS_ENABLED", "false").lower() == "true"
    if not enabled:
        print("[CHAOS] Chaos injector disabled")
        return
    
    if not DOCKER_AVAILABLE:
        print("[CHAOS] Docker SDK not available, chaos disabled")
        return
    
    print(f"[CHAOS] Starting chaos injector (interval={INTERVAL}s, probability={KILL_PROB})")
    threading.Thread(target=chaos_loop, daemon=True).start()
    print("[CHAOS] Chaos injector started")
