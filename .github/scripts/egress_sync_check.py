#!/usr/bin/env python3
# v1.8.3 — verifies outbound endpoints before deploy
import json, sys, socket, ssl, time

TARGETS = [
  "api.netlify.com", "netlify.com",
  "api.render.com", "render.com",
  "api.github.com", "github.com", "codeload.github.com",
  "registry.npmjs.org", "nodejs.org",
  "diagnostics.sr-aibridge.com", "sr-aibridge.onrender.com"
]
PORT = 443

def probe(host):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, PORT), timeout=6) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                return {"host": host, "ok": True, "cert": ssock.version()}
    except Exception as e:
        return {"host": host, "ok": False, "err": str(e)}

def main():
    res = [probe(h) for h in TARGETS]
    ok = all(r["ok"] for r in res)
    print(json.dumps({"ok": ok, "results": res}, indent=2))
    sys.exit(0 if ok else 2)

if __name__ == "__main__":
    main()
