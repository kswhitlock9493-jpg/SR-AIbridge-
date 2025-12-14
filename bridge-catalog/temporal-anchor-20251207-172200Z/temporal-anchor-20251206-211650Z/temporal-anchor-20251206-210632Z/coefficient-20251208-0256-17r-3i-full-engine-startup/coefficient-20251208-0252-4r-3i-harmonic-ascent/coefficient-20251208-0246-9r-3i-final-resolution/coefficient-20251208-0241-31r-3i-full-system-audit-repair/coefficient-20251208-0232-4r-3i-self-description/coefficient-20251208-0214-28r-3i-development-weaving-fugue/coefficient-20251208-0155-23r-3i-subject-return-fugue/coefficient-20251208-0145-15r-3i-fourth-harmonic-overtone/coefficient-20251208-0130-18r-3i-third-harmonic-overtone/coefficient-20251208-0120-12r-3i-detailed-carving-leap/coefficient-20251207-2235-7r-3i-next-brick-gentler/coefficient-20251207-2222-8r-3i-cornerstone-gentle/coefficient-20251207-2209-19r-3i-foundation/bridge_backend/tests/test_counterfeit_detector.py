import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.counterfeit_detector import compare_text

def test_similarity_simple():
    # Test that identical code has high similarity
    a = "def calculate_sum(numbers): return sum(numbers) + len(numbers)"
    b = "def calculate_sum(numbers): return sum(numbers) + len(numbers)"
    assert compare_text(a,b) == 1.0
    
    # Test that very different code has low similarity
    c = "class MyClass: pass"
    assert compare_text(a,c) < 0.2
