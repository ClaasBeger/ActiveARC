"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 1d61978c
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__1d61978c
"""
from __future__ import annotations



import numpy as np

def solve_1d61978c(input_grid):
    """
    Concepts: Connected component analysis, mathematical property detection, component labeling.

    Steps:
    1. Find all connected groups of cells with value 5 (using 8-connectivity).
    2. For each group:
       - If its size is a power of an integer (a^b, a > 1, b > 1) or exactly 2, set those cells to 2.
       - Otherwise, set those cells to 8.
    """
    from grid_utils import group_connected_positions

    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    positions = np.argwhere(input_grid == 5)
    parts = group_connected_positions(positions, connectivity=8)

    def is_power(n):
        """Check if n is a power a^b with a > 1, b > 1."""
        if n <= 1:
            return False
        max_base = int(np.sqrt(n)) + 1
        for base in range(2, max_base + 1):
            exp = np.round(np.log(n) / np.log(base))
            if base ** exp == n and exp > 1:
                return True
        return False

    for part in parts:
        part = np.array(part)
        n = len(part)
        output_grid[part[:, 0], part[:, 1]] = 2 if is_power(n) or n == 2 else 8

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_1d61978c(input_grid)
    return _result
