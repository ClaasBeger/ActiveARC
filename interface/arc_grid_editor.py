"""Streamlit bridge to the arc-app pixel editor (vendored React bundle)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components

from framework.grids import Grid

_BUILD_DIR = Path(__file__).resolve().parent / "arc_grid_component" / "build"
_INDEX = _BUILD_DIR / "index.html"

if _INDEX.exists():
    _arc_grid_component = components.declare_component(
        "activearc_arc_grid",
        path=str(_BUILD_DIR),
    )
else:
    _arc_grid_component = None


def arc_grid_editor_available() -> bool:
    return _arc_grid_component is not None


def arc_grid_editor(grid: Grid, *, key: str) -> Any:
    """Pixel editor matching arc-app; returns updated grid or *default* if unchanged.

    If the frontend bundle is not built (``npm run build`` in
    ``interface/arc_grid_component/frontend``), returns ``None`` so callers
    can fall back to another editor.
    """
    if _arc_grid_component is None:
        return None
    return _arc_grid_component(grid=grid, key=key, default=grid)
