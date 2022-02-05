import React from "react";
import classNames from "classnames";

import "./Card.css";

function Card(props) {
  const { card, isSelected } = props;

  return (
    <div
      className={classNames("card", "column", { isSelected })}
      style={{ backgroundImage: `url(cards/${card}.png)` }}
    />
  );
}

export default Card;
