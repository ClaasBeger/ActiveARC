"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e5c44e8f
source: GitMonsters/SOLVED-562-verified
original_path: solves/e5c44e8f/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__e5c44e8f
"""
from __future__ import annotations



"""
Solver for ARC-AGI puzzle e5c44e8f.

Pattern: A rectangular spiral emanates from a center cell (value 3).
- Directions cycle: Up, Right, Down, Left
- Segment lengths: 2, 2, 4, 4, 6, 6, 8, 8, 10, 10, ...
  (each length used for 2 consecutive segments, then +2)
- Cells with value 2 are obstacles: hitting one stops the entire spiral.
- Off-grid cells are skipped but the spiral continues with virtual position tracking.
"""

import json
from pathlib import Path


def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])

    # Find the center cell (value 3)
    cr, cc = -1, -1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 3:
                cr, cc = r, c
                break
        if cr != -1:
            break

    out = [row[:] for row in grid]

    # Spiral directions: Up, Right, Down, Left
    dirs = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    pr, pc = cr, cc  # virtual cursor position
    dir_idx = 0
    length = 2
    stopped = False

    while length <= 100 and not stopped:
        for _ in range(2):  # two segments share the same length
            dr, dc = dirs[dir_idx % 4]
            for _ in range(length):
                pr += dr
                pc += dc
                if 0 <= pr < rows and 0 <= pc < cols:
                    if grid[pr][pc] == 2:
                        stopped = True
                        break
                    out[pr][pc] = 3
            if stopped:
                break
            dir_idx += 1
        length += 2

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
