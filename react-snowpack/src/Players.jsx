import React from "react";
import classNames from "classnames";
import { toPairs } from "ramda";

export default function Players(props) {
  const { players, myName } = props;

  return (
    <div className="players">
      <h4>Players</h4>
      {toPairs(players).map(([name, setsFound]) => (
        <li
          className={classNames("player", {
            myself: name == myName,
          })}
          key={name}
        >
          <div>{name}</div>
          <div>{setsFound.length}</div>
        </li>
      ))}
    </div>
  );
}
