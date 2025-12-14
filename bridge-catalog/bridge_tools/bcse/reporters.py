"""BCSE Reporters - SARIF, JUnit, and Markdown Output"""
import json
import os
from typing import List, Dict, Any


def write_sarif(sarif_obj: Dict[str, Any], path: str = "bcse.sarif") -> None:
    """
    Write SARIF report for GitHub Security
    
    Args:
        sarif_obj: SARIF format object
        path: Output file path
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sarif_obj, f, indent=2)


def pr_summary(markdown_items: List[Dict[str, str]], outfile: str = "bcse_summary.md") -> None:
    """
    Generate PR summary markdown from template
    
    Args:
        markdown_items: List of items with 'name' and 'status' keys
        outfile: Output markdown file path
    """
    tpl_path = "bridge_tools/bcse/templates/pr_summary.md.j2"
    
    if not os.path.exists(tpl_path):
        # Fallback to simple markdown if template doesn't exist
        with open(outfile, "w", encoding="utf-8") as out:
            out.write("# 🜂 Bridge Code Super-Engine (BCSE) Report\n\n")
            for item in markdown_items:
                status_icon = "✅" if item["status"] == "OK" else "❌"
                out.write(f"{status_icon} **{item['name']}**: {item['status']}\n")
        return
    
    try:
        from jinja2 import Template
        with open(tpl_path, "r", encoding="utf-8") as f:
            tpl = Template(f.read())
        with open(outfile, "w", encoding="utf-8") as out:
            out.write(tpl.render(items=markdown_items))
    except ImportError:
        # Fallback if jinja2 not available
        with open(outfile, "w", encoding="utf-8") as out:
            out.write("# 🜂 Bridge Code Super-Engine (BCSE) Report\n\n")
            for item in markdown_items:
                status_icon = "✅" if item["status"] == "OK" else "❌"
                out.write(f"{status_icon} **{item['name']}**: {item['status']}\n")
