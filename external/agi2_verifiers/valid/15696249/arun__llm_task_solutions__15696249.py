"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 15696249
source: ArunSehrawat/arc-agi2-solutions:llm
original_path: llm_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__llm_task_solutions__15696249
"""
from __future__ import annotations



import numpy as np

def solve_15696249(input_grid):
    """
    Concepts: constant row/column, tiling, alignment

    Transformation steps:
    1. Find the fully constant row or column in the input.
    2. Tile the input three times along the perpendicular axis.
    3. Place that strip in the block whose index matches the constant line.
    """
    input_grid = np.array(input_grid)
    h, w = input_grid.shape
    output_grid = np.zeros((h * 3, w * 3), dtype=int)
    for i in range(h):
        if np.all(input_grid[i] == input_grid[i, 0]):
            output_grid[i * h:(i + 1) * h, :] = np.tile(input_grid, (1, 3))  # Steps 2–3: constant row
            return output_grid
    for j in range(w):
        if np.all(input_grid[:, j] == input_grid[0, j]):
            output_grid[:, j * w:(j + 1) * w] = np.tile(input_grid, (3, 1))  # Steps 2–3: constant column
            return output_grid
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_15696249(input_grid)
    return _result
