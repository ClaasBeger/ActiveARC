"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 5b6cbef5
source: GitMonsters/SOLVED-562-verified
original_path: solves/5b6cbef5/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__5b6cbef5
"""
from __future__ import annotations



def solve(grid):
    """Fractal self-similar tiling: 4x4 → 16x16. Each non-zero cell → input pattern, zero → all zeros."""
    N = len(grid)
    out = [[0] * (N * N) for _ in range(N * N)]
    for br in range(N):
        for bc in range(N):
            if grid[br][bc] != 0:
                for r in range(N):
                    for c in range(N):
                        out[br * N + r][bc * N + c] = grid[r][c]
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
