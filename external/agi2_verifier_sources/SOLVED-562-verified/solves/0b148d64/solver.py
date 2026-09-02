from collections import Counter

def solve(grid):
    h, w = len(grid), len(grid[0])
    row_segs = []
    start = None
    for r in range(h):
        nz = any(grid[r][c] != 0 for c in range(w))
        if nz and start is None:
            start = r
        if not nz and start is not None:
            row_segs.append((start, r - 1))
            start = None
    if start is not None:
        row_segs.append((start, h - 1))
    col_segs = []
    start = None
    for c in range(w):
        nz = any(grid[r][c] != 0 for r in range(h))
        if nz and start is None:
            start = c
        if not nz and start is not None:
            col_segs.append((start, c - 1))
            start = None
    if start is not None:
        col_segs.append((start, w - 1))
    quads = []
    for rs, re in row_segs:
        for cs, ce in col_segs:
            sub = [row[cs:ce + 1] for row in grid[rs:re + 1]]
            counts = Counter(v for row in sub for v in row if v)
            dom = max(counts, key=counts.get) if counts else 0
            quads.append((dom, sub))
    doms = [dom for dom, _ in quads]
    target = next(dom for dom in doms if doms.count(dom) == 1)
    return next(sub for dom, sub in quads if dom == target)
