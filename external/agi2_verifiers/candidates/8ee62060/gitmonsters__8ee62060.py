"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 8ee62060
source: GitMonsters/SOLVED-562-verified
original_path: solves/8ee62060/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__8ee62060
"""
from __future__ import annotations



"""Solver for ARC-AGI task 8ee62060.

Pattern: A small sprite repeats along a diagonal staircase.
The transformation reverses the vertical order of the staircase blocks.
"""

def solve(grid: list[list[int]]) -> list[list[int]]:
    H = len(grid)
    W = len(grid[0])

    # Find the minimum non-zero column per row to detect block boundaries
    def min_nz_col(row):
        for c, v in enumerate(row):
            if v != 0:
                return c
        return -1

    # Detect block height: rows sharing the same min non-zero column region
    first_col = min_nz_col(grid[0])
    block_height = H  # fallback
    for r in range(1, H):
        if min_nz_col(grid[r]) != first_col:
            block_height = r
            break

    # Reverse the order of blocks
    num_blocks = H // block_height
    result = [[0] * W for _ in range(H)]
    for i in range(num_blocks):
        src_start = i * block_height
        dst_start = (num_blocks - 1 - i) * block_height
        for j in range(block_height):
            result[dst_start + j] = list(grid[src_start + j])

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
