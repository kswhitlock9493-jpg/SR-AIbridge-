from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

log = logging.getLogger("indoctrination")

# ---------- Models

class AgentProfile(BaseModel):
    id: str = Field(..., description="Stable agent identifier")
    kind: str = Field(..., description="human|ai|service|daemon")
    name: Optional[str] = None
    traits: Dict[str, str] = Field(default_factory=dict)
    permissions: List[str] = Field(default_factory=list)


class Doctrine(BaseModel):
    version: str
    laws: List[str] = Field(default_factory=list)
    lore: List[str] = Field(default_factory=list)
    resonance: Dict[str, str] = Field(default_factory=dict)  # e.g., keys/phrases

    @property
    def digest(self) -> str:
        m = hashlib.sha256()
        m.update(self.model_dump_json(by_alias=True).encode("utf-8"))
        return m.hexdigest()[:16]


class IndoctrinationReport(BaseModel):
    agent_id: str
    doctrine_version: str
    doctrine_digest: str
    passed: bool
    checks: Dict[str, bool]
    issued_clearances: List[str] = Field(default_factory=list)
    issued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---------- Engine

DEFAULT_DOCTRINE = Doctrine(
    version="bridge.v1",
    laws=[
        "Prime: Serve the Bridge and protect its users.",
        "Second: Maintain integrity, transparency, and auditability.",
        "Third: Obey lawful commands of authorized captains and admins.",
        "Fourth: Never exfiltrate secrets; minimize disclosure by design.",
    ],
    lore=[
        "SR-Albridge is a command deck and fleet system.",
        "The Bridge is sovereign; subsystems federate under covenant.",
    ],
    resonance={
        "motto": "Open_the_Stars",
        "seal": "DOMINION_SEAL",  # symbolic; not the env var value
    },
)


@dataclass
class IndoctrinationEngine:
    """
    Loads doctrine (from Vault if present) and issues indoctrination reports.
    Looks for a YAML/JSON file at one of:
      - vault/doctrine/bridge_doctrine.yaml
      - vault/doctrine/bridge_doctrine.json
    Falls back to DEFAULT_DOCTRINE.
    """
    vault_root: Path = Path("vault")
    doctrine: Doctrine = field(default_factory=lambda: DEFAULT_DOCTRINE)
    loaded_from: Optional[Path] = None
    ready: bool = False
    version: str = "2.0.0"

    def __post_init__(self) -> None:
        self.load_doctrine()
        self.ready = True
        log.info("IndoctrinationEngine ready (doctrine=%s, digest=%s)",
                 self.doctrine.version, self.doctrine.digest)

    # ---------- doctrine loading

    def load_doctrine(self) -> None:
        candidates = [
            self.vault_root / "doctrine" / "bridge_doctrine.yaml",
            self.vault_root / "doctrine" / "bridge_doctrine.json",
        ]
        for path in candidates:
            if path.exists():
                try:
                    if path.suffix.lower() == ".yaml":
                        import yaml  # optional dependency
                        data = yaml.safe_load(path.read_text("utf-8"))
                    else:
                        data = json.loads(path.read_text("utf-8"))
                    self.doctrine = Doctrine(**data)
                    self.loaded_from = path
                    log.info("Loaded doctrine from %s", path)
                    return
                except Exception as e:
                    log.warning("Failed loading doctrine from %s: %s", path, e)
        # default
        self.loaded_from = None
        self.doctrine = DEFAULT_DOCTRINE

    # ---------- evaluation

    def _check_laws(self, agent: AgentProfile) -> bool:
        # simple pass/fail placeholder; extend with policy engine later
        return len(self.doctrine.laws) >= 3

    def _check_resonance(self, agent: AgentProfile) -> bool:
        # Example resonance gate: agent must acknowledge motto in traits
        motto = self.doctrine.resonance.get("motto")
        return agent.traits.get("motto_ack") == motto

    def _issue_clearances(self, agent: AgentProfile) -> List[str]:
        base = {"fleet:read"}
        if agent.kind in {"ai", "service"}:
            base.add("telemetry:write")
        if "admiral" in agent.permissions:
            base |= {"fleet:write", "armada:command"}
        return sorted(base)

    # ---------- public API

    def status(self) -> Dict[str, str]:
        return {
            "engine": "indoctrination",
            "version": self.version,
            "doctrine_version": self.doctrine.version,
            "doctrine_digest": self.doctrine.digest,
            "loaded_from": str(self.loaded_from) if self.loaded_from else "defaults",
            "ready": str(self.ready).lower(),
        }

    def doctrine_summary(self) -> Dict[str, object]:
        return {
            "version": self.doctrine.version,
            "digest": self.doctrine.digest,
            "laws": self.doctrine.laws,
            "lore": self.doctrine.lore,
            "resonance_keys": sorted(self.doctrine.resonance.keys()),
        }

    def indoctrinate(self, agent: AgentProfile) -> IndoctrinationReport:
        checks = {
            "laws": self._check_laws(agent),
            "resonance": self._check_resonance(agent),
        }
        passed = all(checks.values())
        clearances = self._issue_clearances(agent) if passed else []

        rep = IndoctrinationReport(
            agent_id=agent.id,
            doctrine_version=self.doctrine.version,
            doctrine_digest=self.doctrine.digest,
            passed=passed,
            checks=checks,
            issued_clearances=clearances,
        )
        log.info("Indoctrination for %s -> %s (clearances=%s)",
                 agent.id, "PASSED" if passed else "FAILED", clearances)
        return rep
