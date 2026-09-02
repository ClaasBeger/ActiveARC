"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 626c0bcc
source: GitMonsters/SOLVED-562-verified
original_path: solves/626c0bcc/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__626c0bcc
"""
from __future__ import annotations



def solve(grid):
    rows, cols = len(grid), len(grid[0])
    cells = set()
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 8:
                cells.add((r, c))

    # Generate all possible pieces from every 2x2 block
    pieces = []
    for r in range(rows - 1):
        for c in range(cols - 1):
            block = [(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)]
            in_shape = [p for p in block if p in cells]

            if len(in_shape) == 4:
                pieces.append(('square', frozenset(in_shape), None))
                for missing in block:
                    remaining = frozenset(p for p in block if p != missing)
                    mr, mc = missing
                    if mr == r and mc == c: corner = 'TL'
                    elif mr == r and mc == c + 1: corner = 'TR'
                    elif mr == r + 1 and mc == c: corner = 'BL'
                    else: corner = 'BR'
                    pieces.append(('L', remaining, corner))
            elif len(in_shape) == 3:
                missing = [p for p in block if p not in cells][0]
                mr, mc = missing
                if mr == r and mc == c: corner = 'TL'
                elif mr == r and mc == c + 1: corner = 'TR'
                elif mr == r + 1 and mc == c: corner = 'BL'
                else: corner = 'BR'
                pieces.append(('L', frozenset(in_shape), corner))

    cell_to_pieces = {}
    for i, (ptype, pcells, corner) in enumerate(pieces):
        for c in pcells:
            cell_to_pieces.setdefault(c, []).append(i)

    covered = set()
    tiling = []

    def backtrack():
        uncovered = cells - covered
        if not uncovered:
            return True
        best_cell = None
        best_count = float('inf')
        for cell in uncovered:
            count = sum(1 for pi in cell_to_pieces.get(cell, [])
                        if not pieces[pi][1].intersection(covered))
            if count == 0:
                return False
            if count < best_count:
                best_count = count
                best_cell = cell

        for pi in cell_to_pieces.get(best_cell, []):
            ptype, pcells, corner = pieces[pi]
            if not pcells.intersection(covered):
                covered.update(pcells)
                tiling.append((ptype, pcells, corner))
                if backtrack():
                    return True
                tiling.pop()
                covered.difference_update(pcells)
        return False

    backtrack()

    color_map = {'TL': 2, 'TR': 4, 'BL': 3, 'BR': 1}
    result = [[0] * cols for _ in range(rows)]
    for ptype, pcells, corner in tiling:
        color = 1 if ptype == 'square' else color_map[corner]
        for r, c in pcells:
            result[r][c] = color
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
