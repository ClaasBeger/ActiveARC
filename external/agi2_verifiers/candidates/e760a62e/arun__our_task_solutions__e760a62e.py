"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e760a62e
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__e760a62e
"""
from __future__ import annotations



import numpy as np

def solve_e760a62e(input_grid):
    """
    Concepts: grid partitioning with connectors.

    Steps:
    1. Find the first row and column fully filled with 8s (block size).
    2. Partition the grid into blocks of this size.
    3. Identify blocks containing 2 or 3.
    4. Connect same-valued blocks horizontally/vertically by filling paths.
    5. Overlaps of 2 and 3 become 6.
    """

    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()
    nrows, ncols = input_grid.shape

    # Step 1: Block size from fully-8 row/col
    first_row_8 = next(r for r in range(nrows) if np.all(input_grid[r, :] == 8))
    first_col_8 = next(c for c in range(ncols) if np.all(input_grid[:, c] == 8))
    block_h, block_w = first_row_8, first_col_8

    # Step 2: Partition grid into blocks
    blocks_with_2, blocks_with_3 = [], []
    for r in range(0, nrows, block_h + 1):
        for c in range(0, ncols, block_w + 1):
            block = input_grid[r:r + block_h, c:c + block_w]
            if np.any(block == 2):
                blocks_with_2.append((r, c))
            elif np.any(block == 3):
                blocks_with_3.append((r, c))

    def fill_blocks(grid, val, block_corners):
        filled = []
        for (r, c) in block_corners:
            for (rr, cc) in block_corners:
                if r == rr and c != cc:  # horizontal connection
                    for cc_ in range(min(c, cc), max(c, cc) + 1, block_w + 1):
                        grid[r:r + block_h, cc_:cc_ + block_w] = val
                        filled.append((r, cc_))
                elif c == cc and r != rr:  # vertical connection
                    for rr_ in range(min(r, rr), max(r, rr) + 1, block_h + 1):
                        grid[rr_:rr_ + block_h, c:c + block_w] = val
                        filled.append((rr_, c))
        return grid, set(filled)

    # Step 3: Connect blocks with 2s and 3s
    output_grid, corners_2 = fill_blocks(output_grid, 2, blocks_with_2)
    output_grid, corners_3 = fill_blocks(output_grid, 3, blocks_with_3)

    # Step 4: Overlapping connections → 6
    for (r, c) in corners_2 & corners_3:
        output_grid[r:r + block_h, c:c + block_w] = 6

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_e760a62e(input_grid)
    return _result
