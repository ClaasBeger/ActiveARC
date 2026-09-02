"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: af726779
source: GitMonsters/SOLVED-562-verified
original_path: solves/af726779/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__af726779
"""
from __future__ import annotations



"""
ARC Puzzle af726779 Solver

Rule: There's a single row of orange(7) cells on a green(3) background.
From that row, a cascade propagates downward every 2 rows.
Each step: find size-1 gaps between consecutive colored positions from the
previous generation. Place new colored cells at those gap centers.
Colors alternate: step 1 = magenta(6), step 2 = orange(7), step 3 = magenta(6), ...
Continue until no size-1 gaps remain or grid runs out of rows.
"""
import copy

def transform(input_grid: list[list[int]]) -> list[list[int]]:
    grid = copy.deepcopy(input_grid)
    rows = len(grid)
    cols = len(grid[0])
    bg = 3

    # Find the pattern row (first row with non-background cells)
    pattern_row = None
    for r in range(rows):
        if any(c != bg for c in grid[r]):
            pattern_row = r
            break
    if pattern_row is None:
        return grid

    # Get initial colored positions (sorted)
    colored = sorted(c for c in range(cols) if grid[pattern_row][c] != bg)

    step = 1
    current_row = pattern_row

    while True:
        # Find size-1 gaps between consecutive colored positions
        new_colored = []
        for i in range(len(colored) - 1):
            if colored[i + 1] - colored[i] == 2:
                new_colored.append(colored[i] + 1)
        if not new_colored:
            break
        next_row = current_row + 2
        if next_row >= rows:
            break
        color = 6 if step % 2 == 1 else 7
        for c in new_colored:
            grid[next_row][c] = color
        colored = new_colored
        current_row = next_row
        step += 1

    return grid


# === Verification ===


# Catalog entry point: every solver in solves/ exposes solve(grid).
def solve(grid):
    return [list(row) for row in transform(grid)]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
