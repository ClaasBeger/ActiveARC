"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 22a4bbc2
source: GitMonsters/SOLVED-562-verified
original_path: solves/22a4bbc2/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__22a4bbc2
"""
from __future__ import annotations



def solve(grid):
    """Group consecutive identical rows into blocks. Every 3rd block (1st, 4th, 7th...)
    has its non-zero values replaced with 2."""
    rows = len(grid)
    out = [row[:] for row in grid]

    # Group consecutive identical rows into blocks
    blocks = []  # list of (start_row, end_row) inclusive
    i = 0
    while i < rows:
        j = i + 1
        while j < rows and grid[j] == grid[i]:
            j += 1
        blocks.append((i, j - 1))
        i = j

    # Every block at index 0, 3, 6, 9... gets changed
    for idx, (start, end) in enumerate(blocks):
        if idx % 3 == 0:
            for r in range(start, end + 1):
                for c in range(len(grid[r])):
                    if out[r][c] != 0:
                        out[r][c] = 2

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
