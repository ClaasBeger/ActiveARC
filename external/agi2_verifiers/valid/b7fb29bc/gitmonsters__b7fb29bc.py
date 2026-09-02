"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: b7fb29bc
source: GitMonsters/SOLVED-562-verified
original_path: solves/b7fb29bc/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__b7fb29bc
"""
from __future__ import annotations



"""
Solver for ARC-AGI puzzle b7fb29bc.

Rule: A green (3) rectangle has one extra green pixel inside its interior.
Fill the interior with concentric Chebyshev-distance rings from that pixel:
  - distance 0: keep as 3
  - odd distance (1,3,5,...): yellow (4)
  - even distance (2,4,6,...): red (2)
"""

import json
import copy
from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    grid = copy.deepcopy(grid)
    rows, cols = len(grid), len(grid[0])

    # Find all green (3) cells
    green_cells = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 3]

    # Determine the bounding rectangle of the green border
    min_r = min(r for r, c in green_cells)
    max_r = max(r for r, c in green_cells)
    min_c = min(c for r, c in green_cells)
    max_c = max(c for r, c in green_cells)

    # Interior region
    int_r0, int_r1 = min_r + 1, max_r - 1
    int_c0, int_c1 = min_c + 1, max_c - 1

    # Find the extra green pixel strictly inside the border
    marker = None
    for r, c in green_cells:
        if int_r0 <= r <= int_r1 and int_c0 <= c <= int_c1:
            marker = (r, c)
            break

    assert marker is not None, "No interior marker found"
    mr, mc = marker

    # Fill interior cells based on Chebyshev distance from marker
    for r in range(int_r0, int_r1 + 1):
        for c in range(int_c0, int_c1 + 1):
            dist = max(abs(r - mr), abs(c - mc))
            if dist == 0:
                grid[r][c] = 3
            elif dist % 2 == 1:
                grid[r][c] = 4
            else:
                grid[r][c] = 2

    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
