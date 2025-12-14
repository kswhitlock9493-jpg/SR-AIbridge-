from mangum import Mangum
from fastapi import FastAPI
import asyncio, os, time

app = FastAPI(title="BRH Cron")

@app.get("/run")
async def run():
    # nightly federation heartbeat / parity sweep
    await asyncio.sleep(0.05)
    return {"cron": "ok", "ts": time.time()}

handler = Mangum(app)
