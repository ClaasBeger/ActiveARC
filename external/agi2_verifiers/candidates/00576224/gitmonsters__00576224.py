"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 00576224
source: GitMonsters/SOLVED-562-verified
original_path: solves/00576224/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__00576224
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """Tile 2x2 input into 6x6. Alternate row-pairs: normal, LR-flipped, normal."""
    rows, cols = len(grid), len(grid[0])
    out = []
    for block_row in range(3):
        for input_row in range(rows):
            if block_row % 2 == 0:
                row = grid[input_row] * 3
            else:
                row = grid[input_row][::-1] * 3
            out.append(row)
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
