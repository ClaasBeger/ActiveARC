"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: f0df5ff0
source: GitMonsters/SOLVED-562-verified
original_path: solves/f0df5ff0/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__f0df5ff0
"""
from __future__ import annotations



def solve(grid):
    rows = len(grid)
    cols = len(grid[0])
    out = [row[:] for row in grid]

    # For each cell with value 1, fill 0s in 3x3 neighborhood with 1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                            out[nr][nc] = 1

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
