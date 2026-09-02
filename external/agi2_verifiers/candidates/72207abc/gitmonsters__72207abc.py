"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 72207abc
source: GitMonsters/SOLVED-562-verified
original_path: solves/72207abc/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__72207abc
"""
from __future__ import annotations



def solve(grid):
    """Colors placed at positions with increasing gaps in the middle row.
    
    Initial non-zero values define the color sequence. Gaps between placements
    increase by 1 each step. Colors cycle through the sequence.
    """
    out = [row[:] for row in grid]
    middle = 1  # always the middle row of 3 rows

    # Collect initial non-zero values and their positions
    colors = []
    positions = []
    for c in range(len(grid[middle])):
        if grid[middle][c] != 0:
            colors.append(grid[middle][c])
            positions.append(c)

    if len(positions) < 2:
        return out

    # Determine the starting gap increment
    # Gaps between initial positions: e.g., positions [0, 1, 3] have gaps [1, 2]
    gaps = [positions[i+1] - positions[i] for i in range(len(positions) - 1)]
    # The gap increment is 1 each time; next gap = last_gap + 1
    last_gap = gaps[-1] if gaps else 0
    last_pos = positions[-1]
    color_idx = 0  # cycle through colors starting from the beginning

    width = len(grid[middle])
    gap = last_gap + 1
    pos = last_pos
    while True:
        pos += gap
        if pos >= width:
            break
        out[middle][pos] = colors[color_idx % len(colors)]
        color_idx += 1
        gap += 1

    return out

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
