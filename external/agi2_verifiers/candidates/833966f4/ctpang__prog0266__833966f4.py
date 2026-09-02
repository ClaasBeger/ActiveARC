"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 833966f4
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[266](id=266)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0266__833966f4
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return []
    # Assume 5x1 grid based on examples
    colors = [row[0] for row in grid]
    # Swap first and second
    colors[0], colors[1] = colors[1], colors[0]
    # Swap fourth and fifth
    colors[3], colors[4] = colors[4], colors[3]
    return [[c] for c in colors]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
