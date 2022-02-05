import React, { useReducer, useEffect, useState } from "react";
import classNames from "classnames";
import { F, isEmpty, partial, splitEvery, toPairs, zipObj } from "ramda";
import Card from "./Card";

import "./App.css";
import "milligram";

let websocket;

function App() {
  const [state, dispatch] = useReducer(reducer, { board: Object.create(null) });

  const [highContrastMode, setHighContrastMode] = useState(false);

  function reducer(state, action) {
    switch (action.type) {
      case "init":
      case "start":
        return { board: zipObj(action.board, action.board.map(F)) };
      case "select_card":
        let newVal = !state.board[action.card];
        return {
          board: {
            ...state.board,
            [action.card]: newVal,
          },
        };
    }
  }

  useEffect(() => {
    console.log("useEffect: page inited");

    websocket = new WebSocket("ws://localhost:3001");

    websocket.onopen = (e) => {
      console.log("[open] connection established");
      websocket.send(JSON.stringify({ type: "init" }));
    };

    websocket.onmessage = (e) => {
      console.log(`message received from server: ${e.data}`);
      const response = JSON.parse(e.data);

      dispatch(response);
    };

    websocket.onclose = (e) => {
      if (e.wasClean) {
        console.log(
          `[close] connection closed cleanly, code=${e.code}, reason=${e.reason}`
        );
      } else {
        console.error("[close] connection died");
      }
    };

    websocket.onerror = (err) => {
      console.error("[error]: ", err.message);
    };

    return () => websocket.close(1000, "Done");
  }, []);

  useEffect(() => {
    console.log("useEffect: card selected");

    const selected = toPairs(state.board)
      .filter(([_, isSelected]) => isSelected)
      .map(([card, _]) => card);
    if (selected.length == 3) {
      websocket.send(
        JSON.stringify({
          type: "submit",
          cards: selected,
        })
      );
    }
  }, [state.board]);

  const onStartClicked = () => {
    console.log("onStartClicked");
    websocket.send(JSON.stringify({ type: "start" }));
  };

  const onCardClicked = (card) => {
    console.log("onCardClicked: ", card);
    dispatch({
      type: "select_card",
      card,
    });
  };

  return (
    <div
      className={classNames("app", { "high-contrast-mode": highContrastMode })}
    >
      <input
        id="high-contrast-mode"
        type="checkbox"
        onClick={() => setHighContrastMode(!highContrastMode)}
      />
      <label htmlFor="high-contrast-mode">I'm colorblind!</label>
      <div className="board container">
        {isEmpty(state.board) ? (
          <button onClick={onStartClicked}>start game</button>
        ) : (
          splitEvery(3, toPairs(state.board)).map((triple) => (
            <div className="row card-row">
              {triple.map(([card, isSelected]) => (
                <Card
                  card={card}
                  isSelected={isSelected}
                  onClick={() => onCardClicked(card)}
                />
              ))}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;
