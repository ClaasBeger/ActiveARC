"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 90347967
source: GitMonsters/SOLVED-562-verified
original_path: solves/90347967/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__90347967
"""
from __future__ import annotations



def solve(grid):
    # Rotate all non-zero cells 180 degrees about the cell with value 5.
    # Original cells become 0, rotated cells take their place.
    rows, cols = len(grid), len(grid[0])
    result = [[0] * cols for _ in range(rows)]

    # Find the cell with value 5 (center of rotation)
    cr, cc = None, None
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 5:
                cr, cc = r, c
                break
        if cr is not None:
            break

    # Rotate each non-zero cell 180 about (cr, cc)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                nr, nc = 2 * cr - r, 2 * cc - c
                if 0 <= nr < rows and 0 <= nc < cols:
                    result[nr][nc] = grid[r][c]

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
