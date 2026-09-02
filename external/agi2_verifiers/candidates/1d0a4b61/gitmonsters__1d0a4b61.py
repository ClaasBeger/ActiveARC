"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 1d0a4b61
source: GitMonsters/SOLVED-562-verified
original_path: solves/1d0a4b61/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__1d0a4b61
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    H = len(grid)
    W = len(grid[0])

    # Find horizontal period: smallest p where all non-zero pairs agree
    def find_period_h() -> int:
        for p in range(1, W):
            ok = True
            for r in range(H):
                for c in range(W - p):
                    a, b = grid[r][c], grid[r][c + p]
                    if a != 0 and b != 0 and a != b:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return p
        return W

    # Find vertical period
    def find_period_v() -> int:
        for p in range(1, H):
            ok = True
            for r in range(H - p):
                for c in range(W):
                    a, b = grid[r][c], grid[r + p][c]
                    if a != 0 and b != 0 and a != b:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return p
        return H

    hp = find_period_h()
    vp = find_period_v()

    # Build template tile from non-zero values
    template = [[0] * hp for _ in range(vp)]
    for r in range(H):
        for c in range(W):
            if grid[r][c] != 0:
                template[r % vp][c % hp] = grid[r][c]

    # Tile the entire grid
    result = [[template[r % vp][c % hp] for c in range(W)] for r in range(H)]
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
