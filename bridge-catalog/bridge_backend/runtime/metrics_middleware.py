# SPDX-License-Identifier: MIT
import time
from fastapi import Request
from .telemetry import TELEMETRY

async def metrics_middleware(request: Request, call_next):
    t0 = time.perf_counter()
    try:
        response = await call_next(request)
        ms = int((time.perf_counter() - t0) * 1000)
        TELEMETRY.latency_ms.append(ms)  # thin sampling; detailed via health hooks
        return response
    except Exception as e:
        ms = int((time.perf_counter() - t0) * 1000)
        TELEMETRY.events.append({"t": int(time.time()), "kind": "request_err", "ok": False, "ms": ms, "note": str(e)})
        raise
