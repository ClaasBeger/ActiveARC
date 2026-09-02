"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ff72ca3e
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[537](id=537)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0537__ff72ca3e
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    rows = len(grid)
    cols = len(grid[0])
    
    output = [row[:] for row in grid]
    
    yellows = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 4]
    
    for yr, yc in yellows:
        r_border = min(yr, rows - 1 - yr, yc, cols - 1 - yc)
        
        max_r = 0
        for candidate_r in range(0, r_border + 1):
            ok = True
            for i in range(-candidate_r, candidate_r + 1):
                for j in range(-candidate_r, candidate_r + 1):
                    pr = yr + i
                    pc = yc + j
                    if grid[pr][pc] == 5:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                break
            max_r = candidate_r
        
        # Fill the square
        for i in range(-max_r, max_r + 1):
            for j in range(-max_r, max_r + 1):
                pr = yr + i
                pc = yc + j
                if 0 <= pr < rows and 0 <= pc < cols and grid[pr][pc] == 0:
                    output[pr][pc] = 2
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
