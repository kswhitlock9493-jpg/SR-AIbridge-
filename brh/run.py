# brh/run.py
import os
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

MANIFEST = Path("bridge.runtime.yaml")


@dataclass
class HealthSpec:
    http: str | None = None
    tcp: str | None = None
    interval: float = 10.0
    timeout: float = 2.0
    retries: int = 12


def sh(cmd: list[str], **kw):
    print("⇒", " ".join(cmd))
    subprocess.check_call(cmd, **kw)


def ensure_network(name: str):
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
        ok = False
        if h.http:
            ok = http_ok(h.http, h.timeout)
        if h.tcp:
            ok = ok or tcp_ok(h.tcp, h.timeout)
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

    spec = yaml.safe_load(MANIFEST.read_text())
    assert spec["provider"]["kind"] == "docker", "Phase-1 supports docker only"

    net = spec["provider"].get("network", "brh_net")
    ensure_network(net)

    for name, s in spec["services"].items():
        print(f"\n[BRH] service: {name}")
        labels = {
            "brh.service": name,
            "brh.env": ctx.env,
            "brh.epoch": str(ctx.epoch),
        }
        env = (s.get("env") or []) + [f"BRH_TOKEN={token}", f"BRH_ENV={ctx.env}"]
        # Build if context exists; else ensure image present
        if "context" in s:
            dockerfile_path = s.get("dockerfile", "Dockerfile")
            # Build context is relative to current directory, dockerfile is inside context
            dockerfile = f"{s['context']}/{dockerfile_path}"
            sh(["docker", "build", "-t", s["image"], "-f", dockerfile, "."])

        # Stop existing (suppress errors if container doesn't exist)
        try:
            subprocess.run(
                ["docker", "rm", "-f", f"brh_{name}"],
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                check=False
            )
        except Exception:
            pass

        # Run
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

        # Health
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
        print(f"[BRH] {name} is healthy ✔")

    print("\n[BRH] all services healthy. Sovereign node online.")


if __name__ == "__main__":
    main()
