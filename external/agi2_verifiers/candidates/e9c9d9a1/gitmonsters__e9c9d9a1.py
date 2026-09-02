"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e9c9d9a1
source: GitMonsters/SOLVED-562-verified
original_path: solves/e9c9d9a1/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__e9c9d9a1
"""
from __future__ import annotations



"""Solver for ARC-AGI puzzle e9c9d9a1"""
import json
from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    rows = len(grid)
    cols = len(grid[0])
    
    # Find horizontal separator rows (all 3s)
    h_seps = [r for r in range(rows) if all(grid[r][c] == 3 for c in range(cols))]
    # Find vertical separator cols (all 3s)
    v_seps = [c for c in range(cols) if all(grid[r][c] == 3 for r in range(rows))]
    
    # Build row bands (ranges between separators)
    row_edges = [-1] + h_seps + [rows]
    row_bands = []
    for i in range(len(row_edges) - 1):
        start = row_edges[i] + 1
        end = row_edges[i + 1]
        if start < end:
            row_bands.append((start, end))
    
    # Build col bands
    col_edges = [-1] + v_seps + [cols]
    col_bands = []
    for i in range(len(col_edges) - 1):
        start = col_edges[i] + 1
        end = col_edges[i + 1]
        if start < end:
            col_bands.append((start, end))
    
    n_rb = len(row_bands)
    n_cb = len(col_bands)
    
    # Determine fill color for each cell in the logical grid
    out = [row[:] for row in grid]
    for ri, (r_start, r_end) in enumerate(row_bands):
        for ci, (c_start, c_end) in enumerate(col_bands):
            # Corner cells
            if ri == 0 and ci == 0:
                color = 2
            elif ri == 0 and ci == n_cb - 1:
                color = 4
            elif ri == n_rb - 1 and ci == 0:
                color = 1
            elif ri == n_rb - 1 and ci == n_cb - 1:
                color = 8
            # Interior cells (not on any edge of the logical grid)
            elif 0 < ri < n_rb - 1 and 0 < ci < n_cb - 1:
                color = 7
            else:
                color = 0  # edge but not corner → stays 0
            
            for r in range(r_start, r_end):
                for c in range(c_start, c_end):
                    out[r][c] = color
    
    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
