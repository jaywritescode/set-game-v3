import React from "react";
import classNames from "classnames";

import "./Card.css";

function Card(props) {
  const { card, isSelected, onClick } = props;

  return (
    <div
      className={classNames("card", "column", { isSelected })}
      style={{ backgroundImage: `url(cards/${card}.png)` }}
      onClick={onClick}
    />
  );
}

export default Card;
