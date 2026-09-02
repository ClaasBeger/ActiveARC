"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 516b51b7
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__516b51b7
"""
from __future__ import annotations



import numpy as np

def solve_516b51b7(input_grid):
    """
    Find rectangles of connected 1s and convert them into nested frames with alternating values.
    
    Concepts:
    - Rectangle detection: Identify boundaries of connected 1s in input grid
    - Frame generation: Create concentric frames with alternating value pattern
    - Pattern application: Apply values 1->2->3->2 from outside to inside
    
    Transformation steps:
    1. Convert input to numpy array
    2. Find positions of all 1s in the grid
    3. Group connected 1s into rectangles
    4. For each rectangle:
       a. Determine boundaries (min/max row/column)
       b. Calculate how many nested frames fit inside
       c. Fill frames from outside to inside with pattern [1,2,3,2]
    5. Return the transformed grid
    """
    from grid_utils import group_connected_positions
    
    # Convert input to numpy array and initalize empty ouput grid 
    input_grid = np.array(input_grid)
    output_grid = np.zeros_like(input_grid)
    
    # Find positions of 1s
    one_positions = np.argwhere(input_grid == 1)
    if len(one_positions) == 0:
        return output_grid
        
    # Group connected 1s into rectangles
    groups = group_connected_positions(one_positions)
    
    # Process each rectangle
    for group in groups:
        group = np.array(group)
        
        # Find rectangle boundaries
        min_row, min_col = group.min(axis=0)
        max_row, max_col = group.max(axis=0)
        
        # Calculate dimensions
        height = max_row - min_row + 1
        width = max_col - min_col + 1
        
        # Create nested frames
        num_layers = (min(height, width) + 1) // 2
        frame_values = [1, 2, 3, 2]  # Pattern to repeat
        
        # Fill frames from outside to inside
        for layer in range(num_layers):
            value = frame_values[layer % len(frame_values)]
            
            # Top and bottom edges
            output_grid[min_row + layer, min_col + layer:max_col - layer + 1] = value
            output_grid[max_row - layer, min_col + layer:max_col - layer + 1] = value
            
            # Left and right edges
            output_grid[min_row + layer:max_row - layer + 1, min_col + layer] = value
            output_grid[min_row + layer:max_row - layer + 1, max_col - layer] = value

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_516b51b7(input_grid)
    return _result
