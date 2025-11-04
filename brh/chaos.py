# brh/chaos.py
"""
Chaos Injector Module
Simulates random container failures to validate failover and recovery mechanisms.
"""
import os
import random
import threading
import time
import subprocess

INTERVAL = int(os.getenv("BRH_CHAOS_INTERVAL", "600"))  # every 10 min
KILL_PROB = float(os.getenv("BRH_KILL_PROB", "0.15"))   # 15% chance
TARGET_LABEL = "brh.service"


def chaos_loop():
    """
    Continuous chaos injection loop.
    Periodically kills random containers to test resilience.
    """
    while True:
        time.sleep(INTERVAL)
        if random.random() > KILL_PROB:
            continue
        try:
            out = subprocess.check_output(
                ["docker", "ps", "--format", "{{.Names}}"], text=True
            ).strip().splitlines()
            if not out:
                continue
            target = random.choice(out)
            print(f"[CHAOS] 💣 Simulating failure in {target}")
            subprocess.call(["docker", "kill", target])
            
            # Log event
            try:
                from brh.api import log_event
                log_event(f"CHAOS: killed container {target}")
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
    
    print(f"[CHAOS] Starting chaos injector (interval={INTERVAL}s, probability={KILL_PROB})")
    threading.Thread(target=chaos_loop, daemon=True).start()
    print("[CHAOS] Chaos injector started")
