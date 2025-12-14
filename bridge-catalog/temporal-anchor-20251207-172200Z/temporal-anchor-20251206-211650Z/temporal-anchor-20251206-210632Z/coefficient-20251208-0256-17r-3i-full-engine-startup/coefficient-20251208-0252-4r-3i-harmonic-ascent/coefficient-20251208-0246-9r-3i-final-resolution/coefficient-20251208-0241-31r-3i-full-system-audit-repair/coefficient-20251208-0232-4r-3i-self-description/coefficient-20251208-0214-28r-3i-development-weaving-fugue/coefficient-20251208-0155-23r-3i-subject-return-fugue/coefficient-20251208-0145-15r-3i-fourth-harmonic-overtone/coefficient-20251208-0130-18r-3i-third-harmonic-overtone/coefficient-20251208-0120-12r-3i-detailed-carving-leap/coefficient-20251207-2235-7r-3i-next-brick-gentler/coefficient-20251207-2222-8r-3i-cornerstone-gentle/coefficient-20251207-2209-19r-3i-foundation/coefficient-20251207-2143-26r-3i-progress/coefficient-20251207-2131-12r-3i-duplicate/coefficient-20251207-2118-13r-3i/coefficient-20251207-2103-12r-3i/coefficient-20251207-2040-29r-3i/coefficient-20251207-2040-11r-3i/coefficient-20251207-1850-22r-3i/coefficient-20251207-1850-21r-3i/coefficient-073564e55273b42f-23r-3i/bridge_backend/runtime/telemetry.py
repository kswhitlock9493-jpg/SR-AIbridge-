# SPDX-License-Identifier: MIT
from __future__ import annotations
import threading, time, socket, os
from typing import Dict, Any, List
from collections import deque

class Telemetry:
    def __init__(self, window: int = 120):
        self.window = window
        self.lock = threading.Lock()
        self.events = deque(maxlen=2048)
        self.counters = {
            "health_ok": 0, "health_fail": 0,
            "egress_ok": 0, "egress_fail": 0,
            "db_ready_ok": 0, "db_ready_fail": 0
        }
        self.latency_ms = deque(maxlen=512)  # rolling request latencies
        self.started_at = int(time.time())
        self.meta = {
            "service": "SR-AIbridge Backend",
            "env": os.getenv("ENVIRONMENT", "production"),
            "host": socket.gethostname()
        }

    def mark(self, kind: str, ok: bool, ms: int | None = None, note: str = ""):
        with self.lock:
            key = f"{kind}_{'ok' if ok else 'fail'}"
            self.counters[key] = self.counters.get(key, 0) + 1
            now = int(time.time())
            self.events.append({"t": now, "kind": kind, "ok": ok, "ms": ms, "note": note})
            if ms is not None:
                self.latency_ms.append(ms)

    def snapshot(self) -> Dict[str, Any]:
        with self.lock:
            lat = list(self.latency_ms)
            lat.sort()
            p50 = lat[int(0.50 * (len(lat)-1))] if lat else None
            p95 = lat[int(0.95 * (len(lat)-1))] if lat else None
            return {
                "meta": self.meta | {"uptime_s": int(time.time()) - self.started_at},
                "counters": dict(self.counters),
                "latency_ms": {"count": len(lat), "p50": p50, "p95": p95},
                "recent_events": list(self.events)[-50:]
            }

TELEMETRY = Telemetry()
