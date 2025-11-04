import os


def build_blueprint():
    """Build dependency blueprint from Python and JavaScript files."""
    blueprint = {"modules": [], "relations": []}
    for root, _, files in os.walk("."):
        # Skip .git, node_modules, and __pycache__ directories
        if ".git" in root or "node_modules" in root or "__pycache__" in root:
            continue
        for f in files:
            if f.endswith((".py", ".js")):
                filepath = os.path.join(root, f)
                try:
                    with open(filepath, encoding="utf-8") as fp:
                        lines = fp.readlines()
                    imports = [line.strip() for line in lines if "import " in line or "from " in line]
                    blueprint["modules"].append({"file": filepath, "imports": imports})
                except Exception:
                    # Skip files that can't be read
                    pass
    return blueprint
