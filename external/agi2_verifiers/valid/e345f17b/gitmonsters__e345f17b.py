"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e345f17b
source: GitMonsters/SOLVED-562-verified
original_path: solves/e345f17b/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__e345f17b
"""
from __future__ import annotations



import json


def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    Solve e345f17b: Split 4x8 grid into left (cols 0-3) and right (cols 4-7).
    Output 4x4 grid where each cell is 4 if both corresponding left and right cells are 0, else 0.
    """
    result = []
    for r in range(4):
        row = []
        for c in range(4):
            left_val = grid[r][c]
            right_val = grid[r][c + 4]
            
            if left_val == 0 and right_val == 0:
                row.append(4)
            else:
                row.append(0)
        result.append(row)
    
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
