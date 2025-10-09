#!/usr/bin/env python3
"""
Egress connectivity canary
Verifies outbound network connectivity to critical hosts
"""
import socket
import sys
import argparse

HOSTS = [
    "api.github.com",
    "codeload.github.com",
    "registry.npmjs.org",
    "nodejs.org",
    "api.render.com",
    "render.com",
    "api.netlify.com",
    "netlify.com",
]

def check_host(host, port=443, timeout=3):
    """Check if a host is reachable"""
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True
    except Exception:
        return False
    finally:
        s.close()

def main(timeout=6):
    """Check all hosts"""
    print("[egress_canary] Checking network egress...")
    
    failed = []
    for host in HOSTS:
        if not check_host(host, timeout=timeout):
            failed.append(host)
            print(f"[egress_canary] ✗ {host}")
        else:
            print(f"[egress_canary] ✓ {host}")
    
    if failed:
        print(f"[egress_canary] Egress blocked to: {', '.join(failed)}")
        return 1
    
    print("[egress_canary] All hosts reachable")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=6)
    args = parser.parse_args()
    
    sys.exit(main(timeout=args.timeout))
