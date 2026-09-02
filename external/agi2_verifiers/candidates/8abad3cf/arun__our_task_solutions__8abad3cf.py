"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 8abad3cf
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__8abad3cf
"""
from __future__ import annotations



import numpy as np

def solve_8abad3cf(input_grid):
    """
    Arranges non-background colors as squares in a horizontal row, sized by the square root of their frequency,
    with background separators, and flips the result vertically to match the expected orientation (so that they touch the bottom).
 
    Concept:
    - The grid contains a background color (most frequent) and other colors representing elements.
    - Each non-background color is represented as a square block, where the side length is the integer square root of its count.
    - Blocks are placed side by side with background separators, and the entire arrangement is flipped upside down.
 
    Transformation Steps:
    1. Identify unique colors and their frequencies in the input grid.
    2. Sort colors by frequency in ascending order.
    3. Determine the background color as the most frequent.
    4. For each non-background color, compute its block size as the integer square root of its count.
    5. Create a new grid with height equal to the largest block size and width as the sum of block sizes plus separators.
    6. Place each block in the grid with background spacing between them.
    7. Flip the grid vertically to achieve the final orientation (so that they touch the bottom).
    """
 
    input_grid = np.array(input_grid)
 
    # Get unique colors and their counts
    unique, counts = np.unique(input_grid, return_counts=True)
    order = np.argsort(counts)  # Sort by frequency ascending
 
    # Background is the most frequent color
    background_color = unique[order[-1]]
 
    # Non-background colors and their sizes
    colors = unique[order[:-1]]
    sizes = np.sqrt(counts[order[:-1]]).astype(int)
 
    if len(colors) == 0:
        return input_grid  # No non-background colors, return input
 
    # Compute output grid dimensions
    H = sizes[-1]  # Height is the largest size
    W = np.sum(sizes) + len(sizes) - 1  # Width includes spacing
    output_grid = np.full((H, W), background_color, dtype=int)
 
    # Place each color's block
    start_col = 0
    for i, (color, size) in enumerate(zip(colors, sizes)):
        if size > 0:
            output_grid[:size, start_col:start_col + size] = color
        start_col += size + 1  # Move to next position with spacing
 
    # Flip vertically to match expected output
    output_grid = np.flipud(output_grid)
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_8abad3cf(input_grid)
    return _result
