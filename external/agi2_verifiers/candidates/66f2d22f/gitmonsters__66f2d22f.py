"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 66f2d22f
source: GitMonsters/SOLVED-562-verified
original_path: solves/66f2d22f/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__66f2d22f
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    ARC-AGI Puzzle 66f2d22f Solver
    
    Rule: Split the 4x14 grid into left (cols 0-6) and right (cols 7-13) halves.
    For each cell, output 5 if (left != 3 AND right != 2), else output 0.
    Result is a 4x7 grid.
    """
    rows = len(grid)
    cols = 7
    result = []
    
    for row in grid:
        output_row = []
        for j in range(cols):
            left_val = row[j]
            right_val = row[j + cols]
            
            output_val = 5 if (left_val != 3 and right_val != 2) else 0
            output_row.append(output_val)
        result.append(output_row)
    
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
