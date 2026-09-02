"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 13713586
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[28](id=28)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0028__13713586
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid
    height = len(grid)
    width = len(grid[0])
    output = [row[:] for row in grid]

    # Detect border
    direction = None
    border_pos = None
    if all(grid[r][0] == 5 for r in range(height)):
        direction = 'left'
        border_pos = 0
    elif all(grid[r][width - 1] == 5 for r in range(height)):
        direction = 'right'
        border_pos = width - 1
    elif all(grid[0][c] == 5 for c in range(width)):
        direction = 'up'
        border_pos = 0
    elif all(grid[height - 1][c] == 5 for c in range(width)):
        direction = 'down'
        border_pos = height - 1

    if direction is None:
        return output  # No border, no change

    # Find bars
    bars = []
    if direction in ['left', 'right']:
        # Vertical bars
        for c in range(width):
            r = 0
            while r < height:
                if grid[r][c] == 0 or grid[r][c] == 5:
                    r += 1
                    continue
                color = grid[r][c]
                r_start = r
                r += 1
                while r < height and grid[r][c] == color:
                    r += 1
                r_end = r - 1
                bars.append({'pos': c, 'start': r_start, 'end': r_end, 'color': color})
    else:
        # Horizontal bars
        for r in range(height):
            c = 0
            while c < width:
                if grid[r][c] == 0 or grid[r][c] == 5:
                    c += 1
                    continue
                color = grid[r][c]
                c_start = c
                c += 1
                while c < width and grid[r][c] == color:
                    c += 1
                c_end = c - 1
                bars.append({'pos': r, 'start': c_start, 'end': c_end, 'color': color})

    # Compute distances
    for bar in bars:
        if direction == 'right':
            bar['dist'] = border_pos - bar['pos']
        elif direction == 'left':
            bar['dist'] = bar['pos'] - border_pos
        elif direction == 'down':
            bar['dist'] = border_pos - bar['pos']
        elif direction == 'up':
            bar['dist'] = bar['pos'] - border_pos

    # Sort by decreasing distance
    bars.sort(key=lambda b: -b['dist'])

    # Paint in order
    for bar in bars:
        color = bar['color']
        if direction in ['left', 'right']:
            if direction == 'right':
                col_start = bar['pos']
                col_end = border_pos - 1
            else:
                col_start = border_pos + 1
                col_end = bar['pos']
            for cc in range(col_start, col_end + 1):
                for rr in range(bar['start'], bar['end'] + 1):
                    output[rr][cc] = color
        else:
            if direction == 'down':
                row_start = bar['pos']
                row_end = border_pos - 1
            else:
                row_start = border_pos + 1
                row_end = bar['pos']
            for rr in range(row_start, row_end + 1):
                for cc in range(bar['start'], bar['end'] + 1):
                    output[rr][cc] = color

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
