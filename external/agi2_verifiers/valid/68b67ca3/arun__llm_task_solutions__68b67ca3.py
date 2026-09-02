"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 68b67ca3
source: ArunSehrawat/arc-agi2-solutions:llm
original_path: llm_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__llm_task_solutions__68b67ca3
"""
from __future__ import annotations



import numpy as np

def solve_68b67ca3(input_grid):
    """
    Concepts: downsampling, even cells

    Transformation steps:
    1. Keep every other row and column, starting at (0, 0).
    """
    input_grid = np.array(input_grid)
    output_grid = input_grid[::2, ::2]
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_68b67ca3(input_grid)
    return _result
