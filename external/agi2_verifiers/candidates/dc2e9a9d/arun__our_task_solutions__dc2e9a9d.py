"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: dc2e9a9d
source: ArunSehrawat/arc-agi2-solutions:our
original_path: our_task_solutions.py
license: MIT — ArunSehrawat/arc-agi2-solutions (LICENSE)
candidate_id: arun__our_task_solutions__dc2e9a9d
"""
from __future__ import annotations



import numpy as np

def solve_dc2e9a9d(input_grid):
    """
    Concepts:
    - Connected component detection (flood fill)
    - Symmetry-based reflection and value assignment

    Transformation steps:
    1. Find all connected components of cells with value 3.
    2. For each component, determine if the "extra" cell is along a row or column edge.
    3. Reflect the component across the axis opposite the extra cell, with an extra gap.
    4. Assign value 8 for row-based reflections, and 1 for column-based reflections.
    """
    input_grid = np.array(input_grid)
    output_grid = input_grid.copy()
    nrows, ncols = input_grid.shape
    visited = np.zeros_like(input_grid, dtype=bool)

    def get_component(r, c):
        """Return list of coordinates for connected 3's starting from (r, c)."""
        stack = [(r, c)]
        visited[r, c] = True
        coords = []
        while stack:
            rr, cc = stack.pop()
            coords.append((rr, cc))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = rr + dr, cc + dc
                if 0 <= nr < nrows and 0 <= nc < ncols:
                    if not visited[nr, nc] and input_grid[nr, nc] == 3:
                        visited[nr, nc] = True
                        stack.append((nr, nc))
        return coords

    # Step 1: Find all components of 3's
    components = []
    for r in range(nrows):
        for c in range(ncols):
            if not visited[r, c] and input_grid[r, c] == 3:
                components.append(get_component(r, c))

    # Step 2–4: Process each component
    for coords in components:
        rs = np.array([r for r, _ in coords])
        cs = np.array([c for _, c in coords])

        r_unique, r_counts = np.unique(rs, return_counts=True)
        c_unique, c_counts = np.unique(cs, return_counts=True)

        flag = None
        r_extra_cell = c_extra_cell = None

        if np.any(r_counts == 1):
            r_extra_cell = r_unique[r_counts == 1][0]
            c_extra_cell = cs[rs == r_extra_cell][0]
            flag = "extra cell (row) above or below"
        if np.any(c_counts == 1):
            c_extra_cell = c_unique[c_counts == 1][0]
            r_extra_cell = rs[cs == c_extra_cell][0]
            flag = "extra cell (column) left or right"

        rmin, rmax = rs.min(), rs.max()
        cmin, cmax = cs.min(), cs.max()

        # Decide reflection direction and compute target coordinates
        if flag == "extra cell (row) above or below":
            if r_extra_cell == rmin:
                # Extra cell above → mirror below with one extra row in between
                target_r = [rmax + 2 + (rmax - r) for r in rs]
                target_c = cs
            elif r_extra_cell == rmax:
                # Extra cell below → mirror above with one extra row in between
                target_r = [rmin - 2 - (r - rmin) for r in rs]
                target_c = cs
        elif flag == "extra cell (column) left or right":
            if c_extra_cell == cmin:
                # Extra cell left → mirror right with one extra column in between
                target_r = rs
                target_c = [cmax + 2 + (cmax - c) for c in cs]
            elif c_extra_cell == cmax:
                # Extra cell right → mirror left with one extra column in between
                target_r = rs
                target_c = [cmin - 2 - (c - cmin) for c in cs]
        else:
            continue  # Skip if no extra cell found

        # Apply mirrored values: 8 for row-based, 1 for column-based
        for rr, cc in zip(target_r, target_c):
            if 0 <= rr < nrows and 0 <= cc < ncols:
                if flag == "extra cell (row) above or below":
                    output_grid[rr, cc] = 8
                elif flag == "extra cell (column) left or right":
                    output_grid[rr, cc] = 1

    return output_grid

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve_dc2e9a9d(input_grid)
    return _result
