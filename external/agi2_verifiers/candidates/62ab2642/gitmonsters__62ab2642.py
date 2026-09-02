"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: 62ab2642
source: GitMonsters/SOLVED-562-verified
original_path: solves/62ab2642/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__62ab2642
"""
from __future__ import annotations



"""
ARC-AGI Solver for task 62ab2642

Rule: The 5-cells form a connected boundary. Among the connected components
of 0-cells (4-connectivity), the largest component is filled with 8 and
the smallest component is filled with 7. All other cells remain unchanged.
"""

def solve(grid: list[list[int]]) -> list[list[int]]:
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    components: list[list[tuple[int, int]]] = []

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0 and not visited[r][c]:
                comp: list[tuple[int, int]] = []
                stack = [(r, c)]
                visited[r][c] = True
                while stack:
                    cr, cc = stack.pop()
                    comp.append((cr, cc))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == 0:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                components.append(comp)

    sizes = [len(c) for c in components]
    max_idx = sizes.index(max(sizes))
    min_idx = sizes.index(min(sizes))

    result = [row[:] for row in grid]
    for r, c in components[max_idx]:
        result[r][c] = 8
    for r, c in components[min_idx]:
        result[r][c] = 7
    return result

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
