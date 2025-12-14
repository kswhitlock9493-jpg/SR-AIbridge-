"""
Planner Rules - Deterministic blueprint planning logic
Derives objectives and explodes them into executable tasks
"""
from typing import List, Dict


def derive_objectives(brief: str) -> List[str]:
    """
    Derive high-level objectives from mission brief
    Ultra-simple ruleset; extend as needed with more sophisticated logic
    
    Args:
        brief: Mission brief text
        
    Returns:
        List of objective strings
    """
    # Base objectives for any mission
    base = [
        "Clarify requirements",
        "Collect sources/data",
        "Produce deliverable"
    ]
    
    # Context-specific objectives based on brief keywords
    brief_lower = brief.lower()
    
    if "marketing" in brief_lower or "campaign" in brief_lower:
        base.append("Create distribution plan")
    
    if "analysis" in brief_lower or "research" in brief_lower:
        base.append("Analyze findings and generate insights")
    
    if "deploy" in brief_lower or "launch" in brief_lower:
        base.append("Execute deployment and verify")
    
    if "test" in brief_lower or "qa" in brief_lower:
        base.append("Run validation and quality checks")
    
    return base


def explode_tasks(objectives: List[str], brief: str) -> List[Dict]:
    """
    Explode objectives into concrete, executable tasks
    
    Args:
        objectives: List of high-level objectives
        brief: Original mission brief for context
        
    Returns:
        List of task dictionaries with keys: key, title, detail, depends_on, acceptance
    """
    tasks = []
    idx = 1
    
    for objective in objectives:
        task = {
            "key": f"T{idx}",
            "title": objective,
            "detail": f"Execute objective: {objective} — context: {brief[:140]}",
            "depends_on": [] if idx == 1 else [f"T{idx-1}"],
            "role_hint": "agent",
            "acceptance": [
                "Document steps taken",
                "Record logs and outputs",
                "Attach relevant artifacts"
            ]
        }
        tasks.append(task)
        idx += 1
    
    return tasks
