"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 92e50de0
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[303](id=303)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0303__92e50de0
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    grid = np.array(grid)
    h, w = grid.shape

    # Find full line rows and line_color
    line_rows = []
    for i in range(h):
        if np.all(grid[i] == grid[i][0]) and grid[i][0] != 0:
            line_rows.append(i)
    line_color = grid[line_rows[0]][0]

    # Spacing d
    line_rows = sorted(line_rows)
    d = line_rows[1] - line_rows[0]
    period = 2 * d

    # Find motif positions
    motif = []
    for i in range(h):
        for j in range(w):
            c = grid[i, j]
            if c != 0 and c != line_color:
                motif.append((i, j, c))

    min_r = min(i for i, j, c in motif)
    min_c = min(j for i, j, c in motif)

    rel_motif = [(i - min_r, j - min_c, c) for i, j, c in motif]

    # Row starts
    row_mod = min_r % period
    row_starts = list(range(row_mod, h, period))

    # Col starts
    col_mod = min_c % period
    col_starts = list(range(col_mod, w, period))

    # Copy grid
    new_grid = grid.copy()

    # Place replications
    for sr in row_starts:
        for sc in col_starts:
            for dr, dc, c in rel_motif:
                nr = sr + dr
                nc = sc + dc
                if 0 <= nr < h and 0 <= nc < w:
                    new_grid[nr, nc] = c

    return new_grid.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
