"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: a644e277
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__a644e277
"""
from __future__ import annotations



import numpy as np

def solve_a644e277(input_grid):
    """
    Concepts:
    - Region extraction based on dominant and secondary values
    - Subgrid cropping using row/column frequency analysis

    Transformation steps:
    1. Identify the background value (most frequent) and the marked value (second most frequent) in the grid.
    2. Find all the rows dominated by the marked value
    3. Find all the columns dominated by the marked value
    4. For each intersection of these rows and columns, check if the cell contains the background value.
    5. Collect all such row and column indices to define the bounding box.
    6. Crop the input grid to the rectangle defined by these rows and columns.
    """
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape

    # Step 1: Identify background and marked values
    unique_vals, counts = np.unique(input_grid, return_counts=True)
    counts_sorted = np.argsort(counts)
    background_val = unique_vals[counts_sorted[-1]]
    marked_val = unique_vals[counts_sorted[-2]]

    # Step 2: Find rows dominated by the marked value
    output_rows = []
    for r in range(nrows):
        uni_vals, cs = np.unique(input_grid[r], return_counts=True)
        most_freq_val = uni_vals[np.argmax(cs)]
        if most_freq_val == marked_val:
            output_rows.append(r)

    # Step 3: Find columns dominated by the marked value
    output_cols = []
    for c in range(ncols):
        uni_vals, cs = np.unique(input_grid[:, c], return_counts=True)
        most_freq_val = uni_vals[np.argmax(cs)]
        if most_freq_val == marked_val:
            output_cols.append(c)

    # Step 4: Find intersections where the cell is background
    output_corner_rows, output_corner_cols = set(), set()
    for r in output_rows:
        for c in output_cols:
            if input_grid[r, c] == background_val:
                output_corner_rows.add(r)
                output_corner_cols.add(c)

    # Step 5: Sort and crop
    output_corner_rows = sorted(output_corner_rows)
    output_corner_cols = sorted(output_corner_cols)

    # Step 6: Crop the grid to the bounding box
    output_grid = input_grid[
        output_corner_rows[0]:output_corner_rows[1]+1,
        output_corner_cols[0]:output_corner_cols[1]+1
    ]

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_a644e277(input_grid)
    return _result
