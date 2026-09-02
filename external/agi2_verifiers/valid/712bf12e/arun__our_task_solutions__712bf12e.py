"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 712bf12e
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__712bf12e
"""
from __future__ import annotations



import numpy as np

def solve_712bf12e(input_grid):
    """
    Simulates the movement (towards top or right) of entities (value 2) through a grid with empty spaces (value 0)
    and blockers (value 5).
   
    Concept:
    Entities move according to specific rules: first try to move upward, and if blocked,
    try to move right. Continue movement until getting stuck or hitting the top edge of the grid.
   
    Transformation Steps:
    1. Identify all entities (value 2) in the grid
    2. For each entity, simulate movement according to the rules:
       a. First try to move up one cell if empty (value 0)
       b. If blocked above (value 5), try to move right if empty
       c. If blocked in both directions, entity stops moving
    3. Continue movement until entity reaches top boundary or gets stuck
    """
 
    # Convert input to numpy array if it's not already
    input_grid = np.array(input_grid)
    nrows, ncols = input_grid.shape
    output_grid = input_grid.copy()
 
    def one_step_move(grid, start_pos):
        """
        Move an entity one step according to the movement rules.
       
        Args:
            grid: The current grid state
            start_pos: Current position of the entity (r, c)
           
        Returns:
            tuple: (updated_grid, new_position)
            - If the entity can move, updates the grid and returns new position
            - If the entity can't move, returns the original position
        """
        end_pos = None
        r, c = start_pos
       
        # First priority: Try to move up
        if r > 0 and grid[r-1, c] == 0:  # Empty cell above
            grid[r-1, c] = 2  # Move entity up
            end_pos = (r-1, c)
        # Second priority: If blocked above, try to move right
        elif r > 0 and grid[r-1, c] == 5:  # Blocker above
            # Try moving right if in bounds and empty
            if c+1 < ncols and grid[r, c+1] == 0:
                grid[r, c+1] = 2  # Move entity right
                end_pos = (r, c+1)
            else:  # Can't move - either out of bounds or blocked
                end_pos = (r, c)  # Stay in place
        else:  # Other scenarios (e.g., at top edge)
            end_pos = (r, c)  # Stay in place
           
        return grid, end_pos
 
    # Find all entities (value 2) in the grid
    entity_positions = np.argwhere(input_grid == 2)
   
    # Process each entity
    for pos in entity_positions:
        start_pos = tuple(pos)
       
        # Simulate movement (limit to maximum possible steps to avoid infinite loops)
        max_steps = nrows * ncols
        for _ in range(max_steps):
            # Remember original position to check if entity moved
            original_pos = start_pos
           
            # Move one step
            output_grid, end_pos = one_step_move(output_grid, start_pos)
           
            # Extract new position coordinates
            r_new, c_new = end_pos
           
            # Check termination conditions
            if end_pos == original_pos:  # No movement occurred
                break
            if r_new == 0:  # Reached the top edge
                break
               
            # Update starting position for next iteration
            start_pos = end_pos
 
    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_712bf12e(input_grid)
    return _result
