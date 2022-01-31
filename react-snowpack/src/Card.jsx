import React from "react";

import "./Card.css";
import "./sprites.css";

function Card(props) {
  return (
    <div className={`card ${props.card}`}></div>
  )
}

export default Card;