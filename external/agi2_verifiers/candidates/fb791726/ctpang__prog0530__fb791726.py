"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: fb791726
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[530](id=530)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0530__fb791726
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    n = len(grid)
    if n == 0:
        return []
    # Find color c and positions
    positions = []
    c = None
    for i in range(n):
        for j in range(n):
            if grid[i][j] != 0:
                if c is None:
                    c = grid[i][j]
                positions.append((i, j))
    # Group by column
    from collections import defaultdict
    col_rows = defaultdict(list)
    for r, col in positions:
        col_rows[col].append(r)
    # Get motifs
    motifs = []
    for col, rows in col_rows.items():
        rows.sort()
        if len(rows) != 2 or rows[1] != rows[0] + 2:
            continue  # Assume valid
        start_r = rows[0]
        motifs.append((start_r, col))
    # Sort by start_r
    motifs.sort()
    k = len(motifs)
    if k == 0:
        return [[0] * (2 * n) for _ in range(2 * n)]
    d = n // k
    # Base
    s0, c0 = motifs[0]
    # Output
    out_n = 2 * n
    output = [[0] * out_n for _ in range(out_n)]
    num_motifs_out = 2 * k
    for j in range(num_motifs_out):
        sj = s0 + j * d
        cj = c0 + j * d
        if sj + 2 < out_n and cj < out_n:
            output[sj][cj] = c
            output[sj + 2][cj] = c
            for col in range(out_n):
                output[sj + 1][col] = 3
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
