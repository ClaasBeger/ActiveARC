"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: aa18de87
source: GitMonsters/SOLVED-562-verified
original_path: solves/aa18de87/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__aa18de87
"""
from __future__ import annotations



def solve(grid):
    """Fill interior of V/triangle shapes (between colored arms) with color 2."""
    rows = len(grid)
    cols = len(grid[0])
    result = [row[:] for row in grid]
    for r in range(rows):
        colored_cols = [c for c in range(cols) if grid[r][c] != 0]
        if len(colored_cols) >= 2:
            lo, hi = min(colored_cols), max(colored_cols)
            for c in range(lo + 1, hi):
                if result[r][c] == 0:
                    result[r][c] = 2
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
