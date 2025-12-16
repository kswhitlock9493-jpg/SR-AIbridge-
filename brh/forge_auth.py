# brh/forge_auth.py
import os
import hmac
import hashlib
import time
import urllib.parse as up
from dataclasses import dataclass
from typing import Optional

# -----------------------------------------------------------------------------
# Environment retrieval (bridge-aware, Termux-safe)
# -----------------------------------------------------------------------------

try:
    # Preferred: sovereign secret forge (server / full bridge)
    from bridge_backend.bridge_core.token_forge_dominion.secret_forge import (
        retrieve_environment,
    )
except ImportError:
    # Fallback: local / Termux / offline
    def retrieve_environment(key: str, default: Optional[str] = None) -> Optional[str]:
        return os.getenv(key, default)


# -----------------------------------------------------------------------------
# Constants (tuned for mobile + sovereign environments)
# -----------------------------------------------------------------------------

DEFAULT_SKEW_SECONDS = int(
    retrieve_environment("BRH_EPOCH_SKEW_SECONDS", "3600")
)  # 1 hour default

ALLOW_UNSIGNED = (
    retrieve_environment("BRH_ALLOW_UNSIGNED", "false").lower() == "true"
)

# -----------------------------------------------------------------------------
# Data model
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class ForgeContext:
    raw: str
    root: str
    env: str
    epoch: int
    sig: str


# -----------------------------------------------------------------------------
# Parsing
# -----------------------------------------------------------------------------

FORGE_ENV_RAW = retrieve_environment("FORGE_DOMINION_ROOT", "")


def parse_forge_root(raw: str = FORGE_ENV_RAW) -> ForgeContext:
    """
    Parse a dominion:// root URI into a ForgeContext.
    """
    if not raw:
        raise RuntimeError("FORGE_DOMINION_ROOT missing")

    url = up.urlparse(raw)
    qs = up.parse_qs(url.query)

    env = (qs.get("env") or ["unknown"])[0]
    epoch = int((qs.get("epoch") or ["0"])[0])
    sig = (qs.get("sig") or [""])[0]

    root = f"{url.scheme}://{url.netloc}"

    return ForgeContext(
        raw=raw,
        root=root,
        env=env,
        epoch=epoch,
        sig=sig,
    )


# -----------------------------------------------------------------------------
# Verification
# -----------------------------------------------------------------------------

def verify_seal(
    ctx: ForgeContext,
    *,
    skew_seconds: int = DEFAULT_SKEW_SECONDS,
) -> None:
    """
    Verifies:
      - HMAC-SHA256 signature over <root>|<env>|<epoch>
      - Epoch skew within tolerance

    Designed to tolerate mobile clock drift while remaining secure.
    """

    seal = retrieve_environment("DOMINION_SEAL", "")

    if not seal:
        if ALLOW_UNSIGNED:
            return
        raise RuntimeError("DOMINION_SEAL missing")

    message = f"{ctx.root}|{ctx.env}|{ctx.epoch}".encode()
    expected = hmac.new(
        seal.encode(), message, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, ctx.sig):
        raise RuntimeError("Forge signature invalid")

    now = int(time.time())
    delta = abs(now - ctx.epoch)

    if delta > skew_seconds:
        raise RuntimeError(
            f"Forge epoch skew too large (delta={delta}s, allowed={skew_seconds}s)"
        )


# -----------------------------------------------------------------------------
# Token minting (Phase-1 deterministic)
# -----------------------------------------------------------------------------

def mint_ephemeral_token(ctx: ForgeContext) -> str:
    """
    Deterministic, short-lived token.
    Phase-1 only. Replace with SDF / rotating forge in Phase-2.
    """

    seal = retrieve_environment("DOMINION_SEAL", "")

    if not seal:
        raise RuntimeError("DOMINION_SEAL missing")

    payload = f"{ctx.root}|{ctx.env}|{ctx.epoch}|mint".encode()

    return hmac.new(
        seal.encode(), payload, hashlib.sha256
    ).hexdigest()[:40]
