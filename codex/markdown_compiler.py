import sys
import os
import datetime

# Add parent directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codex.truth_engine import gather_meta, validate_facts  # noqa: E402
from codex.parser_engine import parse_docs  # noqa: E402
from codex.blueprint_engine import build_blueprint  # noqa: E402


def compile_markdown():
    """Compile the repository into a human-readable markdown book."""
    meta = gather_meta()
    truths = validate_facts(meta)
    docs = parse_docs()
    blueprint = build_blueprint()

    lines = []
    lines.append("# 📘 The Book of the Repo\n")
    lines.append(f"_Generated automatically on {datetime.datetime.now(datetime.UTC).isoformat()} UTC_\n")
    lines.append("---\n")

    # ─── Truth Section ───
    lines.append("## 🧠 Truth Engine Summary\n")
    for sig, item in truths.items():
        lines.append(f"- **{item['key']}** → `{item['value']}`  \n  _source: {item['source']}_")

    # ─── Documentation Section ───
    lines.append("\n---\n## 📄 Documentation Index\n")
    for doc in docs:
        lines.append(f"### {doc['file']}\n")
        for h in doc['headers']:
            lines.append(f"- {h}")
        lines.append("\n")

    # ─── Blueprint Section ───
    lines.append("---\n## 🧬 Blueprint Overview\n")
    for mod in blueprint["modules"]:
        lines.append(f"### {mod['file']}")
        for imp in mod["imports"]:
            lines.append(f"  - {imp}")
        lines.append("\n")

    os.makedirs("codex/output", exist_ok=True)
    md_path = "codex/output/repo_book.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"📘 Markdown Book compiled successfully → {md_path}")


if __name__ == "__main__":
    compile_markdown()
