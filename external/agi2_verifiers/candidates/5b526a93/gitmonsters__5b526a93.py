"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 5b526a93
source: GitMonsters/SOLVED-562-verified
original_path: solves/5b526a93/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__5b526a93
"""
from __future__ import annotations



import json
from typing import List, Set

def solve(grid: List[List[int]]) -> List[List[int]]:
    """
    Rule:
    1. Find all column positions where [1,1,1] appears in any row (3-wide blocks of all 1s)
    2. These are the 3x3 block positions
    3. For each row group, fill all-zero blocks at these positions using 8s
    """
    result = [row[:] for row in grid]
    rows, cols = len(grid), len(grid[0]) if grid else 0
    
    if rows < 3 or cols < 3:
        return result
    
    # Find all column positions with [1, 1, 1]
    block_positions: Set[int] = set()
    
    for row in grid:
        for col_start in range(len(row) - 2):
            if row[col_start] == 1 and row[col_start + 1] == 1 and row[col_start + 2] == 1:
                block_positions.add(col_start)
    
    block_positions = sorted(block_positions)
    
    if not block_positions:
        return result
    
    # Process each row group
    for row_start in range(0, rows, 3):
        row_end = min(row_start + 3, rows)
        if row_end - row_start < 3:
            continue
        
        # Find template from first block with 1s
        template_shape = None
        template_col = None
        
        for block_col in block_positions:
            if block_col + 3 <= cols:
                block = [grid[r][block_col:block_col+3] for r in range(row_start, row_end)]
                has_ones = any(v == 1 for row in block for v in row)
                
                if has_ones and template_shape is None:
                    template_shape = tuple(tuple(1 if v == 1 else 0 for v in row) for row in block)
                    template_col = block_col
                    break
        
        if template_shape is None:
            continue
        
        # Fill other all-zero blocks
        for block_col in block_positions:
            if block_col == template_col or block_col + 3 > cols:
                continue
            
            is_all_zeros = all(grid[r][c] == 0 for r in range(row_start, row_end) for c in range(block_col, block_col + 3))
            
            if is_all_zeros:
                for r in range(row_start, row_end):
                    for c in range(block_col, block_col + 3):
                        shape_r = r - row_start
                        shape_c = c - block_col
                        if template_shape[shape_r][shape_c] == 1:
                            result[r][c] = 8
    
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
