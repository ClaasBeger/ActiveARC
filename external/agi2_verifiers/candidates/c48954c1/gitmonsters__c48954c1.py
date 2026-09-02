"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: c48954c1
source: GitMonsters/SOLVED-562-verified
original_path: solves/c48954c1/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__c48954c1
"""
from __future__ import annotations



def solve(grid):
    """3x3 input → 9x9 output. Tile 3x3 with reflections creating seamless wallpaper."""
    n = len(grid)
    # Precompute transformations
    O = [row[:] for row in grid]
    H = [row[::-1] for row in grid]               # horizontal flip
    V = [row[:] for row in reversed(grid)]         # vertical flip
    R180 = [row[::-1] for row in reversed(grid)]   # 180° rotation

    # Block layout:
    # R180  V    R180
    # H     O    H
    # R180  V    R180
    blocks = [
        [R180, V, R180],
        [H, O, H],
        [R180, V, R180],
    ]

    result = []
    for br in range(3):
        for r in range(n):
            row = []
            for bc in range(3):
                row.extend(blocks[br][bc][r])
            result.append(row)
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
