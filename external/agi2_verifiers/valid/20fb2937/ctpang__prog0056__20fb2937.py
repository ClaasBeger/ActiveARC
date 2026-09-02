"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 20fb2937
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[56](id=56)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0056__20fb2937
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    # Extract block colors
    colorL = grid[0][0]
    colorM = grid[0][4]
    colorR = grid[0][8]
    
    # Extract representatives
    repL = grid[4][1]
    repM = grid[4][5]
    repR = grid[4][9]
    
    # Mapping
    mapping = {repL: colorL, repM: colorM, repR: colorR}
    
    # Initialize output 13x11 with 7
    output = [[7] * 11 for _ in range(13)]
    
    # Place blocks for each representative in rows 7-19
    for in_r in range(7, 20):
        for c in range(11):
            col = grid[in_r][c]
            if col != 7 and col in mapping:
                block_col = mapping[col]
                out_r = in_r - 7
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr = out_r + dr
                        nc = c + dc
                        if 0 <= nr < 13 and 0 <= nc < 11:
                            output[nr][nc] = block_col
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
