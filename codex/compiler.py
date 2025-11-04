import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from codex.truth_engine import gather_meta, validate_facts
from codex.parser_engine import parse_docs
from codex.blueprint_engine import build_blueprint
import json


def compile_codex():
    """Compile the entire repository into a unified codex."""
    truth = validate_facts(gather_meta())
    docs = parse_docs()
    blueprint = build_blueprint()

    book = {
        "truth": truth,
        "documentation": docs,
        "blueprint": blueprint
    }

    os.makedirs("codex/output", exist_ok=True)
    with open("codex/output/repo_book.json", "w", encoding="utf-8") as f:
        json.dump(book, f, indent=2)

    print("📘 Repo Codex compiled successfully → codex/output/repo_book.json")


if __name__ == "__main__":
    compile_codex()
