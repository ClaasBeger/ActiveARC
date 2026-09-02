"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 64a7c07e
source: GitMonsters/SOLVED-562-verified
original_path: solves/64a7c07e/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__64a7c07e
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    Shift 8s right based on row-band bounding box width.
    
    Rule: For each contiguous band of rows containing 8s,
    find the bounding box width (max_col - min_col + 1),
    and shift all 8s in that band right by that amount.
    """
    
    # Find all rows with 8s
    rows_with_8 = set()
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == 8:
                rows_with_8.add(r)
    
    if not rows_with_8:
        return grid
    
    # Group rows into contiguous bands
    sorted_rows = sorted(rows_with_8)
    bands = []
    current_band = [sorted_rows[0]]
    for r in sorted_rows[1:]:
        if r - current_band[-1] == 1:
            current_band.append(r)
        else:
            bands.append(current_band)
            current_band = [r]
    bands.append(current_band)
    
    # Compute shift for each band
    band_shifts = {}  # band_index -> shift_amount
    for band_idx, band in enumerate(bands):
        # Find bounding box for this band
        cols_in_band = set()
        for r in band:
            for c in range(len(grid[r])):
                if grid[r][c] == 8:
                    cols_in_band.add(c)
        
        if cols_in_band:
            min_col = min(cols_in_band)
            max_col = max(cols_in_band)
            width = max_col - min_col + 1
            band_shifts[band_idx] = width
    
    # Create output grid
    result = [row[:] for row in grid]
    
    # Clear original 8s
    for r in range(len(result)):
        for c in range(len(result[r])):
            if result[r][c] == 8:
                result[r][c] = 0
    
    # Shift each row band
    for band_idx, band in enumerate(bands):
        shift = band_shifts[band_idx]
        for r in band:
            for c in range(len(grid[r])):
                if grid[r][c] == 8:
                    new_c = c + shift
                    if 0 <= new_c < len(result[r]):
                        result[r][new_c] = 8
    
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
