"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 8a371977
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[283](id=283)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0283__8a371977
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    h = len(grid)
    w = len(grid[0])
    
    # Find sparse rows: rows with any 0
    sparse_rows = [i for i in range(h) if any(x == 0 for x in grid[i])]
    
    # Group consecutive sparse rows into blocks
    blocks = []
    current = []
    for r in sparse_rows:
        if not current or r == current[-1] + 1:
            current.append(r)
        else:
            blocks.append(current)
            current = [r]
    if current:
        blocks.append(current)
    M = len(blocks)
    
    # Find runs of 0's in the first sparse row
    if not sparse_rows:
        return grid  # No changes if no sparse rows
    sample_row = grid[sparse_rows[0]]
    runs = []
    start = -1
    for c in range(w):
        if sample_row[c] == 0:
            if start == -1:
                start = c
        else:
            if start != -1:
                runs.append((start, c - 1))
                start = -1
    if start != -1:
        runs.append((start, w - 1))
    N = len(runs)
    
    # Now fill the grid
    output = [row[:] for row in grid]  # Copy grid
    for bm in range(M):
        block_rows = blocks[bm]
        for bn in range(N):
            if bm == 0 or bm == M - 1 or bn == 0 or bn == N - 1:
                color = 2
            else:
                color = 3
            min_c, max_c = runs[bn]
            for r in block_rows:
                for c in range(min_c, max_c + 1):
                    output[r][c] = color
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
