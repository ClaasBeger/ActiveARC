"""Auto-normalized ARC-AGI-2 verifier candidate.

task_id: e9b4f6fc
source: GitMonsters/SOLVED-562-verified
original_path: solves/e9b4f6fc/solver.py
license: NOASSERTION — GitMonsters/SOLVED-562-verified publishes no LICENSE file; retain upstream attribution and review before redistribution.
candidate_id: gitmonsters__e9b4f6fc
"""
from __future__ import annotations



"""
ARC-AGI puzzle e9b4f6fc solver.

Pattern: The grid contains one large rectangular region (the main pattern) and
several isolated 1x2 horizontal pairs (the color mapping legend). Each pair
(left=a, right=b) means: replace color b with color a in the main pattern.
The output is the main pattern with all substitutions applied.
"""

import json
import numpy as np
from collections import deque
from typing import List


def solve(grid: List[List[int]]) -> List[List[int]]:
    g = np.array(grid)
    rows, cols = g.shape

    # Find connected components of non-zero cells (4-connected)
    visited = np.zeros_like(g, dtype=bool)
    components: List[List[tuple]] = []

    for r in range(rows):
        for c in range(cols):
            if g[r, c] != 0 and not visited[r, c]:
                comp = []
                queue = deque([(r, c)])
                visited[r, c] = True
                while queue:
                    cr, cc = queue.popleft()
                    comp.append((cr, cc))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc] and g[nr, nc] != 0:
                            visited[nr, nc] = True
                            queue.append((nr, nc))
                components.append(comp)

    # Largest component is the main grid; rest are key pairs
    components.sort(key=len, reverse=True)
    main_comp = components[0]
    key_pairs = components[1:]

    # Extract main grid bounding box
    min_r = min(r for r, c in main_comp)
    max_r = max(r for r, c in main_comp)
    min_c = min(c for r, c in main_comp)
    max_c = max(c for r, c in main_comp)
    main_grid = g[min_r:max_r + 1, min_c:max_c + 1].copy()

    # Build color mapping from key pairs: pair (a, b) -> replace b with a
    mapping = {}
    for pair in key_pairs:
        pair.sort()
        r1, c1 = pair[0]
        r2, c2 = pair[1]
        a = int(g[r1, c1])  # left value
        b = int(g[r2, c2])  # right value
        mapping[b] = a

    # Apply mapping
    result = main_grid.copy()
    for old_val, new_val in mapping.items():
        result[main_grid == old_val] = new_val

    return result.tolist()

def verify(input_grid):
    """Normalized verifier entrypoint."""
    _result = solve(input_grid)
    return _result
