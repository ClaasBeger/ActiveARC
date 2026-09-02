"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9356391f
source: GitMonsters/SOLVED-562-verified
original_path: solves/9356391f/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__9356391f
"""
from __future__ import annotations



"""Solver for ARC-AGI task 9356391f.

Pattern: Row 0 contains a color legend (innermost→outermost ring colors).
Row 1 is a separator of 5s. Below that, a single colored pixel marks the center.
Output draws concentric square rings (Chebyshev distance) around the center,
colored by the legend sequence.
"""

import json
from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    rows, cols = len(grid), len(grid[0])
    out = [row[:] for row in grid]

    # Extract legend from row 0: values from index 0 to last non-zero index
    last_nz = -1
    for i in range(cols - 1, -1, -1):
        if grid[0][i] != 0:
            last_nz = i
            break
    legend = list(grid[0][: last_nz + 1]) if last_nz >= 0 else []

    # Find the single non-zero pixel below row 1 (the center)
    cr, cc = -1, -1
    for r in range(2, rows):
        for c in range(cols):
            if grid[r][c] != 0:
                cr, cc = r, c
                break
        if cr >= 0:
            break

    # Draw concentric Chebyshev-distance rings below row 1
    for r in range(2, rows):
        for c in range(cols):
            dist = max(abs(r - cr), abs(c - cc))
            if dist < len(legend):
                out[r][c] = legend[dist]
            else:
                out[r][c] = 0

    # Row 0 fix: replace isolated single non-zero values (size-1 groups) with 5
    i = 0
    while i <= last_nz:
        if grid[0][i] != 0:
            start = i
            while i <= last_nz and grid[0][i] != 0:
                i += 1
            if i - start == 1:  # single isolated value
                out[0][start] = 5
        else:
            i += 1

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
