"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 8597cfd7
source: GitMonsters/SOLVED-562-verified
original_path: solves/8597cfd7/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__8597cfd7
"""
from __future__ import annotations



import json

def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    ARC puzzle 8597cfd7 solver.
    
    Rule: Find the row with all 5s (divider).
    Count occurrences of colors 2 and 4 in top and bottom sections.
    Return the color that increases MORE from top to bottom section.
    """
    # Find the divider row (all 5s)
    divider_row = -1
    for i, row in enumerate(grid):
        if all(cell == 5 for cell in row):
            divider_row = i
            break
    
    if divider_row == -1:
        return [[0, 0], [0, 0]]
    
    # Count colors in top and bottom sections
    count_2_top = sum(row.count(2) for row in grid[:divider_row])
    count_4_top = sum(row.count(4) for row in grid[:divider_row])
    count_2_bot = sum(row.count(2) for row in grid[divider_row + 1:])
    count_4_bot = sum(row.count(4) for row in grid[divider_row + 1:])
    
    # Calculate the increase from top to bottom for each color
    increase_2 = count_2_bot - count_2_top
    increase_4 = count_4_bot - count_4_top
    
    # Pick the color with the larger increase (or 2 as default if tied)
    winning_color = 2 if increase_2 >= increase_4 else 4
    
    # Return 2x2 grid filled with winning color
    return [[winning_color, winning_color], [winning_color, winning_color]]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
