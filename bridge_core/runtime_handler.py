#!/usr/bin/env python3
import asyncio, subprocess, yaml, pathlib, logging, signal, time, os
from datetime import datetime, timedelta

MANIFEST  = pathlib.Path("src/bridge.runtime.yaml")
VAULT     = pathlib.Path("vault/runtime")
VAULT.mkdir(parents=True, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="[BRH] %(message)s")

def load_manifest():
    with MANIFEST.open() as f:
        return yaml.safe_load(f)

async def health_check(port=1440):
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection("localhost", port), 5)
        writer.write(b"GET /qic/health HTTP/1.1\r\nHost: localhost\r\n\r\n")
        await writer.drain()
        line = await reader.readline()
        writer.close()
        return b"200" in line
    except Exception:
        return False

async def verify_task():
    while True:
        await asyncio.sleep(86400)          # 24 h
        logging.info("Running 24 h verify loop…")
        proc = await asyncio.create_subprocess_exec(
            "python", "bridge_core/verify_loop.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            logging.warning("Verify loop failed: %s", stderr.decode())
        else:
            logging.info("Verify loop passed")

async def container_loop():
    manifest = load_manifest()
    cmd = manifest["runtime"]["containers"][0]["command"]
    proc = None
    while True:
        if proc is None or proc.returncode is not None:
            logging.info("Starting QIC daemon…")
            proc = await asyncio.create_subprocess_exec(*cmd)
        await asyncio.sleep(17)
        if not await health_check():
            logging.warning("Health fail – restarting")
            proc.terminate()
            await proc.wait()
            proc = None
        else:
            logging.info("Health OK")

async def main():
    await asyncio.gather(container_loop(), verify_task())

def shutdown(sig, frame):
    logging.info("Shutdown received")
    exit(0)

signal.signal(signal.SIGINT, shutdown)

if __name__ == "__main__":
    asyncio.run(main())
