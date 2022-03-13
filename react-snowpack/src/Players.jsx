import React from "react";
import classNames from "classnames";
import { toPairs } from "ramda";

import "purecss";
import "./players.css";

export default function Players(props) {
  const { players, myName } = props;

  return (
    <div className="players pure-g">
      <div className="header pure-u-1">Players</div>
      {toPairs(players).map(([name, setsFound]) => (
        <li
          className={classNames("player", "pure-u-1-4", {
            myself: name == myName,
          })}
          key={name}
        >
          <span>{name}</span>
          <span>{setsFound.length}</span>
        </li>
      ))}
    </div>
  );
}
