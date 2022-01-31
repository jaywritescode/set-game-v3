import React from "react";

import "./Card.css";
import "./sprites.css";

function Card(props) {
  return (
    <div className={`card ${props.card}`} onClick={props.onClick}></div>
  )
}

export default Card;