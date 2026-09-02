"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 8abad3cf
source: epang080516/arc_agi:saved_library_1000.pkl
original_path: saved_library_1000.pkl#primitives[284](id=284)
license: NOASSERTION — epang080516/arc_agi (CT Pang) publishes no top-level LICENSE; retain upstream attribution and review before redistribution.
candidate_id: ctpang__prog0284__8abad3cf
"""
from __future__ import annotations



import numpy as np

from collections import Counter

def transform(grid: list[list[int]]) -> list[list[int]]:
    if not grid or not grid[0]:
        return []

    # Count frequencies
    flat = [cell for row in grid for cell in row]
    counts = Counter(flat)

    # Main color: max count
    main_color = max(counts, key=counts.get)

    # Non-main perfect squares
    non_main_perfect = {}
    for colr, cnt in counts.items():
        if colr != main_color and cnt > 0:
            s = int(cnt ** 0.5)
            if s * s == cnt:
                non_main_perfect[colr] = s

    if not non_main_perfect:
        return grid  # Or handle, but assume there are

    # Max side
    max_side = max(non_main_perfect.values())

    # Large color: assume unique, take the min color if multiple
    large_colors = [c for c, s in non_main_perfect.items() if s == max_side]
    large_color = min(large_colors)  # To handle potential multiple, pick smallest color

    # Small: others
    small_list = [(c, s) for c, s in non_main_perfect.items() if s < max_side]
    small_list.sort(key=lambda x: x[1])  # Sort by side ascending

    # Dimensions
    height = max_side
    left_width = sum(s + 1 for _, s in small_list)
    total_width = left_width + max_side

    # Create output filled with main
    output = [[main_color for _ in range(total_width)] for _ in range(height)]

    # Place small
    current_col = 0
    for c, s in small_list:
        place_start_col = current_col
        place_start_row = height - s
        for r in range(place_start_row, height):
            for cc in range(place_start_col, place_start_col + s):
                output[r][cc] = c
        current_col += s + 1

    # Place large
    large_start_col = left_width
    for r in range(height):
        for cc in range(large_start_col, large_start_col + max_side):
            output[r][cc] = large_color

    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = transform(input_grid)
    return _result
