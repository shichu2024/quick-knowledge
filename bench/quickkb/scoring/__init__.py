"""Scoring package — hard/soft score producers for quickkb cases.

Each scorer returns ``(hard, soft)``:
- ``hard``: 0.0 or 1.0 — fully correct or not
- ``soft``: float in [0, 1] — partial credit so optimizer always has gradient

Final case score = AND of all applicable scorers' hard values, mean of soft.
"""
from .routing import score as score_routing
from .frontmatter import score as score_frontmatter
from .behavior import score as score_behavior
from .flow import score as score_flow

__all__ = [
    "score_routing",
    "score_frontmatter",
    "score_behavior",
    "score_flow",
    "aggregate",
]


def aggregate(results: list[tuple[float, float]]) -> tuple[float, float]:
    """Aggregate multiple (hard, soft) into one.

    hard: AND (all must pass); soft: arithmetic mean.
    """
    if not results:
        return (1.0, 1.0)  # no scorers applied = vacuously true
    hard = 1.0 if all(h >= 1.0 for h, _ in results) else 0.0
    soft = sum(s for _, s in results) / len(results)
    return (hard, soft)
