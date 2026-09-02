"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9c1e755f
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__9c1e755f
"""
from __future__ import annotations



import numpy as np

def solve_9c1e755f(input_grid):
    """
    Concepts: Block replication using guide row or column of a particular value (5).

    Steps:
    1. Identify connected blocks of non-zero cells, the process each block independently.
    2. For each block, detect whether 5s form a boundary row or column.
    3. Extract the interior piece (non-0, non-5 values).
    4. Replicate the piece across the block in the direction suggested by the 5s.
    """
    from grid_utils import group_connected_positions

    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    def fill_block(block):
        filled = block.copy()
        pos_5 = np.argwhere(block == 5)
        if pos_5.size == 0:
            return filled

        min_r5, min_c5 = pos_5.min(axis=0)
        max_r5, max_c5 = pos_5.max(axis=0)

        pos_core = np.argwhere((block != 0) & (block != 5))
        if pos_core.size == 0:
            return filled
        min_r, min_c = pos_core.min(axis=0)
        max_r, max_c = pos_core.max(axis=0)
        piece = block[min_r:max_r+1, min_c:max_c+1]

        h, w = piece.shape
        H, W = block.shape

        # Top row of 5s → tile piece downward
        if min_r5 == max_r5 == 0:
            reps = H // h
            tiled = np.tile(piece, (reps, W // w))[:H, :W]
            filled = np.vstack([block[min_r5, :].reshape(1, -1), tiled])

        # Bottom row of 5s → tile piece upward
        elif min_r5 == max_r5 == H - 1:
            reps = H // h
            tiled = np.tile(piece, (reps, W // w))[-H:, :W]
            filled = np.vstack([tiled, block[max_r5, :].reshape(1, -1)])

        # Left column of 5s → tile piece rightward
        elif min_c5 == max_c5 == 0:
            reps = W // w
            tiled = np.tile(piece, (H // h, reps))[:H, :W]
            filled = np.hstack([block[:, min_c5].reshape(-1, 1), tiled])

        # Right column of 5s → tile piece leftward
        elif min_c5 == max_c5 == W - 1:
            reps = W // w
            tiled = np.tile(piece, (H // h, reps))[:H, -W:]
            filled = np.hstack([tiled, block[:, max_c5].reshape(-1, 1)])

        return filled

    # Process each connected block
    for part in group_connected_positions(np.argwhere(input_grid != 0)):
        part = np.array(part)
        min_r, min_c = part.min(axis=0)
        max_r, max_c = part.max(axis=0)
        block = input_grid[min_r:max_r+1, min_c:max_c+1]
        filled_block = fill_block(block)
        output_grid[min_r:max_r+1, min_c:max_c+1] = filled_block

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_9c1e755f(input_grid)
    return _result
