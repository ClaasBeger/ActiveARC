"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 6cbe9eb8
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__6cbe9eb8
"""
from __future__ import annotations



import numpy as np

def solve_6cbe9eb8(input_grid):
    """
    Concepts:
    - Detect and extract rectangular frames (may be given in parts) or rectangular filled region.
    - Put these frames/filled regions into each other like russian dolls.

    Steps:
    1. Identify unique values in the input grid.
    2. For each unique value, determine if it forms a rectangular frame or a filled rectangle.
    3. Sort the identified frames/filled rectangles by size (area).
    4. Create an output grid that nests the largest rectangle first, followed by smaller ones
       in a top-left aligned manner.    
    """
    input_grid = np.array(input_grid)

    unique_vals, _ = np.unique(input_grid, return_counts=True)

    def check_frame(pos):
        """Return True if `pos` belongs to different parts of a rectangular frame"""
        rows = [p[0] for p in pos]
        cols = [p[1] for p in pos]
        min_r, max_r = min(rows), max(rows)
        min_c, max_c = min(cols), max(cols)

        frame_positions = set()
        # Top and bottom edges
        for c in range(min_c, max_c + 1):
            frame_positions.add((min_r, c))
            frame_positions.add((max_r, c))
        # Left and right edges
        for r in range(min_r, max_r + 1):
            frame_positions.add((r, min_c))
            frame_positions.add((r, max_c))

        return frame_positions.intersection(set(map(tuple, pos))) == set(map(tuple, pos))

    def check_filled(pos):
        """Return True if `pos` forms a completely filled rectangle."""
        rows = [p[0] for p in pos]
        cols = [p[1] for p in pos]
        min_r, max_r = min(rows), max(rows)
        min_c, max_c = min(cols), max(cols)
        return len(pos) == (max_r - min_r + 1) * (max_c - min_c + 1)

    special_vals, positions, types = [], [], []

    for val in unique_vals:
        pos = np.argwhere(input_grid == val).tolist()
        if check_frame(pos):
            special_vals.append(val)
            positions.append(pos)
            types.append("frame")
        elif check_filled(pos):
            special_vals.append(val)
            positions.append(pos)
            types.append("filled")

    # Compute sizes for sorting by largest area
    sizes = []
    for pos in positions:
        rows = [p[0] for p in pos]
        cols = [p[1] for p in pos]
        sizes.append((max(rows) - min(rows) + 1, max(cols) - min(cols) + 1))

    sorted_indices = np.argsort([h * w for h, w in sizes])[::-1]  # largest area first

    largest_h, largest_w = sizes[sorted_indices[0]]
    output_grid = np.zeros((largest_h, largest_w), dtype=int) # Initialize output grid with zeros of size of largest component
    
    # Fill the output grid with the largest components first and then nest smaller components inside
    # all components are placed close to the top-left corner of the output grid
    indicator = 0
    for idx in sorted_indices:
        val = special_vals[idx]
        pos = positions[idx]
        kind = types[idx]

        rows = np.array([p[0] for p in pos])
        cols = np.array([p[1] for p in pos])
        min_r, max_r = rows.min(), rows.max()
        min_c, max_c = cols.min(), cols.max()
        height = max_r - min_r + 1
        width = max_c - min_c

        if kind == "filled":
            output_grid[
                largest_h - height - indicator : largest_h - indicator,
                indicator : width + 1 + indicator
            ] = val
        else:  # frame
            top, bottom = largest_h - height - indicator, largest_h - 1 - indicator
            left, right = indicator, width + indicator
            output_grid[top, left:right] = val
            output_grid[bottom, left:right] = val
            output_grid[top:bottom + 1, left] = val
            output_grid[top:bottom + 1, right] = val
            indicator += 1

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_6cbe9eb8(input_grid)
    return _result
