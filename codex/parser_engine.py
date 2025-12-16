import os
import re


def parse_docs():
    """Parse all markdown files and extract headers and content."""
    docs = []
    for root, _, files in os.walk("."):
        # Skip .git and node_modules directories
        if ".git" in root or "node_modules" in root:
            continue
        for f in files:
            if f.endswith(".md"):
                path = os.path.join(root, f)
                with open(path, encoding="utf-8") as fp:
                    content = fp.read()
                    headers = re.findall(r"^#+ .+", content, flags=re.M)
                    docs.append({
                        "file": path,
                        "headers": headers,
                        "content": content
                    })
    return docs
