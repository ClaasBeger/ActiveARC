"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 6ea4a07e
source: GitMonsters/SOLVED-562-verified
original_path: solves/6ea4a07e/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__6ea4a07e
"""
from __future__ import annotations



def solve(grid):
    # Rule: invert 0/non-zero pattern, map color: 8->2, 3->1, 5->4
    color_map = {8: 2, 3: 1, 5: 4}
    rows, cols = len(grid), len(grid[0])
    # Find the non-zero color in the grid
    color = None
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                color = grid[r][c]
                break
        if color is not None:
            break
    new_color = color_map[color]
    return [[new_color if grid[r][c] == 0 else 0 for c in range(cols)] for r in range(rows)]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
