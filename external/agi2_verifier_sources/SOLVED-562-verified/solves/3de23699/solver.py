from collections import Counter

def solve(grid):
    counts = Counter(v for row in grid for v in row if v)
    marker = next(color for color, count in counts.items() if count == 4)
    corners = [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == marker]
    rows = sorted({r for r, _ in corners})
    cols = sorted({c for _, c in corners})
    return [[marker if v not in (0, marker) else 0 for v in row[cols[0] + 1:cols[1]]] for row in grid[rows[0] + 1:rows[1]]]
