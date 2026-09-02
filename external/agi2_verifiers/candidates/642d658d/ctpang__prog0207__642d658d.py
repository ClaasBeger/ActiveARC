"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 642d658d
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[207](id=207)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0207__642d658d
"""
from __future__ import annotations



import numpy as np

import collections

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid:
        return []
    rows = len(grid)
    cols = len(grid[0])
    petal_colors = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 4:
                colors = []
                valid = True
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if not (0 <= nr < rows and 0 <= nc < cols):
                        valid = False
                        break
                    colors.append(grid[nr][nc])
                if valid and all(color == colors[0] for color in colors):
                    petal_colors.append(colors[0])
    if not petal_colors:
        return [[0]]  # Default, though not needed in examples
    counter = collections.Counter(petal_colors)
    most_common = counter.most_common(1)[0][0]
    return [[most_common]]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
