"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 21f83797
source: GitMonsters/SOLVED-562-verified
original_path: solves/21f83797/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__21f83797
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    # Find the two 2-pixels
    pts = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 2]
    (r1, c1), (r2, c2) = pts[0], pts[1]
    rmin, rmax = min(r1, r2), max(r1, r2)
    cmin, cmax = min(c1, c2), max(c1, c2)

    result = [[0]*cols for _ in range(rows)]
    # Draw full cross lines with 2
    for r in range(rows):
        result[r][c1] = 2
        result[r][c2] = 2
    for c in range(cols):
        result[r1][c] = 2
        result[r2][c] = 2
    # Fill interior rectangle with 1
    for r in range(rmin+1, rmax):
        for c in range(cmin+1, cmax):
            result[r][c] = 1
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
