"""Solver for ARC task b1fc8b8e.

Rule (induced from the grid, not memorised):

* The output is a fixed 5x5 frame: four 2x2 quadrants separated by an empty
  row and an empty column, so it holds at most 16 cells.
* The number of coloured cells is conserved -- the output paints exactly as
  many cells as the input contains. Every example splits evenly across the
  four quadrants, so each quadrant receives count // 4 cells.
* Quadrants fill from the bottom row upwards and from the outer column
  inwards, which is what makes the partially-filled quadrant an L.
"""

from typing import List

Grid = List[List[int]]

# Fill order inside a 2x2 quadrant: bottom row first, then the outer column.
FILL_ORDER = ((1, 0), (1, 1), (0, 1), (0, 0))


def solve(grid: Grid) -> Grid:
    colours = [v for row in grid for v in row if v]
    if not colours:
        return [[0] * 5 for _ in range(5)]

    colour = max(set(colours), key=colours.count)
    per_quadrant = len(colours) // 4

    quadrant = [[0, 0], [0, 0]]
    for r, c in FILL_ORDER[:per_quadrant]:
        quadrant[r][c] = colour

    out = [[0] * 5 for _ in range(5)]
    for qr in (0, 1):
        for qc in (0, 1):
            for r in (0, 1):
                for c in (0, 1):
                    out[qr * 3 + r][qc * 3 + c] = quadrant[r][c]
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
