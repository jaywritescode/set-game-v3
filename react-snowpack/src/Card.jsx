import React from "react";

import "./Card.css";


function Card(props) {
  const style={
    backgroundImage: `url(cards/${props.card}.png)`
  };

  return (
    <div className="card column" style={style} />
  )
}

export default Card;