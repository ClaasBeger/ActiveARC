"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: f823c43c
source: GitMonsters/SOLVED-562-verified
original_path: solves/f823c43c/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__f823c43c
"""
from __future__ import annotations



"""ARC-AGI puzzle f823c43c solver.

Pattern: The grid has a repeating tile pattern corrupted by noise (color 6).
Remove noise by finding the smallest consistent tile and re-tiling the grid.
"""
import json


def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    noise = 6

    for py in range(1, rows + 1):
        for px in range(1, cols + 1):
            tile = [[None] * px for _ in range(py)]
            consistent = True
            for r in range(rows):
                if not consistent:
                    break
                for c in range(cols):
                    if grid[r][c] != noise:
                        tr, tc = r % py, c % px
                        if tile[tr][tc] is None:
                            tile[tr][tc] = grid[r][c]
                        elif tile[tr][tc] != grid[r][c]:
                            consistent = False
                            break

            if consistent and all(
                tile[tr][tc] is not None for tr in range(py) for tc in range(px)
            ):
                return [[tile[r % py][c % px] for c in range(cols)] for r in range(rows)]

    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
