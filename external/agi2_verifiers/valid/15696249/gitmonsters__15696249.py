"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 15696249
source: GitMonsters/SOLVED-562-verified
original_path: solves/15696249/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__15696249
"""
from __future__ import annotations



"""
15696249 solver

Rule:
1. Input is a 3x3 grid.
2. Find the row or column where all 3 values are identical.
3. That row/column index determines placement in a 9x9 output grid
   (a 3x3 meta-grid of 3x3 tiles).
4. If a ROW is uniform: tile the input 3x across that meta-row (horizontally).
5. If a COLUMN is uniform: tile the input 3x down that meta-column (vertically).
6. All other cells are 0.
"""
from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    out = [[0] * 9 for _ in range(9)]

    # Check rows for uniformity
    for r in range(3):
        if grid[r][0] == grid[r][1] == grid[r][2]:
            # Tile horizontally in meta-row r
            for meta_c in range(3):
                for dr in range(3):
                    for dc in range(3):
                        out[r * 3 + dr][meta_c * 3 + dc] = grid[dr][dc]
            return out

    # Check columns for uniformity
    for c in range(3):
        if grid[0][c] == grid[1][c] == grid[2][c]:
            # Tile vertically in meta-column c
            for meta_r in range(3):
                for dr in range(3):
                    for dc in range(3):
                        out[meta_r * 3 + dr][c * 3 + dc] = grid[dr][dc]
            return out

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
