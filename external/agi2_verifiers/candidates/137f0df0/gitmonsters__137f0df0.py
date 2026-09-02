"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 137f0df0
source: GitMonsters/SOLVED-562-verified
original_path: solves/137f0df0/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__137f0df0
"""
from __future__ import annotations



import json, sys

def solve(grid):
    rows = len(grid)
    cols = len(grid[0])

    block_rows = set()
    block_cols = set()
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 5:
                block_rows.add(r)
                block_cols.add(c)

    min_br, max_br = min(block_rows), max(block_rows)
    min_bc, max_bc = min(block_cols), max(block_cols)

    sep_rows = {r for r in range(min_br, max_br + 1) if r not in block_rows}
    sep_cols = {c for c in range(min_bc, max_bc + 1) if c not in block_cols}

    result = [row[:] for row in grid]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                in_r = min_br <= r <= max_br
                in_c = min_bc <= c <= max_bc
                is_sr = r in sep_rows
                is_sc = c in sep_cols
                if (is_sr and in_c) or (is_sc and in_r):
                    result[r][c] = 2
                elif is_sr or is_sc:
                    result[r][c] = 1
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
