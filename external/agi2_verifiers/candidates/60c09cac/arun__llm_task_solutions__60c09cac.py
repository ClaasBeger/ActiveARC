"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 60c09cac
source: ArunSehrawat/arc-agi2-solutions:llm
original_path: llm_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__llm_task_solutions__60c09cac
"""
from __future__ import annotations



import numpy as np

def solve_60c09cac(input_grid):
    """
    Concepts: integer scaling, pixel duplication

    Transformation steps:
    1. Replace each cell with a 2x2 block of the same color.
    """
    input_grid = np.array(input_grid)
    output_grid = np.kron(input_grid, np.ones((2, 2), dtype=int))
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_60c09cac(input_grid)
    return _result
