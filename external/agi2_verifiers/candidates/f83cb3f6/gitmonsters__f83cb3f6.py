"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: f83cb3f6
source: GitMonsters/SOLVED-562-verified
original_path: solves/f83cb3f6/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__f83cb3f6
"""
from __future__ import annotations



"""
ARC-AGI puzzle f83cb3f6 solver.

Rule: A line of 8s (horizontal or vertical, possibly with gaps) divides the grid.
For each 8-cell on the line, look perpendicular in both directions.
If any colored (non-0, non-8) cell exists in that direction, place a colored cell
adjacent to the 8 on that side. Everything else becomes 0.
"""
import json
from typing import List

Grid = List[List[int]]


def solve(grid: Grid) -> Grid:
    rows = len(grid)
    cols = len(grid[0])

    # Find all 8-positions
    eights = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 8]
    eight_rows = set(r for r, c in eights)
    eight_cols = set(c for r, c in eights)

    # Determine the non-background color
    color = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] not in (0, 8):
                color = grid[r][c]
                break
        if color:
            break

    # Build output (all zeros, same size)
    out = [[0] * cols for _ in range(rows)]

    # Place the 8-line
    for r, c in eights:
        out[r][c] = 8

    if len(eight_rows) == 1:
        # Horizontal line at row R
        R = list(eight_rows)[0]
        for c in range(cols):
            if grid[R][c] != 8:
                continue
            # Check above (rows 0..R-1)
            if any(grid[r][c] not in (0, 8) for r in range(R)):
                out[R - 1][c] = color
            # Check below (rows R+1..end)
            if any(grid[r][c] not in (0, 8) for r in range(R + 1, rows)):
                out[R + 1][c] = color
    else:
        # Vertical line at col C
        C = list(eight_cols)[0]
        for r in range(rows):
            if grid[r][C] != 8:
                continue
            # Check left (cols 0..C-1)
            if any(grid[r][c] not in (0, 8) for c in range(C)):
                out[r][C - 1] = color
            # Check right (cols C+1..end)
            if any(grid[r][c] not in (0, 8) for c in range(C + 1, cols)):
                out[r][C + 1] = color

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
