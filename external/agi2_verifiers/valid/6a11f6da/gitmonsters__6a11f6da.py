"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 6a11f6da
source: GitMonsters/SOLVED-562-verified
original_path: solves/6a11f6da/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__6a11f6da
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    The input is a 15x5 grid composed of 3 stacked 5x5 layers:
    - Layer 0 (rows 0-4): contains color 1
    - Layer 1 (rows 5-9): contains color 8
    - Layer 2 (rows 10-14): contains color 6
    
    The output is a 5x5 grid where each cell contains the color from the
    highest priority color at that position across all three layers.
    
    Priority: 6 > 1 > 8 > 0
    """
    layer0 = grid[0:5]
    layer1 = grid[5:10]
    layer2 = grid[10:15]
    
    result = []
    for i in range(5):
        row = []
        for j in range(5):
            colors = [layer0[i][j], layer1[i][j], layer2[i][j]]
            
            # Priority: 6 > 1 > 8 > 0
            if 6 in colors:
                row.append(6)
            elif 1 in colors:
                row.append(1)
            elif 8 in colors:
                row.append(8)
            else:
                row.append(0)
        result.append(row)
    
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
