"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 45737921
source: GitMonsters/SOLVED-562-verified
original_path: solves/45737921/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__45737921
"""
from __future__ import annotations



import json
import sys
from collections import defaultdict
from typing import List


def find_connected_regions(grid: List[List[int]]) -> List[List[tuple]]:
    """Find all connected non-zero regions using DFS."""
    visited = set()
    regions = []
    rows, cols = len(grid), len(grid[0])
    
    def dfs(r: int, c: int) -> List[tuple]:
        if r < 0 or r >= rows or c < 0 or c >= cols or (r, c) in visited or grid[r][c] == 0:
            return []
        visited.add((r, c))
        cells = [(r, c)]
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            cells.extend(dfs(r + dr, c + dc))
        return cells
    
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in visited and grid[r][c] != 0:
                region = dfs(r, c)
                if region:
                    regions.append(region)
    
    return regions


def solve(grid: List[List[int]]) -> List[List[int]]:
    """
    Solve the puzzle by swapping two colors within each connected region.
    """
    result = [row[:] for row in grid]
    
    # Find all connected regions
    regions = find_connected_regions(grid)
    
    # For each region, identify the two colors and swap them
    for region in regions:
        colors = set(grid[r][c] for r, c in region)
        
        if len(colors) == 2:
            color_list = list(colors)
            color1, color2 = color_list[0], color_list[1]
            
            # Swap colors in this region
            for r, c in region:
                if result[r][c] == color1:
                    result[r][c] = color2
                elif result[r][c] == color2:
                    result[r][c] = color1
        elif len(colors) == 1:
            # Single color region - no swap needed
            pass
    
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
