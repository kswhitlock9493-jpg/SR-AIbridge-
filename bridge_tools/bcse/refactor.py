"""BCSE Code Refactoring Module

Safe AST transforms + simple improvements (auto-fix available).
"""
import ast
import pathlib
from typing import List


class StripDebug(ast.NodeTransformer):
    """Remove print() calls in production but keep logging.* calls"""
    
    def visit_Call(self, node: ast.Call):
        try:
            if getattr(node.func, "id", "") == "print":
                # Replace with None expression
                return ast.parse("None").body[0].value
        except Exception:
            pass
        return self.generic_visit(node)


class InlineSimpleConstants(ast.NodeTransformer):
    """Replace DEBUG/SAFE_MODE flags with False in prod builds"""
    
    def visit_Assign(self, node: ast.Assign):
        try:
            for t in node.targets:
                if getattr(t, "id", "") in {"DEBUG", "SAFE_MODE", "ENABLE_SAFE_PLACEHOLDER"}:
                    # Replace with False assignment
                    return ast.parse(f"{t.id} = False").body[0]
        except Exception:
            pass
        return node


# List of transforms to apply
TRANSFORMS = [StripDebug, InlineSimpleConstants]


def improve_file(p: pathlib.Path) -> bool:
    """
    Apply AST transforms to improve a single file
    
    Args:
        p: Path to Python file
        
    Returns:
        True if file was modified, False otherwise
    """
    try:
        src = p.read_text(encoding="utf-8")
        tree = ast.parse(src)
        
        # Apply all transforms
        for T in TRANSFORMS:
            tree = T().visit(tree) or tree
            
        ast.fix_missing_locations(tree)
        new = ast.unparse(tree)
        
        if new != src:
            p.write_text(new, encoding="utf-8")
            return True
    except Exception as e:
        # Skip files with syntax errors or other issues
        return False
        
    return False


def improve(paths: List[str]) -> int:
    """
    Improve code in all Python files under given paths
    
    Args:
        paths: List of directories to scan
        
    Returns:
        Exit code (0 = success)
    """
    changed = 0
    for root in paths:
        root_path = pathlib.Path(root)
        if not root_path.exists():
            continue
            
        for p in root_path.rglob("*.py"):
            # Skip common directories
            if any(part in p.parts for part in ['.git', 'node_modules', 'venv', '.venv', '__pycache__', 'dist', 'build']):
                continue
                
            if improve_file(p):
                changed += 1
                print(f"🔧 Improved: {p}")
                
    print(f"BCSE refactor: {changed} file(s) improved")
    return 0
