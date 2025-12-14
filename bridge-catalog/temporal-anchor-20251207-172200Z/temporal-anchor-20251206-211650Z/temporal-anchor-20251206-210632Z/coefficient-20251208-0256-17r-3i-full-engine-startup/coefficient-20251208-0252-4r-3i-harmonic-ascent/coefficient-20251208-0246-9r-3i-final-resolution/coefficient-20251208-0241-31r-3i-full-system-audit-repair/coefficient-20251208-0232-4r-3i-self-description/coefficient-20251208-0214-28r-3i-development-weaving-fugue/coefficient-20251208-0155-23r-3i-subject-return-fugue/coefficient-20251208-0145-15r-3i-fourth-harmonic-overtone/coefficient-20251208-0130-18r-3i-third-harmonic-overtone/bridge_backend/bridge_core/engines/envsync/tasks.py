import asyncio, logging
from .config import CONFIG
from .engine import sync_provider

log = logging.getLogger(__name__)

async def run_scheduled_sync():
    if not CONFIG.enabled:
        log.info("EnvSync disabled; skipping.")
        return
    for p in CONFIG.targets:
        try:
            res = await sync_provider(p, CONFIG.mode)  # enforce or dry-run
            changed = [d for d in res["diff"] if d["op"] in ("create","update","delete")]
            log.info(f"[EnvSync] {p}: applied={res['applied']} changes={len(changed)} errors={len(res['errors'])}")
        except Exception as e:
            log.exception(f"[EnvSync] Provider {p} crashed: {e}")

# You already have heartbeat/scheduler infra; register a periodic task there.
