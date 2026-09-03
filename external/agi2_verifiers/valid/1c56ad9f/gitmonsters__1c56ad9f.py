"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 1c56ad9f
source: GitMonsters/SOLVED-562-verified
original_path: solves/1c56ad9f/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__1c56ad9f
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])

    # Find vertical bounding box of non-zero cells
    min_r, max_r = rows, -1
    for r in range(rows):
        if any(grid[r][c] != 0 for c in range(cols)):
            if r < min_r: min_r = r
            max_r = r

    n = max_r - min_r + 1  # shape height
    # Zigzag cycle: 0, -1, 0, +1  with start phase chosen so last row offset = 0
    start = (3 - n) % 4
    cycle = [0, -1, 0, 1]

    result = [[0] * cols for _ in range(rows)]
    for r in range(min_r, max_r + 1):
        offset = cycle[(r - min_r + start) % 4]
        for c in range(cols):
            if grid[r][c] != 0:
                nc = c + offset
                if 0 <= nc < cols:
                    result[r][nc] = grid[r][c]
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
