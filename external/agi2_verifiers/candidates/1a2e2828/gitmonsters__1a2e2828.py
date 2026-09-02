"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 1a2e2828
source: GitMonsters/SOLVED-562-verified
original_path: solves/1a2e2828/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__1a2e2828
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """Find the non-zero color that forms a complete uninterrupted line
    (an entire row or column where every cell is that same color).
    The grid has colored "bars" forming a cross-hatch pattern with a
    z-order hierarchy; the topmost bar is never interrupted by others."""
    rows = len(grid)
    cols = len(grid[0])

    for r in range(rows):
        val = grid[r][0]
        if val != 0 and all(grid[r][c] == val for c in range(cols)):
            return [[val]]

    for c in range(cols):
        val = grid[0][c]
        if val != 0 and all(grid[r][c] == val for r in range(rows)):
            return [[val]]

    return [[0]]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
