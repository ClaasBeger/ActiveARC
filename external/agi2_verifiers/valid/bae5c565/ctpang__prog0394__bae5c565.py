"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: bae5c565
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[394](id=394)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0394__bae5c565
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = grid.shape
    
    # Find the purple bar column c, r_start, h
    c = -1
    r_start = -1
    max_h = 0
    for col in range(cols):
        for row in range(rows):
            if grid[row, col] == 8:
                rs = row
                hh = 1
                for r in range(row + 1, rows):
                    if grid[r, col] == 8:
                        hh += 1
                    else:
                        break
                if hh > max_h:
                    max_h = hh
                    c = col
                    r_start = rs
    
    h = max_h
    original = grid[0].tolist()
    
    # Create output grid filled with 5s
    output = np.full((rows, cols), 5, dtype=int)
    
    # Build the pyramid
    for k in range(h):
        py_row = r_start + k
        ideal_w = 1 + 2 * k
        w = min(ideal_w, cols)
        half = (w - 1) // 2
        start_idx = c - half
        end_idx = c + half
        
        # Extract and modify segment
        segment = []
        for idx in range(start_idx, end_idx + 1):
            if 0 <= idx < cols:
                val = original[idx]
                if val == 5:
                    val = 8
                segment.append(val)
        
        # Place segment in output
        start_col = c - half
        for j in range(len(segment)):
            output[py_row, start_col + j] = segment[j]
    
    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
