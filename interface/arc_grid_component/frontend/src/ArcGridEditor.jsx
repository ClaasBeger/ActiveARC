/**
 * Single-grid pixel editor using arc-app Pixel / Row (victorvikram/arc-app).
 */
import React, {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import { CirclePicker } from "react-color";
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import { ARC_COLORS } from "./arcColors.js";
import Row from "./Row.jsx";
import "./styles/pixel.scss";
import "./styles/row.scss";
import "./styles/editor_embed.scss";

function cloneGrid(g) {
  if (!g || !g.length) return [[0]];
  return g.map((row) => [...row]);
}

function normalizeGrid(g) {
  const copy = cloneGrid(g);
  const h = copy.length;
  if (h === 0) return [[0]];
  let w = 0;
  for (let r = 0; r < h; r++) {
    w = Math.max(w, copy[r]?.length ?? 0);
  }
  if (w === 0) return [[0]];
  for (let r = 0; r < h; r++) {
    const row = copy[r] ?? [];
    const next = [];
    for (let c = 0; c < w; c++) {
      let v = row[c];
      if (typeof v !== "number" || !Number.isFinite(v)) v = 0;
      v = Math.round(v);
      if (v < 0) v = 0;
      if (v > 9) v = 9;
      next.push(v);
    }
    copy[r] = next;
  }
  return copy;
}

function gridsEqual(a, b) {
  if (a.length !== b.length) return false;
  for (let r = 0; r < a.length; r++) {
    if (a[r].length !== b[r].length) return false;
    for (let c = 0; c < a[r].length; c++) {
      if (a[r][c] !== b[r][c]) return false;
    }
  }
  return true;
}

function ArcGridEditor({ args, disabled }) {
  const incoming = normalizeGrid(args.grid ?? [[0]]);
  const incomingJson = JSON.stringify(incoming);
  const [grid, setGrid] = useState(() => cloneGrid(incoming));
  const gridRef = useRef(grid);
  const draggingRef = useRef(false);
  /** JSON we last pushed to Streamlit; ignore stale `args` until this round-trips. */
  const pendingJsonRef = useRef(null);

  useLayoutEffect(() => {
    gridRef.current = grid;
  }, [grid]);

  // Merge props from Python without clobbering local edits before Streamlit round-trips.
  useEffect(() => {
    const normalized = normalizeGrid(args.grid ?? [[0]]);
    const j = JSON.stringify(normalized);

    if (pendingJsonRef.current !== null) {
      if (j === pendingJsonRef.current) {
        pendingJsonRef.current = null;
        return;
      }
      // Parent props can still be one frame behind our commit — do not revert to stale grid.
      if (!gridsEqual(normalized, gridRef.current)) {
        return;
      }
      pendingJsonRef.current = null;
      return;
    }

    if (gridsEqual(gridRef.current, normalized)) {
      return;
    }
    const copy = cloneGrid(normalized);
    gridRef.current = copy;
    setGrid(copy);
  }, [incomingJson, args.grid]);

  const [penColor, setPenColor] = useState(ARC_COLORS[0]);

  // Dimension fields: edit freely; apply on blur so typing "15" does not briefly become "1" rows.
  const [dimH, setDimH] = useState(String(incoming.length));
  const [dimW, setDimW] = useState(String(incoming[0]?.length ?? 1));

  useEffect(() => {
    setDimH(String(grid.length));
    setDimW(String(grid[0]?.length ?? 1));
  }, [grid]);

  const h = grid.length;
  const w = grid[0]?.length ?? 0;

  useEffect(() => {
    const gridPx = Math.max(120, h * (24 + 2));
    const paletteH = 140;
    Streamlit.setFrameHeight(gridPx + paletteH);
  }, [h, w]);

  const pushToStreamlit = useCallback(
    (next) => {
      if (disabled) return;
      const norm = normalizeGrid(next);
      const j = JSON.stringify(norm);
      pendingJsonRef.current = j;
      gridRef.current = norm;
      setGrid(norm);
      Streamlit.setComponentValue(norm);
    },
    [disabled]
  );

  const resizeTo = useCallback(
    (newH, newW) => {
      const nh = Math.max(1, Math.min(32, Math.round(newH)));
      const nw = Math.max(1, Math.min(32, Math.round(newW)));
      const base = gridRef.current;
      const next = [];
      const prevH = base.length;
      const prevW = prevH > 0 ? base[0].length : 0;
      for (let r = 0; r < nh; r++) {
        const row = [];
        const rowLen = r < prevH && base[r] ? base[r].length : 0;
        for (let c = 0; c < nw; c++) {
          if (r < prevH && c < rowLen) {
            row.push(base[r][c]);
          } else {
            row.push(0);
          }
        }
        next.push(row);
      }
      pushToStreamlit(next);
    },
    [pushToStreamlit]
  );

  const setPixel = useCallback(
    (r, c, colorIndex) => {
      const base = gridRef.current;
      if (r < 0 || c < 0 || r >= base.length || c >= (base[0]?.length ?? 0)) {
        return;
      }
      const next = cloneGrid(base);
      let idx = colorIndex;
      if (typeof idx !== "number" || !Number.isFinite(idx)) idx = 0;
      idx = Math.round(idx);
      if (idx < 0) idx = 0;
      if (idx > 9) idx = 9;
      next[r][c] = idx;
      pushToStreamlit(next);
    },
    [pushToStreamlit]
  );

  useEffect(() => {
    const stop = () => {
      draggingRef.current = false;
    };
    window.addEventListener("mouseup", stop);
    window.addEventListener("blur", stop);
    return () => {
      window.removeEventListener("mouseup", stop);
      window.removeEventListener("blur", stop);
    };
  }, []);

  const startStroke = () => {
    draggingRef.current = true;
  };

  const circleSize = 28;
  const circleSpacing = 14;

  const applyDimInputs = () => {
    const nh = parseInt(dimH, 10);
    const nw = parseInt(dimW, 10);
    resizeTo(
      Number.isFinite(nh) ? nh : gridRef.current.length,
      Number.isFinite(nw) ? nw : gridRef.current[0]?.length ?? 1
    );
  };

  return (
    <div className="activearc-wrap">
      <div className="activearc-option">
        <label htmlFor="arc-h">Height (rows)</label>
        <input
          id="arc-h"
          type="number"
          className="activearc-panel-input"
          min={1}
          max={32}
          value={dimH}
          disabled={disabled}
          onChange={(e) => setDimH(e.target.value)}
          onBlur={applyDimInputs}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.target.blur();
            }
          }}
        />
        <label htmlFor="arc-w">Width (cols)</label>
        <input
          id="arc-w"
          type="number"
          className="activearc-panel-input"
          min={1}
          max={32}
          value={dimW}
          disabled={disabled}
          onChange={(e) => setDimW(e.target.value)}
          onBlur={applyDimInputs}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.target.blur();
            }
          }}
        />
      </div>
      <div className="activearc-palette">
        <CirclePicker
          color={penColor}
          colors={ARC_COLORS}
          onChangeComplete={(color) => setPenColor(color.hex)}
          width={ARC_COLORS.length * (circleSize + circleSpacing)}
          circleSize={circleSize}
          circleSpacing={circleSpacing}
        />
      </div>
      <div
        id="activearc-pixels"
        role="application"
        tabIndex={0}
        onMouseDownCapture={(e) => {
          if (e.button !== 0) return;
          startStroke();
        }}
      >
        {grid.map((row, ri) => (
          <Row
            key={ri}
            width={row.length}
            selectedColor={penColor}
            draggingRef={draggingRef}
            pixelColors={row}
            changeColor={(col, idx) => setPixel(ri, col, idx)}
          />
        ))}
      </div>
    </div>
  );
}

export default withStreamlitConnection(ArcGridEditor);
