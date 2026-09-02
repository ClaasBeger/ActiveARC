"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 9841fdad
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[318](id=318)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0318__9841fdad
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    output = [row[:] for row in grid]

    # Border color B
    B = grid[0][0]

    # Find all columns that are entirely B
    full_B_cols = []
    for c in range(cols):
        if all(grid[r][c] == B for r in range(rows)):
            full_B_cols.append(c)

    # Assuming three: left (0), sep, right (cols-1)
    if len(full_B_cols) != 3:
        return grid  # Unexpected, return unchanged
    sep = full_B_cols[1]  # The middle one

    L_start = 1
    L_end = sep - 1
    R_start = sep + 1
    R_end = cols - 2
    background = 1  # Hardcoded as per examples

    # Inner rows
    for i in range(1, rows - 1):
        # Find segments in left
        j = L_start
        while j <= L_end:
            if grid[i][j] == background:
                j += 1
                continue
            # Start of segment
            S = j
            C = grid[i][j]
            while j <= L_end and grid[i][j] == C:
                j += 1
            E = j - 1
            # Now process segment S to E, color C
            left_off = S - L_start
            right_off = L_end - E
            length = E - S + 1
            if left_off == 1 and right_off == 1:
                # Stretch
                start_r = R_start + 1
                end_r = R_end - 1
                for k in range(start_r, end_r + 1):
                    output[i][k] = C
            elif left_off == 1:
                # Left align
                start_r = R_start + 1
                end_r = start_r + length - 1
                if end_r <= R_end:
                    for k in range(start_r, end_r + 1):
                        output[i][k] = C
            elif right_off == 1:
                # Right align
                end_r = R_end - 1
                start_r = end_r - length + 1
                if start_r >= R_start:
                    for k in range(start_r, end_r + 1):
                        output[i][k] = C

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
