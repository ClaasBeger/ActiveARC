"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 48f8583b
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[146](id=146)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0146__48f8583b
"""
from __future__ import annotations



import numpy as np

from collections import Counter

def transform(grid: list[list[int]]) -> list[list[int]]:
    # Assume grid is 3x3
    colors = [grid[i][j] for i in range(3) for j in range(3)]
    freq = Counter(colors)
    if not freq:
        return [[0] * 9 for _ in range(9)]
    min_count = min(freq.values())
    candidates = [col for col, cnt in freq.items() if cnt == min_count]
    c = min(candidates)  # Smallest color if tie
    positions = [(i, j) for i in range(3) for j in range(3) if grid[i][j] == c]
    large = [[0] * 9 for _ in range(9)]
    for pi, pj in positions:
        for di in range(3):
            for dj in range(3):
                large[3 * pi + di][3 * pj + dj] = grid[di][dj]
    return large

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
