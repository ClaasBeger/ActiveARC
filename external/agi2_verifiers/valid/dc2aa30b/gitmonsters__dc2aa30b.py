"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: dc2aa30b
source: GitMonsters/SOLVED-562-verified
original_path: solves/dc2aa30b/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__dc2aa30b
"""
from __future__ import annotations



def solve(grid: list[list[int]]) -> list[list[int]]:
    """
    Solves dc2aa30b: Block sorting by 1-count.
    
    The 11x11 grid is divided into 9 3x3 blocks (with 0-separators at rows/cols 3,7).
    Blocks are sorted by 1-count descending, then rearranged in a snake pattern:
    - Position (0,0): rank 2,  (0,1): rank 1,  (0,2): rank 0
    - Position (1,0): rank 5,  (1,1): rank 4,  (1,2): rank 3
    - Position (2,0): rank 8,  (2,1): rank 7,  (2,2): rank 6
    """
    
    def get_block(grid, block_row, block_col):
        """Extract a 3x3 block from the grid."""
        result = []
        rows = [0, 1, 2] if block_row == 0 else ([4, 5, 6] if block_row == 1 else [8, 9, 10])
        cols = [0, 1, 2] if block_col == 0 else ([4, 5, 6] if block_col == 1 else [8, 9, 10])
        for r in rows:
            row = []
            for c in cols:
                row.append(grid[r][c])
            result.append(row)
        return result
    
    def set_block(grid, block_row, block_col, block):
        """Place a 3x3 block into the grid."""
        rows = [0, 1, 2] if block_row == 0 else ([4, 5, 6] if block_row == 1 else [8, 9, 10])
        cols = [0, 1, 2] if block_col == 0 else ([4, 5, 6] if block_col == 1 else [8, 9, 10])
        for i, r in enumerate(rows):
            for j, c in enumerate(cols):
                grid[r][c] = block[i][j]
    
    def count_ones(block):
        """Count 1s in a block."""
        flat = [x for row in block for x in row]
        return flat.count(1)
    
    # Extract all 9 blocks and sort by 1-count descending
    blocks = []
    for r in range(3):
        for c in range(3):
            block = get_block(grid, r, c)
            ones = count_ones(block)
            blocks.append((block, ones))
    
    blocks_sorted = sorted(blocks, key=lambda x: -x[1])
    
    # Create output grid with separators
    output = [[0]*11 for _ in range(11)]
    for i in range(11):
        output[3][i] = 0
        output[7][i] = 0
        output[i][3] = 0
        output[i][7] = 0
    
    # Place blocks in snake pattern
    placement = [
        (0, 0, 2), (0, 1, 1), (0, 2, 0),
        (1, 0, 5), (1, 1, 4), (1, 2, 3),
        (2, 0, 8), (2, 1, 7), (2, 2, 6),
    ]
    
    for out_r, out_c, rank in placement:
        set_block(output, out_r, out_c, blocks_sorted[rank][0])
    
    return output

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
