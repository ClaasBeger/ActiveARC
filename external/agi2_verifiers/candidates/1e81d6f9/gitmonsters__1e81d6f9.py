"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 1e81d6f9
source: GitMonsters/SOLVED-562-verified
original_path: solves/1e81d6f9/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__1e81d6f9
"""
from __future__ import annotations



import copy

def solve(grid: list[list[int]]) -> list[list[int]]:
    result = copy.deepcopy(grid)
    rows, cols = len(grid), len(grid[0])
    
    # Find the key box bordered by 5s in the top-left corner.
    # Structure: 5s form right column and bottom row of a small box.
    # Find box extents by locating the horizontal and vertical 5-lines.
    box_row = 0
    box_col = 0
    for r in range(rows):
        if all(grid[r][c] == 5 for c in range(4)):  # full row of 5s
            box_row = r
            break
    for c in range(cols):
        if all(grid[r][c] == 5 for r in range(box_row + 1)):  # full col of 5s
            box_col = c
            break

    # Find the key color: non-zero, non-5 value inside the box
    key_color = 0
    for r in range(box_row):
        for c in range(box_col):
            if grid[r][c] != 0 and grid[r][c] != 5:
                key_color = grid[r][c]
                break
        if key_color:
            break

    # Remove all instances of key_color outside the box region
    for r in range(rows):
        for c in range(cols):
            if r <= box_row and c <= box_col:
                continue  # inside box, keep
            if result[r][c] == key_color:
                result[r][c] = 0

    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
