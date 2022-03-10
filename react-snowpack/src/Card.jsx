import React from "react";
import classNames from "classnames";

import "./Card.css";

function Card(props) {
  const { card, isSelected, onClick } = props;

  return (
    <div className="card-container pure-u-1-3">
      <div
        className={classNames("card", { isSelected })}
        style={{ backgroundImage: `url(/cards/${card}.png)` }}
        onClick={onClick}
      />
    </div>
  );
}

export default Card;
