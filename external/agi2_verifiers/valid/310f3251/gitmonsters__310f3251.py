"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 310f3251
source: GitMonsters/SOLVED-562-verified
original_path: solves/310f3251/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__310f3251
"""
from __future__ import annotations



"""
Solver for ARC task 310f3251.

For each non-zero cell at (r,c) in the N×N input, place a 2 at the
diagonally shifted position ((r-1)%N, (c-1)%N) if that cell is empty.
Then tile the modified grid 3×3 to produce the output.
"""
import json


def solve(grid: list[list[int]]) -> list[list[int]]:
    n = len(grid)
    tile = [row[:] for row in grid]

    for r in range(n):
        for c in range(n):
            if grid[r][c] != 0:
                sr, sc = (r - 1) % n, (c - 1) % n
                if tile[sr][sc] == 0:
                    tile[sr][sc] = 2

    # Tile 3×3
    out_size = n * 3
    return [[tile[r % n][c % n] for c in range(out_size)] for r in range(out_size)]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
