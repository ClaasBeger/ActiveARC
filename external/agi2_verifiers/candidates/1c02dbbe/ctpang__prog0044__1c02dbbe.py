"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 1c02dbbe
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[44](id=44)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0044__1c02dbbe
"""
from __future__ import annotations



import numpy as np

from collections import defaultdict

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid

    height = len(grid)
    width = len(grid[0])

    # Copy grid
    output = [row[:] for row in grid]

    # Set all seeds to 0
    for r in range(height):
        for c in range(width):
            if output[r][c] != 0 and output[r][c] != 5:
                output[r][c] = 0

    # Group seeds by color
    groups = defaultdict(list)
    for r in range(height):
        for c in range(width):
            val = grid[r][c]
            if val != 0 and val != 5:
                groups[val].append((r, c))

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for color, poss in groups.items():
        entry_points = set()
        for r, c in poss:
            for dr, dc in directions:
                nr = r + dr
                nc = c + dc
                if 0 <= nr < height and 0 <= nc < width and grid[nr][nc] == 5:
                    entry_points.add((nr, nc))

        if not entry_points:
            continue

        min_r = min(x[0] for x in entry_points)
        max_r = max(x[0] for x in entry_points)
        min_c = min(x[1] for x in entry_points)
        max_c = max(x[1] for x in entry_points)

        for fr in range(min_r, max_r + 1):
            for fc in range(min_c, max_c + 1):
                output[fr][fc] = color

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
