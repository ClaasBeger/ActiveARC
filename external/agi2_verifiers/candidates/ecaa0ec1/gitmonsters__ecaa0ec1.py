"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: ecaa0ec1
source: GitMonsters/SOLVED-562-verified
original_path: solves/ecaa0ec1/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__ecaa0ec1
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    Solution for ARC puzzle ecaa0ec1.
    
    Rule:
    1. Find all color 4 cells in the input grid
    2. Find the pattern region (non-zero, non-4 cells)
    3. Determine rotation based on which quadrant (relative to pattern center) has most 4s:
       - Most 4s in TL or TR quadrant -> rotate 270°
       - Most 4s in BL quadrant -> keep or rotate 90° depending on pattern
       - Most 4s in BR quadrant -> rotate 90°
    4. Apply rotation to the pattern
    5. Place rotated pattern at original position
    6. Place single 4 at the corner of the output pattern that corresponds to the 4-dominated quadrant
    """
    # Find all 4s
    four_pos = [(r, c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c] == 4]
    
    if len(four_pos) < 2:
        return [row[:] for row in grid]
    
    # Find pattern region (non-zero, non-4 cells)
    non_zero = [(r, c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c] not in [0, 4]]
    
    if not non_zero:
        return [row[:] for row in grid]
    
    r_min, r_max = min(p[0] for p in non_zero), max(p[0] for p in non_zero)
    c_min, c_max = min(p[1] for p in non_zero), max(p[1] for p in non_zero)
    
    # Create output grid
    output = [[0] * len(grid[0]) for _ in range(len(grid))]
    
    # Extract pattern region
    h, w = r_max - r_min + 1, c_max - c_min + 1
    pattern = [[grid[r_min+r][c_min+c] for c in range(w)] for r in range(h)]
    
    # Determine which quadrant has the most 4s (relative to pattern center in input)
    pattern_center_r = (r_min + r_max) // 2
    pattern_center_c = (c_min + c_max) // 2
    
    tl = sum(1 for r, c in four_pos if r < pattern_center_r and c < pattern_center_c)
    tr = sum(1 for r, c in four_pos if r < pattern_center_r and c >= pattern_center_c)
    bl = sum(1 for r, c in four_pos if r >= pattern_center_r and c < pattern_center_c)
    br = sum(1 for r, c in four_pos if r >= pattern_center_r and c >= pattern_center_c)
    
    # Rotation logic
    def rotate_180(grid):
        h, w = len(grid), len(grid[0])
        return [[grid[h-1-r][w-1-c] for c in range(w)] for r in range(h)]
    
    def rotate_90(grid):
        h, w = len(grid), len(grid[0])
        return [[grid[h-1-c][r] for c in range(h)] for r in range(w)]
    
    def rotate_270(grid):
        h, w = len(grid), len(grid[0])
        return [[grid[c][w-1-r] for c in range(h)] for r in range(w)]
    
    # Determine rotation based on 4 positions in input
    if tl > 0 and br > 0 and tr == 0 and bl == 0:
        # TL-BR opposite diagonal
        rotated = rotate_180(pattern)
    elif tl > 0 and bl > 0 and tr == 0 and br == 0:
        # TL-BL same side (left)
        rotated = rotate_270(pattern)
    elif tl > 0 and tr > 0 and bl == 0 and br == 0:
        # TL-TR same side (top)
        rotated = rotate_270(pattern)
    elif tl > 0 and (tr > 0 or bl > 0) and br == 0:
        # TL with TR or BL
        rotated = rotate_270(pattern)
    elif br > 0 and tr > 0 and tl == 0 and bl == 0:
        # BR-TR same side (right)
        rotated = rotate_90(pattern)
    elif br > 0 and bl > 0 and tl == 0 and tr == 0:
        # BR-BL same side (bottom)
        rotated = rotate_90(pattern)
    elif br > 0 and (tr > 0 or bl > 0) and tl == 0:
        # BR with TR or BL
        rotated = rotate_90(pattern)
    elif tr > 0 and bl > 0 and tl == 0 and br == 0:
        # TR-BL opposite diagonal
        rotated = rotate_180(pattern)
    elif bl > 0:
        # BL dominant
        rotated = rotate_270(pattern)
    else:
        rotated = pattern
    
    # Place rotated pattern back
    for r in range(h):
        for c in range(w):
            if rotated[r][c] != 0:
                output[r_min+r][c_min+c] = rotated[r][c]
    
    # Determine where to place the single 4 (at the corner with most input 4s)
    # Place it one cell away from the pattern in the dominant direction
    if tl >= max(tr, bl, br):
        four_row, four_col = r_min - 1, c_min - 1
    elif tr > max(tl, bl, br):
        four_row, four_col = r_min - 1, c_max + 1
    elif bl > max(tl, tr, br):
        four_row, four_col = r_max + 1, c_min - 1
    else:  # br dominant
        four_row, four_col = r_max + 1, c_max + 1
    
    # Place 4 if within bounds
    if 0 <= four_row < len(output) and 0 <= four_col < len(output[0]):
        output[four_row][four_col] = 4
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
