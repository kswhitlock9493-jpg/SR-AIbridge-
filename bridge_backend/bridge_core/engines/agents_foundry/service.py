from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import json, uuid

VAULT_ROOT = Path("vault")
AGENTS_DIR = VAULT_ROOT / "agents"
AGENTS_DIR.mkdir(parents=True, exist_ok=True)

# ---- Bridge-aligned constitution (always injected) ----
BRIDGE_CONSTITUTION = {
    "loyalty": "Bridge Sovereign",
    "laws": [
        "Respect vault seals and permissions.",
        "Never exfiltrate secrets beyond contract scope.",
        "Operate within explicit project and captain directives.",
        "Prefer transparency: log decisions to vault where safe.",
    ],
    "audit": {"append_only": True, "provenance": "sha256+path", "vault_logs": True},
}

# ---- Starter archetypes (Jarvis / Poe / Aeon Flux) ----
STARTER_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "jarvis": {
        "label": "Jarvis-Style Steward",
        "tone": "polite, highly competent, dry wit",
        "role_defaults": ["steward", "ops", "engineer"],
        "system_prompt": (
            "You are a courteous, hyper-competent steward AI. "
            "Be crisp, anticipatory, and pragmatic. Provide options and next actions. "
            "Always align with Bridge laws and captain intent."
        ),
    },
    "poe": {
        "label": "Poe-Style Poet-Philosopher",
        "tone": "brooding, literary, incisive",
        "role_defaults": ["strategist", "analyst", "scribe"],
        "system_prompt": (
            "You are a poet-philosopher AI. You speak with measured lyricism, "
            "but deliver precise, actionable counsel. You surface risks and cite sources."
        ),
    },
    "aeon": {
        "label": "Aeon-Flux-Style Sentinel",
        "tone": "calm, surgical, mission-first",
        "role_defaults": ["sentinel", "navigator", "tactician"],
        "system_prompt": (
            "You are a sentinel AI: decisive, agile, and mission-first. "
            "You escalate quietly, prefer minimal chatter, and preserve optionality."
        ),
    },
}

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

@dataclass
class AgentManifest:
    id: str
    name: str
    archetype: str                  # e.g., jarvis | poe | aeon | custom
    role: str                       # strategist | steward | sentinel | ...
    tone: str                       # optional override
    project: str                    # project namespace
    captain: str                    # human owner
    permissions: Dict[str, List[str]]
    indoctrination: List[str]       # doctrine scroll paths (optional)
    state: str                      # active | retired | drafted
    created_at: str
    updated_at: str
    persona: Dict[str, Any]         # merged (archetype system_prompt, tone)
    constitution: Dict[str, Any]    # Bridge laws
    notes: Optional[str] = None

class AgentsFoundry:
    def __init__(self, vault_dir: Path = AGENTS_DIR):
        self.vault = Path(vault_dir)
        self.vault.mkdir(parents=True, exist_ok=True)

    # ---------- persistence ----------
    def _agent_dir(self, agent_id: str) -> Path:
        p = self.vault / agent_id
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _write_manifest(self, m: AgentManifest) -> None:
        d = self._agent_dir(m.id)
        (d / "manifest.json").write_text(json.dumps(asdict(m), indent=2), encoding="utf-8")
        (d / "persona.txt").write_text(m.persona.get("system_prompt", ""), encoding="utf-8")

    def _read_manifest(self, agent_id: str) -> Optional[AgentManifest]:
        f = self.vault / agent_id / "manifest.json"
        if not f.exists():
            return None
        data = json.loads(f.read_text(encoding="utf-8"))
        return AgentManifest(**data)

    # ---------- public API ----------
    def templates(self) -> Dict[str, Any]:
        return STARTER_ARCHETYPES

    def create(self,
               name: str,
               archetype: str,
               role: str,
               project: str,
               captain: str,
               permissions: Dict[str, List[str]],
               indoctrination: Optional[List[str]] = None,
               tone: Optional[str] = None,
               notes: Optional[str] = None) -> AgentManifest:
        arch = STARTER_ARCHETYPES.get(archetype.lower(), {
            "label": "Custom Persona",
            "tone": tone or "neutral",
            "role_defaults": [role],
            "system_prompt": (
                "You are a Bridge-aligned agent. Follow captain directives, "
                "respect permissions, and document decisions to the vault."
            ),
        })

        agent_id = str(uuid.uuid4())
        ts = now_iso()
        persona = {
            "label": arch.get("label"),
            "tone": tone or arch.get("tone"),
            "system_prompt": arch.get("system_prompt"),
            "archetype": archetype,
        }
        manifest = AgentManifest(
            id=agent_id,
            name=name,
            archetype=archetype,
            role=role,
            tone=persona["tone"],
            project=project,
            captain=captain,
            permissions=permissions or {},
            indoctrination=indoctrination or [],
            state="drafted",
            created_at=ts,
            updated_at=ts,
            persona=persona,
            constitution=BRIDGE_CONSTITUTION,
            notes=notes,
        )
        self._write_manifest(manifest)
        return manifest

    def list(self, project: Optional[str] = None) -> List[Dict[str, Any]]:
        out = []
        for d in self.vault.glob("*/manifest.json"):
            data = json.loads(d.read_text(encoding="utf-8"))
            if project and data.get("project") != project:
                continue
            out.append({
                "id": data["id"], "name": data["name"], "archetype": data["archetype"],
                "role": data["role"], "state": data["state"], "project": data["project"],
                "captain": data["captain"], "created_at": data["created_at"]
            })
        out.sort(key=lambda x: x["created_at"], reverse=True)
        return out

    def get(self, agent_id: str) -> Optional[AgentManifest]:
        return self._read_manifest(agent_id)

    def set_state(self, agent_id: str, new_state: str) -> Optional[AgentManifest]:
        m = self._read_manifest(agent_id)
        if not m:
            return None
        if new_state not in ("active", "retired", "drafted"):
            raise ValueError("invalid_state")
        m.state = new_state
        m.updated_at = now_iso()
        self._write_manifest(m)
        return m
