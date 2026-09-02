"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 94be5b80
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__94be5b80
"""
from __future__ import annotations



import numpy as np

def solve_94be5b80(input_grid):
    """
    Concept:
    Align and stack identical-shaped objects vertically in a grid 
    based on a reference ordering.

    Transformation Logic:
    1. Identify connected components of non-zero values using connected component analysis.
    2. Find the component that contains all unique non-zero values. 
       - This component is used as the "reference order" of objects.
       - Remove this reference component from the grid.
    3. Identify the other component(s) that only contain a subset of the values.
    4. Reorder these subset components to match the reference order.
    5. Stack missing objects above and/or below the subset so the final arrangement 
       reproduces the full ordered stack vertically.

    Effect:
    - The grid is transformed so that all identical-shaped objects appear stacked 
      on top of each other in the correct order, as dictated by the reference.
    """
    from grid_utils import group_connected_positions

    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    # Identify unique non-zero values and connected components
    unique_vals = np.unique(output_grid[output_grid != 0])
    parts = group_connected_positions(np.argwhere(output_grid != 0), connectivity=8)

    order, other_part, other_vals = None, None, None

    # Process each connected component
    for part in parts:
        part = np.array(part)
        min_row, min_col = part.min(axis=0)
        max_row, max_col = part.max(axis=0)
        block = input_grid[min_row:max_row+1, min_col:max_col+1]
        vals = np.unique(block[block != 0])

        if set(vals) == set(unique_vals):
            # Find the component that contains all unique non-zero values. This component is used as the "reference order" of objects.
            output_grid[part[:, 0], part[:, 1]] = 0
            order = block[0, :]
        else:
            # Identify the other component(s) that only contain a subset of the values.
            other_part, other_vals = part.copy(), vals.copy() 

    # Reorder other components to match the reference order
    place = np.array([np.where(order == v)[0][0] if v in order else -1 for v in other_vals])
    place = place - place.min()
    other_vals_sort = np.array(other_vals)[place]

    # Stack missing objects above the subset
    val = other_vals_sort[0]
    pos = np.argwhere(output_grid == val)
    min_r, min_c = pos.min(axis=0)
    max_r, max_c = pos.max(axis=0)
    pos_norm = pos - np.array([min_r, min_c])

    plc = np.argwhere(order == val)[0][0]
    val_before = order[:plc] if plc > 0 else None

    counter = 1
    for v in val_before[::-1]:
        posit = pos_norm + np.array([min_r - counter * (max_r - min_r + 1), min_c])
        counter += 1
        output_grid[posit[:, 0], posit[:, 1]] = v

    # Stack missing objects below the subset so the final arrangement reproduces the full ordered stack vertically.
    val = other_vals_sort[-1]
    pos = np.argwhere(output_grid == val)
    min_r, min_c = pos.min(axis=0)
    max_r, max_c = pos.max(axis=0)
    pos_norm = pos - np.array([min_r, min_c])

    plc = np.argwhere(order == val)[0][0]
    val_after = order[plc+1:] if plc > 0 else None

    counter = 0
    for v in val_after:
        posit = pos_norm + np.array([max_r + 1 + counter * (max_r - min_r + 1), min_c])
        counter += 1
        output_grid[posit[:, 0], posit[:, 1]] = v

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_94be5b80(input_grid)
    return _result
