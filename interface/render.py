from __future__ import annotations

from html import escape
from typing import Optional

from framework.grids import Grid

_SYMBOL_TO_COLOR = {
    0: "#000000",
    1: "#0074D9",
    2: "#FF4136",
    3: "#2ECC40",
    4: "#FFDC00",
    5: "#AAAAAA",
    6: "#F012BE",
    7: "#FF851B",
    8: "#7FDBFF",
    9: "#870C25",
}


def _cell_size_px(grid: Grid, max_px: int = 26) -> int:
    h = max(1, len(grid))
    w = max(1, len(grid[0]))
    return int(max(6, min(max_px, 360 / max(h, w))))


def grid_height_px(grid: Grid, *, max_px: int = 26) -> int:
    h = len(grid) or 1
    size = _cell_size_px(grid, max_px=max_px)
    return int(h * size + 80)


def grid_html(
    grid: Grid,
    *,
    show_numbers: bool = False,
    title: str | None = None,
    max_px: int = 26,
    border_color: Optional[str] = None,
    border_width_px: int = 1,
) -> str:
    size = _cell_size_px(grid, max_px=max_px)
    h = len(grid)
    w = len(grid[0]) if h else 0

    title_html = ""
    if title is not None:
        title_html = f"<div class='arc-grid-title'>{escape(title)}</div>"

    rows: list[str] = []
    for r in range(h):
        cells: list[str] = []
        for c in range(w):
            sym = int(grid[r][c])
            color = _SYMBOL_TO_COLOR.get(sym, "#000000")
            text = str(sym) if show_numbers else ""
            cells.append(
                "<div class='arc-cell' "
                f"style='background:{color};width:{size}px;height:{size}px'>"
                f"{escape(text)}</div>"
            )
        rows.append("<div class='arc-row'>" + "".join(cells) + "</div>")

    style = """
<style>
.arc-grid-wrap { margin: 0.25rem 0 0.75rem 0; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
.arc-grid-title { font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem; opacity: 0.85; }
.arc-grid { display: inline-block; border: 1px solid rgba(120,120,120,0.6); background: rgba(0,0,0,0.2); }
.arc-row { display: flex; }
.arc-cell {
  box-sizing: border-box;
  border-right: 1px solid rgba(85,85,85,0.75);
  border-bottom: 1px solid rgba(85,85,85,0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  line-height: 1;
  color: rgba(255,255,255,0.9);
  user-select: none;
}
.arc-row:last-child .arc-cell { border-bottom: 0; }
.arc-cell:last-child { border-right: 0; }
</style>
"""

    grid_border_style = ""
    if border_color is not None:
        grid_border_style = (
            f" style='border:{border_width_px}px solid {escape(border_color)};'"
        )

    return (
        style
        + "<div class='arc-grid-wrap'>"
        + f"{title_html}"
        + f"<div class='arc-grid'{grid_border_style}>"
        + "".join(rows)
        + "</div></div>"
    )
