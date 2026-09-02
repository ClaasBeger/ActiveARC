"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 4f537728
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[157](id=157)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0157__4f537728
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    rows = len(grid)
    cols = len(grid[0])
    
    # Find defect color C (assuming one color != 0 and != 1)
    C = None
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and grid[r][c] != 1:
                C = grid[r][c]
                break
        if C is not None:
            break
    
    if C is None:
        return [row[:] for row in grid]  # No defect, return copy
    
    # Find defect positions
    defect_positions = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == C:
                defect_positions.append((r, c))
    
    # Find defect rows and cols
    rs = [p[0] for p in defect_positions]
    cs = [p[1] for p in defect_positions]
    min_r, max_r = min(rs), max(rs)
    min_c, max_c = min(cs), max(cs)
    defect_rows = set(range(min_r, max_r + 1))
    defect_cols = set(range(min_c, max_c + 1))
    
    # Create output
    output = [row[:] for row in grid]
    
    # Apply transformations
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                if r in defect_rows:
                    output[r][c] = C
                elif c in defect_cols:
                    output[r][c] = C
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
