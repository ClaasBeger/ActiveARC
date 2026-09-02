"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 73182012
source: GitMonsters/SOLVED-562-verified
original_path: solves/73182012/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__73182012
"""
from __future__ import annotations



def solve(grid):
    """Find bounding box of non-zero cells, extract top-left quadrant."""
    rows = len(grid)
    cols = len(grid[0])
    min_r, max_r = rows, 0
    min_c, max_c = cols, 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                min_r = min(min_r, r)
                max_r = max(max_r, r)
                min_c = min(min_c, c)
                max_c = max(max_c, c)
    h = (max_r - min_r + 1) // 2
    w = (max_c - min_c + 1) // 2
    out = []
    for r in range(min_r, min_r + h):
        out.append([grid[r][c] for c in range(min_c, min_c + w)])
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
