"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: d304284e
source: GitMonsters/SOLVED-562-verified
original_path: solves/d304284e/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__d304284e
"""
from __future__ import annotations



#!/usr/bin/env python3
import json
from typing import List

def solve(grid: List[List[int]]) -> List[List[int]]:
    """
    Find the pattern shape and tile it horizontally and vertically.
    Horizontal tiling repeats: 7, 7, 6, 7, 7, 6... (color pattern of period 3)
    First row block shows all tiles (even partial ones at the edge).
    Subsequent row blocks show only tiles marked as color 6.
    """
    height = len(grid)
    width = len(grid[0])
    
    # Find bounding box of non-zero elements
    non_zero_rows = [r for r in range(height) if any(grid[r][c] != 0 for c in range(width))]
    non_zero_cols = [c for c in range(width) if any(grid[r][c] != 0 for r in range(height))]
    
    if not non_zero_rows or not non_zero_cols:
        return grid
    
    min_row, max_row = non_zero_rows[0], non_zero_rows[-1]
    min_col, max_col = non_zero_cols[0], non_zero_cols[-1]
    
    # Extract the pattern
    pattern_height = max_row - min_row + 1
    pattern_width = max_col - min_col + 1
    
    pattern = []
    for r in range(min_row, max_row + 1):
        row = []
        for c in range(min_col, max_col + 1):
            row.append(grid[r][c])
        pattern.append(row)
    
    # Get the original color
    original_color = None
    for r in pattern:
        for v in r:
            if v != 0:
                original_color = v
                break
        if original_color:
            break
    
    # Create output grid
    output = [[0] * width for _ in range(height)]
    
    # Tile spacing: pattern_width + 1 (one gap column)
    tile_period = pattern_width + 1
    
    # Color pattern repeats every 3 tiles: original, original, 6
    color_pattern = [original_color, original_color, 6]
    
    # First row block: place all tiles (including partial ones at edges)
    tile_col = 0
    col_offset = min_col
    
    while col_offset < width:
        color = color_pattern[tile_col % 3]
        
        # Place pattern, allowing it to be partial at right edge
        for r_idx, r in enumerate(pattern):
            for c_idx, val in enumerate(r):
                if val != 0:
                    out_col = col_offset + c_idx
                    if out_col < width:
                        output[min_row + r_idx][out_col] = color
        
        col_offset += tile_period
        tile_col += 1
    
    # Vertical tiling: subsequent row blocks only show tiles marked as color 6
    vert_tile_period = pattern_height + 1
    
    vert_row = 1
    row_offset = min_row + pattern_height + 1
    
    while row_offset < height:
        # Only place tiles where color_pattern[tile_col % 3] == 6
        tile_col = 0
        col_offset = min_col
        
        while col_offset < width:
            color = color_pattern[tile_col % 3]
            
            if color == 6:
                for r_idx, r in enumerate(pattern):
                    out_row = row_offset + r_idx
                    if out_row < height:
                        for c_idx, val in enumerate(r):
                            if val != 0:
                                out_col = col_offset + c_idx
                                if out_col < width:
                                    output[out_row][out_col] = 6
            
            col_offset += tile_period
            tile_col += 1
        
        row_offset += vert_tile_period
        vert_row += 1
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
