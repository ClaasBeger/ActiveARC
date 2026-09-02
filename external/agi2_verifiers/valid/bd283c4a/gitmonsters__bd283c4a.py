"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: bd283c4a
source: GitMonsters/SOLVED-562-verified
original_path: solves/bd283c4a/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__bd283c4a
"""
from __future__ import annotations



"""ARC-AGI puzzle bd283c4a solver.
Rule: Count color frequencies, sort descending, fill output column-by-column bottom-to-top.
"""
from collections import Counter

def transform(input_grid: list[list[int]]) -> list[list[int]]:
    rows = len(input_grid)
    cols = len(input_grid[0])
    
    counts: Counter = Counter()
    for row in input_grid:
        for val in row:
            counts[val] += 1
    
    sorted_colors = sorted(counts.items(), key=lambda x: -x[1])
    
    output = [[0] * cols for _ in range(rows)]
    
    color_idx = 0
    remaining = sorted_colors[0][1]
    current_color = sorted_colors[0][0]
    
    for c in range(cols):
        for r in range(rows - 1, -1, -1):
            if remaining == 0:
                color_idx += 1
                current_color = sorted_colors[color_idx][0]
                remaining = sorted_colors[color_idx][1]
            output[r][c] = current_color
            remaining -= 1
    
    return output



# Catalog entry point: every solver in solves/ exposes solve(grid).
def solve(grid):
    return [list(row) for row in transform(grid)]

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
