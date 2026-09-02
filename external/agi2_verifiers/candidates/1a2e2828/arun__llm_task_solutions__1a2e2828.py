"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 1a2e2828
source: ArunSehrawat/arc-agi2-solutions:llm
original_path: llm_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__llm_task_solutions__1a2e2828
"""
from __future__ import annotations



import numpy as np

def solve_1a2e2828(input_grid):
    """
    Concepts: full row/column, unique divider color

    Transformation steps:
    1. Find a row that is a single nonzero color across its full width, or a column that is a single nonzero color across its full height.
    2. Return that color as a 1x1 grid.
    """
    input_grid = np.array(input_grid)
    for row in input_grid:
        if row[0] != 0 and np.all(row == row[0]):
            output_grid = np.array([[int(row[0])]])
            return output_grid
    for col in input_grid.T:
        if col[0] != 0 and np.all(col == col[0]):
            output_grid = np.array([[int(col[0])]])
            return output_grid
    output_grid = np.array([[0]])
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_1a2e2828(input_grid)
    return _result
