"""Solver for ARC task 2dd70a9a.

Rule (induced from the grid, not memorised):

* The grid holds a two-cell 3 marker and a two-cell 2 marker, plus 8 obstacles.
* A ray of 3s leaves the 3 marker along the marker's own axis, heading towards
  the 2 marker.
* The ray runs straight until the next cell is occupied, then turns 90 degrees,
  always picking the turn that closes the remaining gap to the 2 marker (and
  falling back to the other turn if that one is blocked).
* It stops on reaching the 2 marker. Every cell it crossed becomes a 3.
"""

from typing import List, Tuple

Grid = List[List[int]]


def _cells(grid: Grid, colour: int) -> List[Tuple[int, int]]:
    return [(r, c)
            for r, row in enumerate(grid)
            for c, v in enumerate(row)
            if v == colour]


def _sign(n: float) -> int:
    return (n > 0) - (n < 0)


def solve(grid: Grid) -> Grid:
    rows, cols = len(grid), len(grid[0])
    out = [row[:] for row in grid]

    source = _cells(grid, 3)
    target = _cells(grid, 2)
    if not source or not target:
        return out

    tr = sum(r for r, _ in target) / len(target)
    tc = sum(c for _, c in target) / len(target)

    # The marker's own axis sets the launch direction; it points at the target.
    axis = (1, 0) if len({c for _, c in source}) == 1 else (0, 1)
    sr = sum(r for r, _ in source) / len(source)
    sc = sum(c for _, c in source) / len(source)
    towards = _sign(tr - sr) if axis == (1, 0) else _sign(tc - sc)

    def run_length(step: Tuple[int, int]) -> int:
        head = max(source, key=lambda p: p[0] * step[0] + p[1] * step[1])
        n = 0
        while True:
            head = (head[0] + step[0], head[1] + step[1])
            if not (0 <= head[0] < rows and 0 <= head[1] < cols):
                return n
            if grid[head[0]][head[1]] != 0:
                return n
            n += 1

    if towards:
        direction = (axis[0] * towards, axis[1] * towards)
    else:
        # Target sits square-on to the marker, so head down the clearer run.
        forward = axis
        backward = (-axis[0], -axis[1])
        direction = max((forward, backward), key=run_length)

    # Launch from whichever marker cell is furthest along that direction.
    head = max(source, key=lambda p: p[0] * direction[0] + p[1] * direction[1])

    for _ in range(rows * cols):
        nr, nc = head[0] + direction[0], head[1] + direction[1]
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
            head = (nr, nc)
            out[nr][nc] = 3
            continue
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 2:
            return out

        # Blocked: turn 90 degrees, preferring the way that closes the gap.
        if direction[0]:
            options = [(0, _sign(tc - head[1])), (0, -_sign(tc - head[1]))]
        else:
            options = [(_sign(tr - head[0]), 0), (-_sign(tr - head[0]), 0)]

        for turn in options:
            if turn == (0, 0):
                continue
            nr, nc = head[0] + turn[0], head[1] + turn[1]
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] in (0, 2):
                direction = turn
                break
        else:
            return out

    return out


if __name__ == "__main__":
    import json
    import sys

    with open(sys.argv[1]) as fh:
        task = json.load(fh)
    for split in ("train", "test"):
        for i, pair in enumerate(task[split]):
            got = solve(pair["input"])
            print(f"{split}[{i}]: {'PASS' if got == pair['output'] else 'FAIL'}")
