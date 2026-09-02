"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ad7e01d0
source: GitMonsters/SOLVED-562-verified
original_path: solves/ad7e01d0/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__ad7e01d0
"""
from __future__ import annotations



"""
Solver for ARC task ad7e01d0.

The input is an NxN grid containing the value 5 and other values.
The output is an N*N x N*N grid composed of NxN blocks: each block (br, bc)
is a copy of the original grid if input[br][bc] == 5, otherwise all zeros.
"""

import json
from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    N = len(grid)
    size = N * N
    out = [[0] * size for _ in range(size)]

    for br in range(N):
        for bc in range(N):
            if grid[br][bc] == 5:
                for r in range(N):
                    for c in range(N):
                        out[br * N + r][bc * N + c] = grid[r][c]
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
