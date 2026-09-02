"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 8dae5dfc
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__8dae5dfc
"""
from __future__ import annotations



import numpy as np

def solve_8dae5dfc(input_grid):
    """
    Transform nested rectangular frames by reversing their color values.
    
    Concepts:
    - Connected component analysis: Group adjacent non-zero cells, each group is made of nested rectangular frames
    - Pattern recognition: Identify nested rectangular frames colors (values)
    - Color transformation: Reverse the order of colors from outer to inner frame
    
    Transformation steps:
    1. Find connected components of non-zero values
    2. For each component:
        a. Extract the rectangular block containing the component
        b. Identify unique colors from outer to inner frame
        c. Reverse the color ordering and apply to frames
    
    """
    from grid_utils import group_connected_positions


    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()

    # Find connected components of non-zero values
    non_zero_positions = np.argwhere(input_grid != 0)
    connected_components = group_connected_positions(non_zero_positions)

    # Process each connected component
    for component in connected_components:
        # Get bounding box of component
        component = np.array(component)
        min_row, min_col = component.min(axis=0)
        max_row, max_col = component.max(axis=0)
        height = max_row - min_row + 1
        width = max_col - min_col + 1
        
        # Extract block containing the component
        block = input_grid[min_row:max_row + 1, min_col:max_col + 1]
        
        # Identify unique colors from outer to inner frames
        # Sample middle column from top to center to get frame colors
        frame_colors = []
        for row in range(height//2 + 1):
            color = block[row, width//2]
            if color not in frame_colors:
                frame_colors.append(color)
                
        # Reverse color ordering for transformation
        reversed_colors = frame_colors[::-1]
        
        # Apply reversed colors to each frame
        output_block = block.copy()
        for old_color, new_color in zip(frame_colors, reversed_colors):
            color_positions = np.argwhere(block == old_color)
            output_block[color_positions[:, 0], color_positions[:, 1]] = new_color
            
        # Update output grid with transformed block
        output_grid[min_row:max_row + 1, min_col:max_col + 1] = output_block

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_8dae5dfc(input_grid)
    return _result
