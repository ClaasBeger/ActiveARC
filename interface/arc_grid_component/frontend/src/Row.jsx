import React from "react";
import "./styles/row.scss";
import Pixel from "./Pixel.jsx";

export default function Row(props) {
  const {
    width,
    selectedColor,
    draggingRef,
    changeColor,
    pixelColors,
  } = props;
  const pixels = [];

  for (let j = 0; j < width; j++) {
    pixels.push(
      <Pixel
        key={j}
        selectedColor={selectedColor}
        draggingRef={draggingRef}
        changeColor={(newVal) => changeColor(j, newVal)}
        pixelColor={pixelColors[j]}
      />
    );
  }

  return <div className="row">{pixels}</div>;
}
