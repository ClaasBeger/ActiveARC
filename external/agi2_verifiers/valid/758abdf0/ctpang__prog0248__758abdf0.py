"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 758abdf0
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[248](id=248)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0248__758abdf0
"""
from __future__ import annotations



import numpy as np

import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    
    grid = np.array(grid)
    rows, cols = grid.shape
    
    # Find wall
    wall_type = None
    wall_pos = None
    for r in range(rows):
        if np.all(grid[r, :] == 0):
            wall_type = 'horizontal'
            wall_pos = r
            break
    if wall_type is None:
        for c in range(cols):
            if np.all(grid[:, c] == 0):
                wall_type = 'vertical'
                wall_pos = c
                break
    if wall_type is None:
        return grid.tolist()
    
    output = grid.copy()
    
    if wall_type == 'vertical':
        # Assume left wall
        start = wall_pos + 1
        field_size = cols - start
        for line in range(rows):
            seq = list(output[line, start: start + field_size])
            if len(seq) < 2:
                continue
            if seq[0] == 8:
                if seq[1] == 8:
                    seq[0] = 7
                    seq[1] = 7
                    if len(seq) >= 7:
                        seq[5] = 0
                        seq[6] = 0
                else:
                    seq[1] = 8
            output[line, start: start + field_size] = seq
    else:  # horizontal
        if wall_pos == 0:  # top
            direction = 1
            start = wall_pos + 1
            field_size = rows - start
        else:  # bottom
            direction = -1
            start = wall_pos - 1
            field_size = start + 1
        for line in range(cols):
            if direction == 1:
                seq = list(output[start: start + field_size, line])
            else:
                seq = []
                curr = start
                for _ in range(field_size):
                    seq.append(output[curr, line])
                    curr -= 1
            if len(seq) < 2:
                continue
            if seq[0] == 8:
                if seq[1] == 8:
                    seq[0] = 7
                    seq[1] = 7
                    if len(seq) >= 7:
                        seq[5] = 0
                        seq[6] = 0
                else:
                    seq[1] = 8
            if direction == 1:
                output[start: start + field_size, line] = seq
            else:
                idx = 0
                curr = start
                for _ in range(field_size):
                    output[curr, line] = seq[idx]
                    idx += 1
                    curr -= 1
    
    return output.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
