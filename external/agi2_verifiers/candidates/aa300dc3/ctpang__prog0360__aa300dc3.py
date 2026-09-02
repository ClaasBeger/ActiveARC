"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: aa300dc3
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[360](id=360)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0360__aa300dc3
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = grid.shape
    max_zeros = -1
    candidates = []

    # Backslash diagonals (\): constant col - row = k
    for k in range(-rows + 1, cols):
        diag = []
        for r in range(rows):
            c = r + k
            if 0 <= c < cols:
                diag.append((r, c))
        if diag:
            count = sum(1 for r, c in diag if grid[r, c] == 0)
            length = len(diag)
            if count > max_zeros:
                max_zeros = count
                candidates = [diag]
            elif count == max_zeros:
                candidates.append(diag)

    # Forward slash diagonals (/): constant row + col = s
    for s in range(rows + cols - 1):
        diag = []
        for r in range(rows):
            c = s - r
            if 0 <= c < cols:
                diag.append((r, c))
        if diag:
            count = sum(1 for r, c in diag if grid[r, c] == 0)
            length = len(diag)
            if count > max_zeros:
                max_zeros = count
                candidates = [diag]
            elif count == max_zeros:
                candidates.append(diag)

    # Filter by max length
    if candidates:
        max_len = max(len(d) for d in candidates)
        candidates = [d for d in candidates if len(d) == max_len]

    # Assume unique after filters; pick the first if multiple
    if not candidates:
        return grid.tolist()
    chosen_diag = candidates[0]

    # Create output
    output = grid.copy()
    for r, c in chosen_diag:
        if grid[r, c] == 0:
            output[r, c] = 8

    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
