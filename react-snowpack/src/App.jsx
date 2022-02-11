import React, { useReducer, useEffect, useState } from "react";
import classNames from "classnames";
import generate from "project-name-generator";
import {
  difference,
  F,
  includes,
  isEmpty,
  splitEvery,
  toLower,
  toPairs,
  toUpper,
  zipObj,
} from "ramda";
import Card from "./Card";

import "./App.css";
import "purecss";

let websocket;

const cardToStr = ({ number, color, shading, shape }) => {
  return [number, color, shading, shape].map(toLower).join("-");
};

const strToCard = (string) => {
  return zipObj(
    ["number", "color", "shading", "shape"],
    string.split("-").map(toUpper)
  );
};

function App() {
  const [state, dispatch] = useReducer(reducer, { 
    board: Object.create(null),
    playerName: generate().dashed,
    players: [],
  });

  const [highContrastMode, setHighContrastMode] = useState(false);

  function reducer(state, action) {
    switch (action.type) {
      case "joinRoom": {
        return {
          ...state,
          ...action.payload
        };
      }
      case "start":
        return {
          ...state,
          board: zipObj(action.board.map(cardToStr), action.board.map(F)),
        };
      case "select_card":
        let newVal = !state.board[action.card];
        return {
          ...state,
          board: {
            ...state.board,
            [action.card]: newVal,
          },
        };
      case "submit":
        console.log(action);
        let current_board = Object.keys(state.board);
        let updated_board = action.board.map(cardToStr);

        let r = difference(current_board, updated_board);
        let n = difference(updated_board, current_board);

        let newboard = current_board.map((k) =>
          includes(k, r) ? n.shift() : k
        );
        return { 
          ...state, 
          board: zipObj(newboard, newboard.map(F)) 
        };
    }
  }

  useEffect(function onJoinRoom () {
    console.debug("useEffect: page inited");

    websocket = new WebSocket("ws://localhost:3001");

    websocket.onopen = (e) => {
      console.log("[open] connection established");
      websocket.send(JSON.stringify({ 
        type: "joinRoom",
        payload: {
          playerName: state.playerName,
        }
      }));
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
          cards: selected.map(strToCard),
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
      <div>
        <h4>Players</h4>
        <ul>
          {Object.keys(state.players).map(playerName => (
            <li className={classNames('player', { myself: playerName == state.playerName })} key={playerName}>{playerName}</li>
          ))}
        </ul>
      </div>
      
      <p>
        Your id: {state.playerName}
      </p>
      <div className="board container">
        {isEmpty(state.board) ? (
          <button onClick={onStartClicked}>start game</button>
        ) : (
          splitEvery(3, toPairs(state.board)).map((triple) => (
            <div className="pure-g card-row">
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
