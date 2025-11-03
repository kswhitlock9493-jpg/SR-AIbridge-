# brh/forge_auth.py
import os
import hmac
import hashlib
import time
import urllib.parse as up
from dataclasses import dataclass


@dataclass
class ForgeContext:
    raw: str
    root: str
    env: str
    epoch: int
    sig: str


FORGE_ENV = os.getenv("FORGE_DOMINION_ROOT", "")


def parse_forge_root(raw: str = FORGE_ENV) -> ForgeContext:
    if not raw:
        raise RuntimeError("FORGE_DOMINION_ROOT missing")
    url = up.urlparse(raw)
    qs = up.parse_qs(url.query)
    env = (qs.get("env") or ["unknown"])[0]
    epoch = int((qs.get("epoch") or ["0"])[0])
    sig = (qs.get("sig") or [""])[0]
    root = f"{url.scheme}://{url.netloc}"
    return ForgeContext(raw=raw, root=root, env=env, epoch=epoch, sig=sig)


def verify_seal(ctx: ForgeContext, *, skew_seconds: int = 900) -> None:
    """HMAC-SHA256 over '<root>|<env>|<epoch>' using DOMINION_SEAL.
       Rejects if time skew > ±15 min or sig mismatch (unless allow_unsigned)."""
    seal = os.getenv("DOMINION_SEAL", "")
    allow_unsigned = os.getenv("BRH_ALLOW_UNSIGNED", "false").lower() == "true"
    if not seal:
        if allow_unsigned:
            return
        raise RuntimeError("DOMINION_SEAL missing")

    msg = f"{ctx.root}|{ctx.env}|{ctx.epoch}".encode()
    want = hmac.new(seal.encode(), msg, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(want, ctx.sig):
        raise RuntimeError("Forge signature invalid")

    now = int(time.time())
    if abs(now - ctx.epoch) > skew_seconds:
        raise RuntimeError("Forge epoch skew too large")


def mint_ephemeral_token(ctx: ForgeContext) -> str:
    """Deterministic, short-lived token (Phase-1). Replace with SDTF call in Phase-2."""
    seal = os.getenv("DOMINION_SEAL", "dev-seal")
    msg = f"{ctx.root}|{ctx.env}|{ctx.epoch}|mint".encode()
    return hmac.new(seal.encode(), msg, hashlib.sha256).hexdigest()[:40]
