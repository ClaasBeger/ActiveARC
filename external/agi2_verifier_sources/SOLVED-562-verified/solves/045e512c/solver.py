from collections import Counter

def solve(grid):
    h, w = len(grid), len(grid[0])
    bg = Counter(v for row in grid for v in row).most_common(1)[0][0]
    dirs8 = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]
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
                for dr, dc in dirs8:
                    ni, nj = i + dr, j + dc
                    if 0 <= ni < h and 0 <= nj < w and grid[ni][nj] == color and (ni, nj) not in seen:
                        seen.add((ni, nj))
                        stack.append((ni, nj))
            objects.append(cells)
    template = max(objects, key=len)
    rows = [r for r, _ in template]
    cols = [c for _, c in template]
    th = max(rows) - min(rows) + 1
    tw = max(cols) - min(cols) + 1
    out = [row[:] for row in grid]
    for dr, dc in dirs8:
        step = (0 if dr == 0 else dr * (th + 1), 0 if dc == 0 else dc * (tw + 1))
        probe = [(r + step[0], c + step[1]) for r, c in template if 0 <= r + step[0] < h and 0 <= c + step[1] < w]
        colors = {grid[r][c] for r, c in probe if grid[r][c] != bg}
        if not colors:
            continue
        color = next(iter(colors))
        k = 1
        while True:
            coords = [(r + step[0] * k, c + step[1] * k) for r, c in template]
            inside = [(r, c) for r, c in coords if 0 <= r < h and 0 <= c < w]
            if not inside:
                break
            for r, c in inside:
                out[r][c] = color
            k += 1
    return out
