"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: baf41dbf
source: GitMonsters/SOLVED-562-verified
original_path: solves/baf41dbf/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__baf41dbf
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    Extend rectangle to include markers.
    Preserve both row and column dividers.
    """
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    
    result = [row[:] for row in grid]
    
    # Find shape and markers
    shape_cells = set()
    markers = []
    
    for r in range(height):
        for c in range(width):
            if grid[r][c] == 3:
                shape_cells.add((r, c))
            elif grid[r][c] == 6:
                markers.append((r, c))
    
    if not shape_cells:
        return result
    
    # Get current bounds
    shape_rows = [r for r, c in shape_cells]
    shape_cols = [c for r, c in shape_cells]
    
    old_min_row, old_max_row = min(shape_rows), max(shape_rows)
    old_min_col, old_max_col = min(shape_cols), max(shape_cols)
    
    # Determine new bounds based on markers
    new_min_row = old_min_row
    new_max_row = old_max_row
    new_min_col = old_min_col
    new_max_col = old_max_col
    
    changed = True
    while changed:
        changed = False
        for mr, mc in markers:
            # If marker row is within CURRENT rect rows, extend horizontally
            if new_min_row <= mr <= new_max_row:
                if mc < new_min_col - 1:
                    new_min_col = mc + 1
                    changed = True
                elif mc > new_max_col + 1:
                    new_max_col = mc - 1
                    changed = True
            # If marker col is within CURRENT rect cols, extend vertically
            if new_min_col <= mc <= new_max_col:
                if mr < new_min_row - 1:
                    new_min_row = mr + 1
                    changed = True
                elif mr > new_max_row + 1:
                    new_max_row = mr - 1
                    changed = True
    
    # Find columns that are completely filled in original rect (dividers)
    filled_cols = set()
    for c in range(old_min_col, old_max_col + 1):
        if all((r, c) in shape_cells for r in range(old_min_row, old_max_row + 1)):
            filled_cols.add(c)
    
    divider_cols = filled_cols - {old_min_col, old_max_col}
    
    # Find rows that are completely filled in original rect (dividers)
    filled_rows = set()
    for r in range(old_min_row, old_max_row + 1):
        if all((r, c) in shape_cells for c in range(old_min_col, old_max_col + 1)):
            filled_rows.add(r)
    
    divider_rows = filled_rows - {old_min_row, old_max_row}
    
    # Draw new rectangle
    for r in range(new_min_row, new_max_row + 1):
        for c in range(new_min_col, new_max_col + 1):
            # Top and bottom edges
            if r == new_min_row or r == new_max_row:
                result[r][c] = 3
            # Left and right edges
            elif c == new_min_col or c == new_max_col:
                result[r][c] = 3
            # Interior dividers (rows)
            elif r in divider_rows:
                result[r][c] = 3
            # Interior dividers (columns)
            elif c in divider_cols:
                result[r][c] = 3
            else:
                # Interior empty space
                result[r][c] = 0
    
    # Preserve 6s
    for mr, mc in markers:
        result[mr][mc] = 6
    
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
