"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 0692e18c
source: ArunSehrawat/arc-agi2-solutions:llm
original_path: llm_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__llm_task_solutions__0692e18c
"""
from __future__ import annotations



import numpy as np

def solve_0692e18c(input_grid):
    """
    Concepts: fractal copy, color inversion, indicator cells

    Transformation steps:
    1. Build a color-inverted copy of the input (nonzero becomes 0, 0 becomes the sprite color).
    2. Scale the canvas by the input size.
    3. Where the input cell is nonzero, paste the inverted sprite into that block.
    """
    input_grid = np.array(input_grid)
    h, w = input_grid.shape
    color = int(next(c for c in np.unique(input_grid) if c != 0))
    inverted = np.where(input_grid == 0, color, 0)                  # Step 1: invert colors
    output_grid = np.zeros((h * h, w * w), dtype=int)               # Step 2: scaled canvas
    for i in range(h):
        for j in range(w):
            if input_grid[i, j] != 0:                               # Step 3: paste on nonzero cells
                output_grid[i * h:(i + 1) * h, j * w:(j + 1) * w] = inverted
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_0692e18c(input_grid)
    return _result
