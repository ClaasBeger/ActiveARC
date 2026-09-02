"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: af726779
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__af726779
"""
from __future__ import annotations



import numpy as np

def solve_af726779(input_grid):
    """
    Creating inverted triangles of alternating colors (7 and 6).
   
    Concept:
    For each row containing a specific value (top_value), identify pairs of adjacent occurrences
    and place another value (bottom_value) two rows below in the middle column between those pairs.
    This process is repeated alternating between two different values.
   
    Transformation Steps:
    1. Scan the grid from bottom to top to find rows containing the target value (top_value)
    2. Identify pairs of adjacent occurrences of this value in the row
    3. For each pair, place another value (bottom_value) two rows below in the middle column
    4. Alternate this process between two different values (7→6 and 6→7)
    """
 
    # Convert input to numpy array if it's not already
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()
 
    def place_row_below(grid, top_value, bottom_value):
        """
        Find pairs of top_value in a row that is closest to the grid-bottom and place bottom_value two rows below.
 
        Args:
            grid: The current grid state
            top_value: The value to look for in rows
            bottom_value: The value to place two rows below
           
        Returns:
            Updated grid with new values placed
        """
        # Find the last row from bottom containing the top_value
        row_with_top_value_id = None
        for r in range(nrows-1, 0, -1):  # Scan from bottom to top
            if top_value in grid[r]:
                row_with_top_value_id = r
                break
               
        # If no row contains the top_value, return the grid unchanged
        if row_with_top_value_id is None:
            return grid
           
        # Get the row and positions of top_value in that row
        row_with_top_value = grid[row_with_top_value_id]
        positions = np.sort(np.where(row_with_top_value == top_value)[0])
 
        # Calculate target row for placement (two rows below)
        next_next_row_id = row_with_top_value_id + 2
       
        # Only proceed if the target row is within grid bounds
        if next_next_row_id < nrows:
            # For each pair of adjacent top_values, place bottom_value in between and two rows below
            for i in range(len(positions)-1):
                middle_cols = list(range(positions[i]+1, positions[i+1]))
                # Only place if there's exactly one column between the pair
                if len(middle_cols) == 1:
                    grid[next_next_row_id, middle_cols[0]] = bottom_value
                   
        return grid
 
    # Alternately apply the transformation for both value pairs 7->6 and 6->7 and so on
    for _ in range(nrows):
        output_grid = place_row_below(output_grid, top_value=7, bottom_value=6)
        output_grid = place_row_below(output_grid, top_value=6, bottom_value=7)
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_af726779(input_grid)
    return _result
