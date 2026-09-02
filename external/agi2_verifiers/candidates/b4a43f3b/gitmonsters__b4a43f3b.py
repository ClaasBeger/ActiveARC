"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: b4a43f3b
source: GitMonsters/SOLVED-562-verified
original_path: solves/b4a43f3b/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__b4a43f3b
"""
from __future__ import annotations



"""
Solver for ARC-AGI puzzle b4a43f3b

Rule:
  Input is split by a row of 5s into two 6×6 grids.
  - Top grid: 3×3 arrangement of 2×2 color blocks → a 3×3 "stamp" palette.
  - Bottom grid: template where 2s mark positions on a 6×6 canvas.
  - Output is 18×18 (each template cell → 3×3 output block).
  - For every template cell == 2, stamp the 3×3 palette into the output.
"""

import json
from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    # Find the separator row (all 5s)
    sep = next(r for r, row in enumerate(grid) if all(v == 5 for v in row))

    # Extract 3×3 palette from the top 6×6 (2×2 blocks → single cells)
    palette = [[grid[r * 2][c * 2] for c in range(3)] for r in range(3)]

    # Extract 6×6 template from below the separator
    template = [grid[sep + 1 + r] for r in range(6)]

    # Build 18×18 output
    out = [[0] * 18 for _ in range(18)]
    for tr in range(6):
        for tc in range(6):
            if template[tr][tc] == 2:
                for pr in range(3):
                    for pc in range(3):
                        out[tr * 3 + pr][tc * 3 + pc] = palette[pr][pc]
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
