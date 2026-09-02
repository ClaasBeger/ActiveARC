"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 2685904e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[76](id=76)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0076__2685904e
"""
from __future__ import annotations



import numpy as np

from collections import Counter

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    height = len(grid)
    width = len(grid[0])
    output = [row[:] for row in grid]
    
    # Find purple length N (consecutive 8's in row 0 from left)
    N = 0
    for c in range(width):
        if grid[0][c] == 8:
            N += 1
        else:
            break
    
    # Find gray_row: the row where all cells are 5
    gray_row = None
    for r in range(height):
        if all(cell == 5 for cell in grid[r]):
            gray_row = r
            break
    if gray_row is None:
        return output  # No gray bar, no change
    
    # Assume bottom_row is gray_row + 2
    bottom_row = gray_row + 2
    if bottom_row >= height:
        return output
    
    # Count frequencies in bottom_row
    freq = Counter()
    for c in range(width):
        color = grid[bottom_row][c]
        if color != 0:
            freq[color] += 1
    
    # For each color C with freq[C] == N
    for C in freq:
        if freq[C] == N:
            # Find columns where bottom has C
            cols = [c for c in range(width) if grid[bottom_row][c] == C]
            # For each such col, add pillar of height N upwards from gray_row - 1
            for col in cols:
                for h in range(N):
                    grow_r = gray_row - 1 - h
                    if grow_r >= 0:
                        output[grow_r][col] = C
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
