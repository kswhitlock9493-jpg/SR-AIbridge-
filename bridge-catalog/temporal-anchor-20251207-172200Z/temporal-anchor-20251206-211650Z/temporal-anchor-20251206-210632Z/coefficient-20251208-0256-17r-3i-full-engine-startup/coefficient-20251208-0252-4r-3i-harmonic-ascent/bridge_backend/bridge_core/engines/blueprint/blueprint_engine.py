"""
Blueprint Engine - Core planning engine
Deterministic, rules-first blueprinting with extensible LLM integration
"""
from .planner_rules import derive_objectives, explode_tasks
from typing import Dict, Any, List


class BlueprintEngine:
    """
    Deterministic, rules-first blueprinting.
    You can later plug an LLM behind the same interface for smarter planning.
    """
    
    def draft(self, brief: str) -> Dict[str, Any]:
        """
        Create a draft blueprint from a mission brief
        
        Args:
            brief: Free-form mission description
            
        Returns:
            Dictionary with objectives, tasks, artifacts, and success_criteria
        """
        objectives = derive_objectives(brief)
        tasks = explode_tasks(objectives, brief)
        
        plan = {
            "objectives": objectives,
            "tasks": tasks,
            "artifacts": ["report.md", "logs.json"],
            "success_criteria": [
                "All acceptance criteria satisfied",
                "No task failing; critical tasks done"
            ],
        }
        
        return plan
    
    def agent_jobs_from_plan(
        self,
        mission_id: int,
        blueprint_id: int,
        captain: str,
        plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Convert blueprint plan into agent job records
        
        Args:
            mission_id: Associated mission ID
            blueprint_id: Associated blueprint ID
            captain: Captain who owns these jobs
            plan: Blueprint plan dictionary
            
        Returns:
            List of agent job dictionaries ready for database insertion
        """
        jobs = []
        
        for task in plan.get("tasks", []):
            job = {
                "mission_id": mission_id,
                "blueprint_id": blueprint_id,
                "captain": captain,
                "task_key": task["key"],
                "task_desc": f'{task["title"]}: {task["detail"]}',
                "role": task.get("role_hint", "agent"),
                "status": "queued",
                "inputs": {"depends_on": task.get("depends_on", [])},
                "outputs": {}
            }
            jobs.append(job)
        
        return jobs
