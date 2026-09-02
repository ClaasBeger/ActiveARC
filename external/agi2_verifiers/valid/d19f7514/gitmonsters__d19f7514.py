"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: d19f7514
source: GitMonsters/SOLVED-562-verified
original_path: solves/d19f7514/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__d19f7514
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    Extract and merge two 6x4 regions of a 12x4 grid.
    
    Input: 12x4 grid
      - Top half (rows 0-5): Contains 0 and 3
      - Bottom half (rows 6-11): Contains 0 and 5
    
    Output: 6x4 grid
      - For each position (i,j): output is 4 if top[i][j]==3 OR bottom[i][j]==5, else 0
    """
    top = grid[:6]
    bottom = grid[6:12]
    
    output = []
    for i in range(6):
        row = []
        for j in range(4):
            has_3 = top[i][j] == 3
            has_5 = bottom[i][j] == 5
            value = 4 if (has_3 or has_5) else 0
            row.append(value)
        output.append(row)
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
