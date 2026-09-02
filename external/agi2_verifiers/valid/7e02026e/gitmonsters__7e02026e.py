"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 7e02026e
source: GitMonsters/SOLVED-562-verified
original_path: solves/7e02026e/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__7e02026e
"""
from __future__ import annotations



import json
from typing import List

def solve(grid: List[List[int]]) -> List[List[int]]:
    """
    Color swap puzzle: Mark certain 0-cells with color 3 based on pattern.
    The rule: Find all connected regions of 0s. In each region, identify
    cross/diamond patterns and mark them with color 3.
    """
    output = [row[:] for row in grid]
    
    def get_zero_regions():
        """Find all connected regions of 0s"""
        visited = set()
        regions = []
        
        def dfs(r, c, region):
            if (r, c) in visited or r < 0 or r >= len(grid) or c < 0 or c >= len(grid[0]):
                return
            if grid[r][c] != 0:
                return
            visited.add((r, c))
            region.append((r, c))
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                dfs(r + dr, c + dc, region)
        
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if (r, c) not in visited and grid[r][c] == 0:
                    region = []
                    dfs(r, c, region)
                    regions.append(region)
        
        return regions
    
    def find_diamonds_in_region(region):
        """
        Find + cross patterns in a 0-region.
        Cross pattern: center at (r, c) with cells up, down, left, right all being 0.
        """
        region_set = set(region)
        crosses = []
        
        # For each cell in the region, check if it's a + cross center
        for r, c in region:
            # Check for + cross pattern (center + 4 cardinal neighbors)
            plus_cells = [(r, c), (r-1, c), (r+1, c), (r, c-1), (r, c+1)]
            if all(cell in region_set for cell in plus_cells):
                crosses.append(plus_cells)
        
        return crosses
    
    # Find all 0-regions
    regions = get_zero_regions()
    
    # For each region, find diamonds and mark them
    for region in regions:
        diamonds = find_diamonds_in_region(region)
        for diamond in diamonds:
            for r, c in diamond:
                output[r][c] = 3
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
