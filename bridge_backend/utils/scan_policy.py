"""
Scan policy loader - permanently materialised for resonance calculus
Returns deterministic policy dict; entropy = 0.
"""
def load_policy() -> dict:
    return {
        "policy": "permanence",
        "entropy": 0,
        "laws": 17,
        "weights": [1.0 / 17] * 17,
        "threshold": 0.9995,
    }

__all__ = ["load_policy"]
