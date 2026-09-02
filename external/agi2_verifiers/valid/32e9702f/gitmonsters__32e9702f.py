"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 32e9702f
source: GitMonsters/SOLVED-562-verified
original_path: solves/32e9702f/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__32e9702f
"""
from __future__ import annotations



"""
ARC-AGI solver for task 32e9702f

Rule:
- Replace all 0s with 5.
- Shift each contiguous horizontal colored segment left by 1 position,
  clipping at the left grid edge.
"""


def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    out = [[5] * cols for _ in range(rows)]

    for r in range(rows):
        c = 0
        while c < cols:
            if grid[r][c] != 0:
                color = grid[r][c]
                start = c
                while c < cols and grid[r][c] == color:
                    c += 1
                # Shift segment left by 1
                new_start = max(0, start - 1)
                new_end = new_start + (c - start)
                if new_start == 0 and start == 0:
                    # Can't shift left; truncate from the right
                    new_end = c - 1
                for nc in range(new_start, min(new_end, cols)):
                    out[r][nc] = color
            else:
                c += 1

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
