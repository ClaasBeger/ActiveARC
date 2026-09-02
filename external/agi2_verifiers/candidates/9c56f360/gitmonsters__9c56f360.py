"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9c56f360
source: GitMonsters/SOLVED-562-verified
original_path: solves/9c56f360/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__9c56f360
"""
from __future__ import annotations



def solve(grid):
    """Each row's contiguous block of 3s slides left until hitting an 8 or the edge."""
    rows = len(grid)
    cols = len(grid[0])
    out = [row[:] for row in grid]

    for r in range(rows):
        # Find contiguous 3s in this row
        threes = [c for c in range(cols) if grid[r][c] == 3]
        if not threes:
            continue
        min_c = min(threes)
        count = len(threes)

        # Clear original 3 positions
        for c in threes:
            out[r][c] = 0

        # Find leftmost position: slide left from min_c until hitting 8 or edge
        # The block occupies [new_start, new_start+count-1]
        new_start = min_c
        while new_start > 0 and out[r][new_start - 1] != 8:
            new_start -= 1

        for i in range(count):
            out[r][new_start + i] = 3

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
