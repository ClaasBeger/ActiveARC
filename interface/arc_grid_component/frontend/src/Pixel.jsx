import React, { useState } from "react";
import { ARC_COLORS } from "./arcColors.js";
import "./styles/pixel.scss";

export default function Pixel(props) {
  const { selectedColor, draggingRef, changeColor, pixelColor } = props;
  const [dispPixelColor, setDispPixelColor] = useState(null);

  function resolvePenIndex() {
    const sel = String(selectedColor).toLowerCase();
    const palette = ARC_COLORS.map((c) => c.toLowerCase());
    let newIndex = palette.indexOf(sel);
    if (newIndex < 0) {
      newIndex = 0;
    }
    return newIndex;
  }

  function applyColor() {
    changeColor(resolvePenIndex());
    setDispPixelColor(null);
  }

  function changeColorOnMouseEnter() {
    if (draggingRef.current) {
      applyColor();
    } else {
      setDispPixelColor(selectedColor);
    }
  }

  function resetColor() {
    setDispPixelColor(null);
  }

  const backgroundColor =
    dispPixelColor == null ? ARC_COLORS[pixelColor] : dispPixelColor;

  return (
    <div
      className="pixel"
      onMouseDown={(e) => {
        if (e.button !== 0) return;
        e.preventDefault();
        draggingRef.current = true;
        applyColor();
      }}
      onMouseEnter={changeColorOnMouseEnter}
      onMouseLeave={resetColor}
      style={{ backgroundColor: backgroundColor }}
    />
  );
}
