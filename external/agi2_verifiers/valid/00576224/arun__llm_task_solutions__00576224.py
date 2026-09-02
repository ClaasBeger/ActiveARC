"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 00576224
source: ArunSehrawat/arc-agi2-solutions:llm
original_path: llm_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__llm_task_solutions__00576224
"""
from __future__ import annotations



import numpy as np

def solve_00576224(input_grid):
    """
    Concepts: tiling, horizontal flip, alternating rows of tiles

    Transformation steps:
    1. Repeat the input three times horizontally.
    2. Stack that strip three times, flipping the middle strip left-right.
    """
    input_grid = np.array(input_grid)
    rows = []
    for i in range(3):
        block = input_grid if i % 2 == 0 else np.fliplr(input_grid)  # Step 2: flip odd strips
        rows.append(np.tile(block, (1, 3)))                         # Step 1: tile horizontally
    output_grid = np.vstack(rows)
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_00576224(input_grid)
    return _result
