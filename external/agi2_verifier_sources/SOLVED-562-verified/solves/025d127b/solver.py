from collections import Counter

def _components(cells, diag):
    cells = set(cells)
    steps = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if diag:
        steps += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    out = []
    while cells:
        start = cells.pop()
        stack = [start]
        comp = {start}
        while stack:
            r, c = stack.pop()
            for dr, dc in steps:
                nxt = (r + dr, c + dc)
                if nxt in cells:
                    cells.remove(nxt)
                    stack.append(nxt)
                    comp.add(nxt)
        out.append(comp)
    return out


def solve(grid):
    h, w = len(grid), len(grid[0])
    bg = Counter(v for row in grid for v in row).most_common(1)[0][0]
    seen = set()
    objects = []
    for r in range(h):
        for c in range(w):
            color = grid[r][c]
            if color == bg or (r, c) in seen:
                continue
            cells = set()
            stack = [(r, c)]
            seen.add((r, c))
            while stack:
                i, j = stack.pop()
                cells.add((i, j))
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        if di == dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < h and 0 <= nj < w and grid[ni][nj] == color and (ni, nj) not in seen:
                            seen.add((ni, nj))
                            stack.append((ni, nj))
            objects.append((color, cells))
    out = [row[:] for row in grid]
    for color, cells in objects:
        for r, c in cells:
            out[r][c] = bg
        parts = _components(cells, False)
        anchor = max(parts, key=lambda part: max(c for _, c in part))
        moved = set(anchor)
        for part in parts:
            if part is anchor:
                continue
            for r, c in part:
                moved.add((r, c + 1))
        for r, c in moved:
            out[r][c] = color
    return out
