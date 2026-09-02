"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ef26cbf6
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[516](id=516)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0516__ef26cbf6
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    rows, cols = grid.shape
    # Find full yellow rows
    yellow_rows = [r for r in range(rows) if np.all(grid[r] == 4)]
    # Find full yellow columns
    yellow_cols = [c for c in range(cols) if np.all(grid[:, c] == 4)]
    num_yr = len(yellow_rows)
    num_yc = len(yellow_cols)
    output = grid.copy()
    if num_yr > num_yc:
        # Row sections
        dividers = sorted(yellow_rows)
        section_starts = [0] + [d + 1 for d in dividers]
        section_ends = dividers + [rows]
        for start, end in zip(section_starts, section_ends):
            if start >= end:
                continue
            subgrid = grid[start:end, :]
            colors = set(subgrid.flatten())
            candidates = colors - {0, 1, 4}
            if len(candidates) == 1:
                C = candidates.pop()
                for r in range(start, end):
                    for c in range(cols):
                        if grid[r, c] == 1:
                            output[r, c] = C
    elif num_yc > num_yr:
        # Column sections
        dividers = sorted(yellow_cols)
        section_starts = [0] + [d + 1 for d in dividers]
        section_ends = dividers + [cols]
        for start, end in zip(section_starts, section_ends):
            if start >= end:
                continue
            subgrid = grid[:, start:end]
            colors = set(subgrid.flatten())
            candidates = colors - {0, 1, 4}
            if len(candidates) == 1:
                C = candidates.pop()
                for c in range(start, end):
                    for r in range(rows):
                        if grid[r, c] == 1:
                            output[r, c] = C
    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
