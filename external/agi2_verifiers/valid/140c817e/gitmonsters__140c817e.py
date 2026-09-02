"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 140c817e
source: GitMonsters/SOLVED-562-verified
original_path: solves/140c817e/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__140c817e
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    # Find background color and 1-positions
    ones: list[tuple[int, int]] = []
    bg = -1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                ones.append((r, c))
            else:
                bg = grid[r][c]

    result = [[bg] * cols for _ in range(rows)]

    # Draw cross lines (value 1) through each original 1 position
    for r, c in ones:
        for cc in range(cols):
            result[r][cc] = 1
        for rr in range(rows):
            result[rr][c] = 1

    # Place 3s at diagonal neighbors of each original 1
    for r, c in ones:
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and result[nr][nc] != 1:
                result[nr][nc] = 3

    # Place 2 at each original 1 position (highest priority)
    for r, c in ones:
        result[r][c] = 2

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
