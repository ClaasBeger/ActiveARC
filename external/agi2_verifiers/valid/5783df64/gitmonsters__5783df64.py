"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 5783df64
source: GitMonsters/SOLVED-562-verified
original_path: solves/5783df64/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__5783df64
"""
from __future__ import annotations



def solve(grid):
    """Divide grid into 3x3 blocks, extract the single non-zero value from each."""
    R, C = len(grid), len(grid[0])
    bh, bw = R // 3, C // 3
    out = []
    for bi in range(3):
        row = []
        for bj in range(3):
            val = 0
            for r in range(bi * bh, (bi + 1) * bh):
                for c in range(bj * bw, (bj + 1) * bw):
                    if grid[r][c] != 0:
                        val = grid[r][c]
            row.append(val)
        out.append(row)
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
