import os
from dataclasses import dataclass
from typing import List

def _csv(name: str, default: str="") -> List[str]:
    v = os.getenv(name, default).strip()
    return [s.strip() for s in v.split(",") if s.strip()]

@dataclass
class EnvSyncConfig:
    enabled: bool = os.getenv("ENVSYNC_ENABLED","true").lower() == "true"
    mode: str = os.getenv("ENVSYNC_MODE","enforce")
    schedule: str = os.getenv("ENVSYNC_SCHEDULE","@hourly")
    canonical_source: str = os.getenv("ENVSYNC_CANONICAL_SOURCE","vault")
    targets: List[str] = None
    discovery_order: List[str] = None
    secret_filenames: List[str] = None
    vault_token_keys: List[str] = None
    dashboard_token_urls: List[str] = None
    include_prefixes: List[str] = None
    exclude_prefixes: List[str] = None
    allow_deletions: bool = os.getenv("ENVSYNC_ALLOW_DELETIONS","false").lower() == "true"
    
    def __post_init__(self):
        if self.targets is None:
            self.targets = _csv("ENVSYNC_TARGETS","render,netlify")
        if self.discovery_order is None:
            self.discovery_order = _csv("ENVSYNC_DISCOVERY_ORDER","env,secret_files,vault,dashboard")
        if self.secret_filenames is None:
            self.secret_filenames = _csv("ENVSYNC_SECRET_FILENAMES","render.token,netlify.token")
        if self.vault_token_keys is None:
            self.vault_token_keys = _csv("ENVSYNC_VAULT_TOKEN_KEYS","RENDER_API_TOKEN,NETLIFY_API_TOKEN")
        if self.dashboard_token_urls is None:
            self.dashboard_token_urls = _csv("ENVSYNC_DASHBOARD_TOKEN_URLS","")
        if self.include_prefixes is None:
            self.include_prefixes = _csv("ENVSYNC_INCLUDE_PREFIXES","BRIDGE_,SR_,HEART_,ENVSYNC_")
        if self.exclude_prefixes is None:
            self.exclude_prefixes = _csv("ENVSYNC_EXCLUDE_PREFIXES","SECRET_,INTERNAL_,DEBUG_")

CONFIG = EnvSyncConfig()
