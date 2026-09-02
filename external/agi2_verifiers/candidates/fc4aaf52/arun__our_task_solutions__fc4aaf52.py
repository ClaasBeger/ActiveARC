"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: fc4aaf52
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__fc4aaf52
"""
from __future__ import annotations



import numpy as np

def solve_fc4aaf52(input_grid):
    """
    Concepts: color flipping, grid partitioning, and connected component analysis.

    Transformation steps:
    1. Initialize output with background (8).
    2. Flip non-background colors.
    3. Split into top and bottom halves around the vertical midpoint of non-background cells.
    4. Shift the top half horizontally until top+bottom form more than one connected component.
    5. Return the last valid connected configuration.
    """
    from grid_utils import group_connected_positions
    
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    background = 8

    # Step 1: initialize with background
    output_grid = np.full((nrows, ncols), background)

    # Step 2: flip non-background values (colors)
    values = np.unique(input_grid[input_grid != background])
    if len(values) > 0:
        mapping = {v: values[(i + 1) % len(values)] for i, v in enumerate(values)}
        for r, c in np.argwhere(input_grid != background):
            output_grid[r, c] = mapping[input_grid[r, c]]

    # Step 3: split into top and bottom halves
    non_bg_positions = np.argwhere(output_grid != background)
    min_r, max_r = non_bg_positions[:, 0].min(), non_bg_positions[:, 0].max()
    mid = (min_r + max_r) // 2
    top, bottom = output_grid[:mid + 1], output_grid[mid + 1:]

    # Step 4 + 5: shift top horizontally, track connectivity
    for _ in range(ncols):
        candidate = np.vstack((top, bottom))
        positions = np.argwhere(candidate != background)
        pieces = group_connected_positions(positions, connectivity=8)

        if len(pieces) == 1:   # valid fully connected
            output_grid = candidate
        else:                  # connectivity breaks → stop
            break

        # cyclic right shift of top
        top = np.hstack((top[:, -1:], top[:, :-1]))

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_fc4aaf52(input_grid)
    return _result
