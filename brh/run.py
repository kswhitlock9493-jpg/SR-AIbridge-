import os
import shutil
import subprocess
import sys
import time
import socket
import json
import yaml
import requests
from pathlib import Path
from dataclasses import dataclass
from brh.forge_auth import parse_forge_root, verify_seal, mint_ephemeral_token
from brh import heartbeat_daemon, consensus, role

MANIFEST = Path("bridge.runtime.yaml")

def is_api_only_mode():
    # User can force, or autodetect Termux/Android or missing Docker.
    if os.environ.get("BRH_RUNTIME", "") == "api":
        return True
    if shutil.which("docker") is None or "/data/data/com.termux" in os.getcwd():
        return True
    return False

API_ONLY = is_api_only_mode()

@dataclass
class HealthSpec:
    http: str | None = None
    tcp: str | None = None
    interval: float = 10.0
    timeout: float = 2.0
    retries: int = 12

class NotLeaderError(Exception):
    """Raised when a non-leader node attempts orchestration"""
    pass

def sh(cmd: list[str], **kw):
    print("+", " ".join(cmd))
    if API_ONLY:
        print("[BRH][API-ONLY] Skipping shell execution:", " ".join(cmd))
        return
    subprocess.check_call(cmd, **kw)

def sh_guarded(cmd: list[str], **kw):
    if not role.am_leader():
        raise NotLeaderError("This BRH is not the elected leader; orchestration denied.")
    print("+", " ".join(cmd))
    if API_ONLY:
        print("[BRH][API-ONLY] Skipping leader shell execution:", " ".join(cmd))
        return
    subprocess.check_call(cmd, **kw)

def ensure_network(name: str):
    if API_ONLY:
        print(f"[BRH][API-ONLY] Skipping Docker network ensure '{name}' (Docker unavailable)")
        return
    try:
        subprocess.check_output(["docker", "network", "inspect", name])
    except subprocess.CalledProcessError:
        sh(["docker", "network", "create", name])

def tcp_ok(addr: str, timeout: float) -> bool:
    try:
        host, port = addr.split(":")
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except Exception:
        return False

def http_ok(url: str, timeout: float) -> bool:
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code < 500
    except Exception:
        return False

def wait_health(h: HealthSpec):
    for i in range(h.retries):
        http_ok_result = False
        tcp_ok_result = False
        if h.http:
            http_ok_result = http_ok(h.http, h.timeout)
        if h.tcp:
            tcp_ok_result = tcp_ok(h.tcp, h.timeout)
        # Both must pass if both defined
        if h.http and h.tcp:
            ok = http_ok_result and tcp_ok_result
        elif h.http:
            ok = http_ok_result
        elif h.tcp:
            ok = tcp_ok_result
        else:
            ok = True  # No health checks defined
        if ok:
            return
        time.sleep(h.interval)
    raise SystemExit("Health check failed")

def main():
    if not MANIFEST.exists():
        raise SystemExit("bridge.runtime.yaml not found")

    ctx = parse_forge_root()
    verify_seal(ctx)
    token = mint_ephemeral_token(ctx)
    print(f"[BRH] Forge root={ctx.root} env={ctx.env} epoch={ctx.epoch}")
    print(f"[BRH] ephemeral-token={token[:8]}… (masked)")

    if API_ONLY:
        print("[BRH] Running in API-only mode: Docker features and container orchestration are DISABLED (Termux/mobile/native mode enabled).\n")
    else:
        print("[BRH] Full orchestration mode: Docker enabled.\n")

    # Start heartbeat daemon
    heartbeat_daemon.start()
    # Start consensus coordinator
    consensus.start()

    # Start chaos injector if enabled (guard for imports)
    try:
        from brh import chaos
        chaos.start()
    except ImportError:
        pass

    # Start recovery watchtower if enabled (guard for imports)
    try:
        from brh import recovery
        recovery.start()
    except ImportError:
        pass

    spec = yaml.safe_load(MANIFEST.read_text())

    if API_ONLY:
        print("[BRH][API-ONLY] Skipping all Docker service orchestration.\nSovereign REST API/remote control is active.\n")
        print("[BRH] Node ready in API-only mode. All service orchestration functions are skipped!")
        return

    assert spec["provider"]["kind"] == "docker", "Phase-1 supports docker only"
    net = spec["provider"].get("network", "brh_net")
    ensure_network(net)

    for name, s in spec["services"].items():
        print(f"\n[BRH] service: {name}")
        labels = {
            "brh.service": name,
            "brh.env": ctx.env,
            "brh.epoch": str(ctx.epoch),
            "brh.owner": role.BRH_NODE_ID,
        }
        env = (s.get("env") or []) + [f"BRH_TOKEN={token}", f"BRH_ENV={ctx.env}", f"BRH_EPOCH={ctx.epoch}"]
        # Build if context exists, else ensure image present
        if "context" in s:
            dockerfile_path = s.get("dockerfile", "Dockerfile")
            dockerfile = f"{s['context']}/{dockerfile_path}"
            sh(["docker", "build", "-t", s["image"], "-f", dockerfile, "."])
        # Stop existing container (suppress errors if container doesn't exist)
        try:
            subprocess.run(
                ["docker", "rm", "-f", f"brh_{name}"],
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                check=False
            )
        except Exception:
            pass
        # Run container
        run = ["docker", "run", "-d", "--name", f"brh_{name}", "--network", net]
        for p in s.get("ports", []):
            run += ["-p", p]
        for v in s.get("volumes", []):
            run += ["-v", v]
        for k, v in labels.items():
            run += ["--label", f"{k}={v}"]
        for e in env:
            run += ["-e", e]
        run += [s["image"]]
        sh(run)
        # Health check
        h = s.get("health", {})
        hs = HealthSpec(
            http=h.get("http"),
            tcp=h.get("tcp"),
            interval=float(h.get("interval", "10s").rstrip("s")),
            timeout=float(h.get("timeout", "2s").rstrip("s")),
            retries=int(h.get("retries", 12)),
        )
        print(f"[BRH] waiting for health: {h}")
        wait_health(hs)
        print(f"[BRH] {name} is healthy ✔️")

    print("\n[BRH] all services healthy. Sovereign node online.")

if __name__ == "__main__":
    main()
