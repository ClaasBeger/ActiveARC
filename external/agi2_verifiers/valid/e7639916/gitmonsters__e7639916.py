"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e7639916
source: GitMonsters/SOLVED-562-verified
original_path: solves/e7639916/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__e7639916
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    Find all 8s in the grid. They mark the corners of a rectangle.
    Draw a rectangle border using 1s connecting these corner 8s.
    """
    # Find all positions with 8s
    eights = []
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 8:
                eights.append((r, c))
    
    if len(eights) < 3:
        return [row[:] for row in grid]
    
    # Find bounding box of all 8s
    min_r = min(e[0] for e in eights)
    max_r = max(e[0] for e in eights)
    min_c = min(e[1] for e in eights)
    max_c = max(e[1] for e in eights)
    
    # Create output grid as a copy
    result = [row[:] for row in grid]
    
    # Draw horizontal lines on top and bottom
    for c in range(min_c, max_c + 1):
        if result[min_r][c] != 8:
            result[min_r][c] = 1
        if result[max_r][c] != 8:
            result[max_r][c] = 1
    
    # Draw vertical lines on left and right
    for r in range(min_r, max_r + 1):
        if result[r][min_c] != 8:
            result[r][min_c] = 1
        if result[r][max_c] != 8:
            result[r][max_c] = 1
    
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
