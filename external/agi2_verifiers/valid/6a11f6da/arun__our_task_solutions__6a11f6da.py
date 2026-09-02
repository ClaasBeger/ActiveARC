"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 6a11f6da
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__6a11f6da
"""
from __future__ import annotations



import numpy as np

def solve_6a11f6da(input_grid):
    """
    Concepts: grid partitioning into three parts, merged by overlapping.
    Non-zero values overwrite zeros sequentially.

    Steps:
    1. Split input grid into 3 equal vertical sections.
    2. Rearrange sections in order: last → first → second.
    3. Build output by filling zeros with values from each section in sequence.
    """

    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    part_size = nrows // 3
    # Step 1 and 2: Partition rows into three equal parts and rearrange them in the order
    parts = [
        input_grid[2 * part_size:],          # last part
        input_grid[:part_size],               # first part
        input_grid[part_size:2 * part_size]  # second part
    ]

    # Step 3: Build output by filling zeros with values from each section
    output_grid = np.zeros((part_size, ncols), dtype=input_grid.dtype)
    for part in parts:
        mask = (output_grid == 0)
        output_grid[mask] = part[mask]

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_6a11f6da(input_grid)
    return _result
