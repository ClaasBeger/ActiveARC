"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 4cd1b7b2
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[155](id=155)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0155__4cd1b7b2
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    n = len(grid)
    output = [row[:] for row in grid]
    
    row_used = [[False] * (n + 1) for _ in range(n)]
    col_used = [[False] * (n + 1) for _ in range(n)]
    empties = []
    
    for i in range(n):
        for j in range(n):
            c = output[i][j]
            if c == 0:
                empties.append((i, j))
            else:
                row_used[i][c] = True
                col_used[j][c] = True
    
    def backtrack(idx):
        if idx == len(empties):
            return True
        r, c = empties[idx]
        for num in range(1, n + 1):
            if not row_used[r][num] and not col_used[c][num]:
                output[r][c] = num
                row_used[r][num] = True
                col_used[c][num] = True
                if backtrack(idx + 1):
                    return True
                output[r][c] = 0
                row_used[r][num] = False
                col_used[c][num] = False
        return False
    
    backtrack(0)
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
