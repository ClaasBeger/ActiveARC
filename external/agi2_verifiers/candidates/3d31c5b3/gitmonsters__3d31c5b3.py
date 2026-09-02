"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 3d31c5b3
source: GitMonsters/SOLVED-562-verified
original_path: solves/3d31c5b3/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__3d31c5b3
"""
from __future__ import annotations



"""
ARC-AGI Task 3d31c5b3 Solver

Pattern: Overlay four layers (5, 4, 2, 8) with priority 5 > 4 > 8 > 2
- Input: 12x6 grid (4 stacked 3x6 layers)
- Output: 3x6 grid (composite result)

For each position, pick the non-zero value with highest priority.
"""

def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    Solve ARC-AGI task 3d31c5b3.
    
    Args:
        grid: 12x6 input grid with 4 stacked layers
    
    Returns:
        3x6 output grid
    """
    # Extract the 4 layers from the input
    # Layer 5: rows 0-2
    # Layer 4: rows 3-5
    # Layer 2: rows 6-8
    # Layer 8: rows 9-11
    
    result = []
    
    for i in range(3):
        row = []
        for j in range(6):
            l5 = grid[i][j]
            l4 = grid[3 + i][j]
            l2 = grid[6 + i][j]
            l8 = grid[9 + i][j]
            
            # Priority: 5 > 4 > 8 > 2
            if l5 != 0:
                value = l5
            elif l4 != 0:
                value = l4
            elif l8 != 0:
                value = l8
            elif l2 != 0:
                value = l2
            else:
                value = 0
            
            row.append(value)
        
        result.append(row)
    
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
