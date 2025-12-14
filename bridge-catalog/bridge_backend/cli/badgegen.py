#!/usr/bin/env python3
"""
Bridge Health Badge Generator
Generates Shields.io-compatible SVG and Markdown badges
"""

import click
import json
import sys
from pathlib import Path
from typing import Dict, Any


def load_health_record(filepath: str) -> Dict[str, Any]:
    """Load health record JSON"""
    try:
        path = Path(filepath)
        if not path.exists():
            print(f"❌ Health record not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load health record: {e}", file=sys.stderr)
        sys.exit(1)


def determine_badge_color(health_score: int) -> str:
    """
    Determine badge color based on health score
    
    Rules:
    - >= 95% → green (passing)
    - 80-94% → yellow (warning)
    - < 80% → red (critical)
    """
    if health_score >= 95:
        return "brightgreen"
    elif health_score >= 80:
        return "yellow"
    else:
        return "red"


def generate_svg_badge(record: Dict[str, Any]) -> str:
    """
    Generate Shields.io-compatible SVG badge
    """
    health_score = record["bridge_health_score"]
    truth_certified = record["truth_certified"]
    color = determine_badge_color(health_score)
    
    # Badge message
    if truth_certified:
        message = f"{health_score}% (Truth Certified)"
    else:
        message = f"{health_score}% (Not Certified)"
    
    # SVG template for shields.io static badge
    # Using simple rectangular badge design
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="234" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="a">
    <rect width="234" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#a)">
    <path fill="#555" d="M0 0h95v20H0z"/>
    <path fill="#{get_color_hex(color)}" d="M95 0h139v20H95z"/>
    <path fill="url(#b)" d="M0 0h234v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110">
    <text x="485" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="850">Bridge Health</text>
    <text x="485" y="140" transform="scale(.1)" textLength="850">Bridge Health</text>
    <text x="1635" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="1290">{message}</text>
    <text x="1635" y="140" transform="scale(.1)" textLength="1290">{message}</text>
  </g>
</svg>'''
    
    return svg


def get_color_hex(color_name: str) -> str:
    """Convert color name to hex"""
    color_map = {
        "brightgreen": "4c1",
        "green": "97CA00",
        "yellow": "dfb317",
        "yellowgreen": "a4a61d",
        "orange": "fe7d37",
        "red": "e05d44",
        "blue": "007ec6",
        "grey": "555",
        "gray": "555",
        "lightgrey": "9f9f9f",
        "lightgray": "9f9f9f"
    }
    return color_map.get(color_name, "9f9f9f")


def generate_markdown_badge(record: Dict[str, Any], svg_path: str) -> str:
    """
    Generate Markdown badge reference
    """
    health_score = record["bridge_health_score"]
    truth_certified = record["truth_certified"]
    status = record["status"]
    
    # Badge emoji based on status
    if status == "passing":
        emoji = "🟢"
    elif status == "warning":
        emoji = "🟡"
    else:
        emoji = "🔴"
    
    # Generate markdown
    md = f"# {emoji} Bridge Health Badge\n\n"
    md += f"![Bridge Health]({svg_path})\n\n"
    md += f"**Current Status:** {status.upper()}\n\n"
    md += f"- **Health Score:** {health_score}%\n"
    md += f"- **Truth Certified:** {'✅ Yes' if truth_certified else '❌ No'}\n"
    md += f"- **Auto-Heals:** {record['auto_heals']}\n"
    md += f"- **Last Updated:** {record['timestamp']}\n\n"
    md += "## Integration\n\n"
    md += "Add this badge to your README:\n\n"
    md += f"```markdown\n"
    md += f"![Bridge Health]({svg_path})\n"
    md += f"```\n"
    
    return md


@click.command()
@click.option("--input", required=True, help="Path to health record JSON")
@click.option("--out-md", required=True, help="Output path for markdown badge")
@click.option("--out-svg", required=True, help="Output path for SVG badge")
def main(input: str, out_md: str, out_svg: str):
    """
    Generate Bridge Health badge from health record
    Outputs SVG and Markdown files
    """
    try:
        print("🎨 Generating Bridge Health Badge...")
        
        # Load health record
        health_record = load_health_record(input)
        
        # Generate SVG badge
        svg_content = generate_svg_badge(health_record)
        
        # Generate Markdown badge
        md_content = generate_markdown_badge(health_record, out_svg)
        
        # Ensure output directories exist
        Path(out_svg).parent.mkdir(parents=True, exist_ok=True)
        Path(out_md).parent.mkdir(parents=True, exist_ok=True)
        
        # Write SVG
        with open(out_svg, 'w') as f:
            f.write(svg_content)
        print(f"✅ SVG badge: {out_svg}")
        
        # Write Markdown
        with open(out_md, 'w') as f:
            f.write(md_content)
        print(f"✅ Markdown: {out_md}")
        
        # Display summary
        print(f"\n📊 Badge Summary:")
        print(f"   Score: {health_record['bridge_health_score']}%")
        print(f"   Color: {determine_badge_color(health_record['bridge_health_score'])}")
        print(f"   Status: {health_record['status']}")
        
    except Exception as e:
        print(f"❌ Failed to generate badge: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
