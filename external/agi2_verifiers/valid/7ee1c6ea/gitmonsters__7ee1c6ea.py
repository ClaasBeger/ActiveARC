"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7ee1c6ea
source: GitMonsters/SOLVED-562-verified
original_path: solves/7ee1c6ea/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__7ee1c6ea
"""
from __future__ import annotations



"""
Task 7ee1c6ea: Inside a 5-bordered rectangle, swap the two non-zero colors.
Everything outside the rectangle is unchanged.
"""
import json


def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    output = [row[:] for row in grid]

    # Locate the 5-bordered rectangle
    five_cells = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 5]
    min_r = min(r for r, c in five_cells)
    max_r = max(r for r, c in five_cells)
    min_c = min(c for r, c in five_cells)
    max_c = max(c for r, c in five_cells)

    # Identify the two non-zero, non-5 colors inside the rectangle
    interior_colors: set[int] = set()
    for r in range(min_r + 1, max_r):
        for c in range(min_c + 1, max_c):
            v = grid[r][c]
            if v != 0 and v != 5:
                interior_colors.add(v)

    if len(interior_colors) == 2:
        a, b = sorted(interior_colors)
        swap = {a: b, b: a}
        for r in range(min_r + 1, max_r):
            for c in range(min_c + 1, max_c):
                if grid[r][c] in swap:
                    output[r][c] = swap[grid[r][c]]

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
