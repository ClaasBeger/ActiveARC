"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e4075551
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[480](id=480)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0480__e4075551
"""
from __future__ import annotations



import numpy as np

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return grid

    h = len(grid)
    w = len(grid[0])

    # Find all colored positions
    positions = [(r, c) for r in range(h) for c in range(w) if grid[r][c] != 0]

    if not positions:
        return [row[:] for row in grid]

    # Find min and max row and col
    min_r = min(r for r, c in positions)
    max_r = max(r for r, c in positions)
    min_c = min(c for r, c in positions)
    max_c = max(c for r, c in positions)

    # Find center (position of 2)
    centers = [(r, c) for r, c in positions if grid[r][c] == 2]
    assert len(centers) == 1, "Exactly one center (color 2) expected"
    center_r, center_c = centers[0]

    # Find top color (unique colored cell in min_r)
    top_cs = [c for r, c in positions if r == min_r]
    assert len(top_cs) == 1, "Unique top seed expected"
    top_color = grid[min_r][top_cs[0]]

    # Find bottom color
    bottom_cs = [c for r, c in positions if r == max_r]
    assert len(bottom_cs) == 1
    bottom_color = grid[max_r][bottom_cs[0]]

    # Find left color
    left_rs = [r for r, c in positions if c == min_c]
    assert len(left_rs) == 1
    left_color = grid[left_rs[0]][min_c]

    # Find right color
    right_rs = [r for r, c in positions if c == max_c]
    assert len(right_rs) == 1
    right_color = grid[right_rs[0]][max_c]

    # Create output grid
    output = [[0] * w for _ in range(h)]

    # Draw top border
    for c in range(min_c, max_c + 1):
        output[min_r][c] = top_color

    # Draw bottom border
    for c in range(min_c, max_c + 1):
        output[max_r][c] = bottom_color

    # Draw left border
    for r in range(min_r + 1, max_r):
        output[r][min_c] = left_color

    # Draw right border
    for r in range(min_r + 1, max_r):
        output[r][max_c] = right_color

    # Draw vertical arm
    for r in range(min_r + 1, max_r):
        output[r][center_c] = 5

    # Draw horizontal arm
    for c in range(min_c + 1, max_c):
        output[center_r][c] = 5

    # Set center to 2
    output[center_r][center_c] = 2

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
