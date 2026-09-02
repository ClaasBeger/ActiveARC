"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: bf699163
source: GitMonsters/SOLVED-562-verified
original_path: solves/bf699163/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__bf699163
"""
from __future__ import annotations



def solve(grid):
    """Extract the 3x3 block enclosed by the scattered (non-block) color's bounding box."""
    rows = len(grid)
    cols = len(grid[0])
    bg = 5  # background

    # Find all non-bg colors and their cells
    from collections import defaultdict
    color_cells = defaultdict(list)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != bg:
                color_cells[grid[r][c]].append((r, c))

    # Identify 3x3 blocks: pattern [[c,c,c],[c,bg,c],[c,c,c]]
    block_colors = set()
    for color, cells in color_cells.items():
        if len(cells) == 8:
            rs = [r for r, c in cells]
            cs = [c for r, c in cells]
            rmin, rmax = min(rs), max(rs)
            cmin, cmax = min(cs), max(cs)
            if rmax - rmin == 2 and cmax - cmin == 2:
                # Check it's a frame pattern (center is bg)
                center_r, center_c = rmin + 1, cmin + 1
                if grid[center_r][center_c] == bg:
                    block_colors.add(color)

    # The scattered color is the one that's NOT a clean 3x3 block
    scatter_color = None
    for color in color_cells:
        if color not in block_colors:
            scatter_color = color
            break

    # Bounding box of scattered color
    scatter_cells = color_cells[scatter_color]
    sr_min = min(r for r, c in scatter_cells)
    sr_max = max(r for r, c in scatter_cells)
    sc_min = min(c for r, c in scatter_cells)
    sc_max = max(c for r, c in scatter_cells)

    # Find the 3x3 block inside scatter bounding box
    for color in block_colors:
        cells = color_cells[color]
        rs = [r for r, c in cells]
        cs = [c for r, c in cells]
        rmin, rmax = min(rs), max(rs)
        cmin, cmax = min(cs), max(cs)
        # Check if block is inside scatter bbox
        if rmin >= sr_min and rmax <= sr_max and cmin >= sc_min and cmax <= sc_max:
            # Extract the 3x3 block
            return [grid[r][cmin:cmax + 1] for r in range(rmin, rmax + 1)]

    return grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
