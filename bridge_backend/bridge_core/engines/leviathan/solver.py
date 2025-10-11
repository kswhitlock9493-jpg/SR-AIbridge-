from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re

# Vault locations
SOLVER_DIR = Path("vault") / "leviathan" / "solver"
SOLVER_DIR.mkdir(parents=True, exist_ok=True)

# --- Light imports from your existing engines (all local, no HTTP) ---
# Truth layer
try:
    from bridge_core.engines.truth.utils import TRUTH_DIR, read_jsonl, PARSER_LEDGER, load_chunk_text
except Exception:
    TRUTH_DIR = Path("vault") / "truth"
    def read_jsonl(p: Path): return []
    PARSER_LEDGER = Path("vault") / "parser" / "ledger.jsonl"
    def load_chunk_text(sha: str): return None

# Autonomy engine
try:
    from bridge_core.engines.autonomy.service import AutonomyEngine
except Exception:
    AutonomyEngine = None

# Six Super Engines - import the actual engines
try:
    from bridge_core.engines import (
        CalculusCore, QHelmSingularity, AuroraForge,
        ChronicleLoom, ScrollTongue, CommerceForge
    )
    ENGINES_AVAILABLE = True
except Exception:
    ENGINES_AVAILABLE = False
    CalculusCore = None
    QHelmSingularity = None
    AuroraForge = None
    ChronicleLoom = None
    ScrollTongue = None
    CommerceForge = None

# --- Helpers ---
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"

def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()

def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

# --- Minimal "intent" classifier & decomposition (deterministic, local) ---
INTENT_PATTERNS = {
    "research": [r"\bwhat\b", r"\bcompare\b", r"\bsurvey\b", r"\bpaper\b", r"\bstate of the art\b"],
    "plan":     [r"\bplan\b", r"\broadmap\b", r"\bphases?\b", r"\bmilestones?\b"],
    "design":   [r"\bdesign\b", r"\barchitecture\b", r"\bspec\b", r"\bprototype\b"],
}

def classify_intents(q: str) -> List[str]:
    ql = q.lower()
    hits = []
    for label, pats in INTENT_PATTERNS.items():
        if any(re.search(p, ql) for p in pats):
            hits.append(label)
    if not hits:
        hits = ["research","plan"]  # safe default
    return hits

def decompose(q: str, intents: List[str]) -> List[Dict[str, Any]]:
    subs = []
    if "research" in intents:
        subs.append({"id":"literature_scan","prompt":f"Survey prior art for: {q}"})
    if "design" in intents:
        subs.append({"id":"architecture_sketch","prompt":f"Sketch architecture for: {q}"})
    if "plan" in intents:
        subs.append({"id":"execution_plan","prompt":f"Produce phases/risks for: {q}"})
    # Always include requirements synthesis
    subs.append({"id":"requirements","prompt":f"List math/hardware/software/team needs for: {q}"})
    return subs

# --- Truth grounding (Parser ledger + Truth truths) ---
def ground_in_truth(q: str, limit: int = 25) -> Dict[str, Any]:
    # 1) parser ledger → collect sentences that mention tokens from q
    ledger = read_jsonl(PARSER_LEDGER) if PARSER_LEDGER.exists() else []
    tokens = set(re.findall(r"\w+", q.lower()))
    candidates = []
    for row in ledger:
        sha = row.get("sha") or row.get("hash") or row.get("id")
        if not sha: 
            continue
        txt = load_chunk_text(sha) or ""
        if not txt:
            continue
        if any(t in txt.lower() for t in tokens):
            snippet = txt[:400]
            candidates.append({"sha": sha, "source": row.get("source"), "ts": row.get("ts"), "snippet": snippet})
    # 2) bound truths (if any)
    truths_file = TRUTH_DIR / "truths.jsonl"
    truths = read_jsonl(truths_file)[:limit] if truths_file.exists() else []

    return {
        "parser_hits": candidates[:limit],
        "truths": truths[:limit]
    }

# --- Adapter layer for Six Super Engines ---

def engine_math_science(q: str) -> Dict[str, Any]:
    """
    Adapter for CalculusCore (Math) and QHelmSingularity (Quantum/Science)
    """
    result = {
        "notes": [],
        "requirements": {"math": [], "science": [], "quantum": []},
    }
    
    if ENGINES_AVAILABLE and CalculusCore:
        try:
            # Initialize CalculusCore
            calc = CalculusCore()
            
            # Extract mathematical concepts from query
            math_keywords = ["projection", "rotation", "transform", "operator", "dimension", "4D", "R4"]
            math_notes = []
            math_reqs = []
            
            for keyword in math_keywords:
                if keyword.lower() in q.lower():
                    if "4D" in keyword or "R4" in keyword:
                        math_notes.append("Model high-dimensional transforms; define projection operators.")
                        math_reqs.append("ℝ⁴ rotations")
                    if "projection" in keyword.lower():
                        math_reqs.append("projection operators")
                    if "rotation" in keyword.lower() or "transform" in keyword.lower():
                        math_notes.append("Bound computational complexity; estimate FLOPs for real-time rendering.")
            
            if math_notes:
                result["notes"].extend(math_notes)
            if math_reqs:
                result["requirements"]["math"].extend(math_reqs)
                
        except Exception as e:
            result["notes"].append(f"CalculusCore adapter note: {str(e)[:100]}")
    
    if ENGINES_AVAILABLE and QHelmSingularity:
        try:
            # Initialize QHelmSingularity for quantum/physics aspects
            qhelm = QHelmSingularity()
            
            # Extract quantum/science concepts
            quantum_keywords = ["quantum", "singularity", "spacetime", "physics"]
            for keyword in quantum_keywords:
                if keyword.lower() in q.lower():
                    result["notes"].append("Quantum entanglement patterns for data correlation")
                    result["requirements"]["quantum"].append("quantum state modeling")
                    break
                    
            # Add science requirements for display/optics
            if any(word in q.lower() for word in ["display", "visual", "render", "3D", "4D"]):
                result["requirements"]["science"].append("optics/display tradeoffs")
                
        except Exception as e:
            result["notes"].append(f"QHelmSingularity adapter note: {str(e)[:100]}")
    
    # Fallback to deterministic notes if engines not available
    if not result["notes"]:
        result["notes"] = [
            "Model high-dimensional transforms; define projection operators.",
            "Bound computational complexity; estimate FLOPs for real-time rendering."
        ]
        result["requirements"]["math"] = ["ℝ⁴ rotations", "projection operators"]
        result["requirements"]["science"] = ["optics/display tradeoffs"]
    
    return result

def engine_creativity(q: str) -> Dict[str, Any]:
    """
    Adapter for AuroraForge (Creativity/Visual)
    """
    result = {
        "notes": [],
        "artifacts": []
    }
    
    if ENGINES_AVAILABLE and AuroraForge:
        try:
            # Initialize AuroraForge
            aurora = AuroraForge()
            
            # Extract creative/visual concepts
            visual_keywords = ["demo", "UX", "interface", "visualization", "graphics", "interactive"]
            creative_notes = []
            artifacts = []
            
            for keyword in visual_keywords:
                if keyword.lower() in q.lower():
                    if "demo" in keyword.lower():
                        creative_notes.append("Narrative & UX: interactive hyperslicing, color-by-w cues, demo tour script.")
                        artifacts.extend(["demo_script.md", "ux_wireframes.png"])
                    if "ux" in keyword.lower() or "interface" in keyword.lower():
                        creative_notes.append("Artifacts: diagrams, explainer graphics, onboarding tutorial.")
                        artifacts.append("onboarding_tutorial.md")
                    if "visual" in keyword.lower() or "graphics" in keyword.lower():
                        artifacts.append("visualization_mockups.png")
            
            if creative_notes:
                result["notes"].extend(creative_notes)
            if artifacts:
                result["artifacts"].extend(list(set(artifacts)))  # Remove duplicates
                
        except Exception as e:
            result["notes"].append(f"AuroraForge adapter note: {str(e)[:100]}")
    
    # Fallback to deterministic notes
    if not result["notes"]:
        result["notes"] = [
            "Narrative & UX: interactive hyperslicing, color-by-w cues, demo tour script.",
            "Artifacts: diagrams, explainer graphics, onboarding tutorial."
        ]
        result["artifacts"] = ["demo_script.md", "ux_wireframes.png"]
    
    return result

def engine_business(q: str) -> Dict[str, Any]:
    """
    Adapter for CommerceForge (Business/Economic)
    """
    result = {
        "notes": [],
        "requirements": {"ops": [], "team": []},
    }
    
    if ENGINES_AVAILABLE and CommerceForge:
        try:
            # Initialize CommerceForge
            commerce = CommerceForge()
            
            # Extract business/economic concepts
            business_keywords = ["cost", "budget", "vendor", "team", "resource", "BOM", "hardware"]
            biz_notes = []
            ops_reqs = []
            team_reqs = []
            
            for keyword in business_keywords:
                if keyword.lower() in q.lower():
                    if "cost" in keyword.lower() or "budget" in keyword.lower():
                        biz_notes.append("Estimate BOM if hardware path; vendor shortlist; target segments.")
                        ops_reqs.append("budget bands")
                    if "vendor" in keyword.lower() or "hardware" in keyword.lower():
                        ops_reqs.append("vendor scan")
                    if "team" in keyword.lower() or "resource" in keyword.lower():
                        team_reqs.extend(["graphics eng", "applied math", "UX"])
            
            if biz_notes:
                result["notes"].extend(biz_notes)
            if ops_reqs:
                result["requirements"]["ops"].extend(list(set(ops_reqs)))
            if team_reqs:
                result["requirements"]["team"].extend(list(set(team_reqs)))
                
        except Exception as e:
            result["notes"].append(f"CommerceForge adapter note: {str(e)[:100]}")
    
    # Fallback to deterministic notes
    if not result["notes"]:
        result["notes"] = ["Estimate BOM if hardware path; vendor shortlist; target segments."]
    if not result["requirements"]["ops"]:
        result["requirements"]["ops"] = ["vendor scan","budget bands"]
    if not result["requirements"]["team"]:
        result["requirements"]["team"] = ["graphics eng","applied math","UX"]
    
    return result

def engine_language(q: str, synthesized_points: List[str]) -> str:
    """
    Adapter for ScrollTongue (Language/NLP)
    """
    if ENGINES_AVAILABLE and ScrollTongue:
        try:
            # Initialize ScrollTongue
            scroll = ScrollTongue()
            
            # Use ScrollTongue for synthesis
            # For now, just combine points with better formatting
            synthesis = " ".join(synthesized_points)
            
            # Could use ScrollTongue's analyze method to improve the text
            # But for minimal changes, we'll keep it simple
            return synthesis[:1200]
            
        except Exception as e:
            pass
    
    # Fallback: Concise synthesis
    return " ".join(synthesized_points)[:1200]

def engine_history(q: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Adapter for ChronicleLoom (History/Chronicle)
    """
    result = {
        "notes": [],
        "chronicle_refs": []
    }
    
    if ENGINES_AVAILABLE and ChronicleLoom:
        try:
            # Initialize ChronicleLoom
            chronicle = ChronicleLoom()
            
            # Extract historical/chronicle concepts
            history_keywords = ["history", "previous", "prior", "past", "evolution", "chronicle"]
            
            for keyword in history_keywords:
                if keyword.lower() in q.lower():
                    result["notes"].append("Reference prior project phases and historical patterns")
                    result["chronicle_refs"].append("project_timeline")
                    break
                    
        except Exception as e:
            result["notes"].append(f"ChronicleLoom adapter note: {str(e)[:100]}")
    
    return result

# --- Optional Autonomy task dispatch ---
def maybe_dispatch_tasks(q: str, captain: str, project: str, dispatch: bool) -> List[Dict[str, Any]]:
    if not dispatch or AutonomyEngine is None:
        return []
    A = AutonomyEngine()
    tasks = []
    # 1) paper roundup
    t1 = A.create_task(
        project=project or "general",
        captain=captain or "unknown",
        permissions={"read": ["web","docs"], "write": ["vault"]},
        mode="hybrid",
        objective="paper_roundup",
        params={"query": q, "limit": 10}
    )
    tasks.append(asdict(t1))
    # 2) prototype scaffold
    t2 = A.create_task(
        project=project or "general",
        captain=captain or "unknown",
        permissions={"read": ["docs"], "write": ["repo","vault"]},
        mode="screen",
        objective="prototype_scaffold",
        params={"topic": q}
    )
    tasks.append(asdict(t2))
    return tasks

# --- Solver orchestrator ---
@dataclass
class SolveRequest:
    q: str
    captain: Optional[str] = None
    project: Optional[str] = None
    modes: Optional[List[str]] = None     # ["research","plan","design"]
    dispatch: bool = False                # spawn autonomy tasks
    allow_web: bool = False               # reserved for future web plane

def solve(payload: SolveRequest) -> Dict[str, Any]:
    q = payload.q.strip()
    intents = payload.modes or classify_intents(q)
    steps = decompose(q, intents)

    # Ground in existing knowledge
    grounding = ground_in_truth(q, limit=25)

    # Route to super engines via adapters
    m = engine_math_science(q)
    c = engine_creativity(q)
    b = engine_business(q)
    h = engine_history(q, steps)

    # Synthesize a short summary and a concrete phased plan
    points = [
        "We can approximate 4D→3D→2D via projection + hyperslicing with interactive rotation.",
        "For spatial display, explore light-field/volumetric/holo; desktop uses stereo + temporal cues.",
        "Phases: math modeling → rendering core → display R&D → interaction/UX → content → ops."
    ]
    summary = engine_language(q, points)

    plan = [
        {"phase": 1, "name": "Modeling & Math", "deliverables": m["requirements"]["math"], "estimate_weeks": "2-3"},
        {"phase": 2, "name": "Rendering Core", "deliverables": ["GPU pipeline","cues: silhouette, color-by-w"], "estimate_weeks": "3-5"},
        {"phase": 3, "name": "Display R&D", "deliverables": ["vendor shortlist","latency/brightness report"], "estimate_weeks": "4-8"},
        {"phase": 4, "name": "Interaction & UX", "deliverables": c["artifacts"], "estimate_weeks": "2-3"},
        {"phase": 5, "name": "Content & Narrative", "deliverables": ["demo tour","tutorials"], "estimate_weeks": "2"},
        {"phase": 6, "name": "Ops & Biz", "deliverables": b["requirements"]["ops"], "estimate_weeks": "1-2"},
    ]

    requirements = {
        "math": m["requirements"]["math"],
        "science": m["requirements"].get("science", []),
        "quantum": m["requirements"].get("quantum", []),
        "software": ["WebGPU/Vulkan/OpenGL renderer","shader stack","stereo/temporal multiplexing"],
        "hardware_optional": ["light-field or volumetric dev kit","VR HMD for stereo demo"],
        "team": b["requirements"]["team"],
        "risks": ["display brightness/resolution","user comprehension"]
    }

    # Citations from grounding (truths + parser hits)
    citations = {
        "truths": grounding.get("truths", []),
        "parser_hits": grounding.get("parser_hits", [])
    }

    # Maybe spawn autonomy tasks
    tasks = maybe_dispatch_tasks(q, payload.captain or "", payload.project or "", payload.dispatch)

    # Proof artifact
    proof = {
        "ts": now_iso(),
        "q": q,
        "intents": intents,
        "subs": steps,
        "engines_used": {
            "math_science": bool(m["notes"]),
            "creativity": bool(c["notes"]),
            "business": bool(b["notes"]),
            "history": bool(h["notes"]),
            "engines_available": ENGINES_AVAILABLE
        },
        "citations_counts": {
            "truths": len(citations["truths"]),
            "parser_hits": len(citations["parser_hits"])
        },
        "tasks_spawned": len(tasks),
    }
    proof["seal"] = sha256_bytes(json.dumps(proof, sort_keys=True).encode())
    write_json(SOLVER_DIR / f"proof_{proof['ts'].replace(':','-')}.json", proof)

    return {
        "summary": summary,
        "plan": plan,
        "requirements": requirements,
        "citations": citations,
        "tasks": tasks,
        "proof": proof
    }
