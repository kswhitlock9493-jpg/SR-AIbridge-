#!/usr/bin/env python3
import asyncio, uvicorn
import os
import subprocess
import time
import yaml
import socket
import requests
from bridge_backend import create_app

def http_health(url):
    try:
        r = requests.get(url, timeout=2)
        return r.status_code == 200
    except Exception:
        return False

def tcp_health(host, port):
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except Exception:
        return False

with open("bridge.runtime.yaml") as f:
    config = yaml.safe_load(f)

services = config["services"]
os.makedirs("logs", exist_ok=True)
procs = {}

def launch_service(name, service):
    parts = service["command"].split()
    env = os.environ.copy()
    for env_item in service.get("env", []):
        k, v = env_item.split("=", 1)
        env[k] = v
    log_out = open(f"logs/{name}.out", "a")
    log_err = open(f"logs/{name}.err", "a")
    print(f"[orchestrator] Launching {name}: {service['command']}")
    return subprocess.Popen(parts, stdout=log_out, stderr=log_err, env=env)

def check_health(name, service):
    health = service.get("health", {})
    if "http" in health:
        return http_health(health["http"])
    elif "tcp" in health:
        host, port = health["tcp"].split(":")
        return tcp_health(host, int(port))
    return True

while True:
    for name, svc in services.items():
        proc = procs.get(name)
        healthy = True
        if proc and proc.poll() is None:
            healthy = check_health(name, svc)
        if not proc or proc.poll() is not None or not healthy:
            if proc and proc.poll() is None:
                print(f"[orchestrator] {name} unhealthy—restarting")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except:
                    proc.kill()
            procs[name] = launch_service(name, svc)
    time.sleep(10)
