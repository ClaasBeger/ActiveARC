"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 762cd429
source: GitMonsters/SOLVED-562-verified
original_path: solves/762cd429/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__762cd429
"""
from __future__ import annotations



"""
Solver for ARC-AGI task 762cd429.

Pattern: A 2x2 seed [[a,b],[c,d]] expands in a staircase fractal.
Each column group k has width 2^(k+1), starting at column 2^(k+1)-2.
Within group k, the seed is scaled by 2^k: each value becomes a 2^k × 2^k block,
arranged as [[a_block, b_block], [c_block, d_block]].
The top half extends upward from the seed row, the bottom half extends downward.
"""

import json
from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    rows = len(grid)
    cols = len(grid[0])

    # Find the 2x2 seed (first non-zero cell is top-left)
    seed_r = seed_c = -1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                seed_r, seed_c = r, c
                break
        if seed_r >= 0:
            break

    a, b = grid[seed_r][seed_c], grid[seed_r][seed_c + 1]
    c, d = grid[seed_r + 1][seed_c], grid[seed_r + 1][seed_c + 1]

    out = [[0] * cols for _ in range(rows)]

    col_start = seed_c
    k = 0
    while col_start < cols:
        half = 1 << k        # 2^k
        width = half << 1     # 2^(k+1)

        for dr in range(half):
            tr = seed_r - half + 1 + dr   # top half row
            br = seed_r + 1 + dr          # bottom half row

            for dc in range(width):
                col = col_start + dc
                if col >= cols:
                    break
                val_top = a if dc < half else b
                val_bot = c if dc < half else d

                if 0 <= tr < rows:
                    out[tr][col] = val_top
                if 0 <= br < rows:
                    out[br][col] = val_bot

        col_start += width
        k += 1

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
