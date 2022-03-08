import React, { useReducer, useEffect, useState } from "react";
import classNames from "classnames";
import generate from "project-name-generator";
import {
  difference,
  F,
  includes,
  isEmpty,
  sortBy,
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
          ...action.payload,
        };
      }
      case "start":
        let { board } = action.payload;
        return {
          ...state,
          board: zipObj(board.map(cardToStr), board.map(F)),
        };
      case "select_card":
        let card = action.payload.card;
        return {
          ...state,
          board: {
            ...state.board,
            [card]: !state.board[card],
          },
        };
      case "submit":
        let current_board = Object.keys(state.board);
        let updated_board = action.payload.board.map(cardToStr);

        let r = difference(current_board, updated_board);
        let n = difference(updated_board, current_board);

        let newboard = current_board.map((k) =>
          includes(k, r) ? n.shift() : k
        );
        return {
          ...state,
          board: zipObj(newboard, newboard.map(F)),
          players: action.payload.players,
        };
    }
  }

  useEffect(function onJoinRoom() {
    console.debug("useEffect: page inited");

    websocket = new WebSocket("ws://localhost:3001");

    websocket.onopen = (e) => {
      console.log("[open] connection established");
      websocket.send(
        JSON.stringify({
          type: "joinRoom",
          payload: {
            playerName: state.playerName,
          },
        })
      );
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

  useEffect(
    function onCardSelected() {
      console.log("useEffect: card selected");

      const selected = toPairs(state.board)
        .filter(([_, isSelected]) => isSelected)
        .map(([card, _]) => card);
      if (selected.length == 3) {
        websocket.send(
          JSON.stringify({
            type: "submit",
            payload: {
              cards: selected.map(strToCard),
              player: state.playerName,
            },
          })
        );
      }
    },
    [state.board]
  );

  const onStartClicked = () => {
    websocket.send(
      JSON.stringify({
        type: "start",
        payload: {},
      })
    );
  };

  const onCardClicked = (card) => {
    console.log("onCardClicked: ", card);
    dispatch({
      type: "select_card",
      payload: { card },
    });
  };

  return (
    <>
      <menu>
        <div>
          <input
            id="high-contrast-mode"
            type="checkbox"
            className="switch"
            onClick={() => setHighContrastMode(!highContrastMode)}
          />
          <label htmlFor="high-contrast-mode">I'm colorblind!</label>
        </div>
      </menu>
      <div className="players">
        <h4>Players</h4>
        {sortBy(([_, setsFound]) => setsFound.length)(
          toPairs(state.players)
        ).map(([playerName, setsFound]) => (
          <li
            className={classNames("player", {
              myself: playerName == state.playerName,
            })}
            key={playerName}
          >
            <div>{playerName}</div>
            <div>{setsFound.length}</div>
          </li>
        ))}
      </div>

      <div
        className={classNames("board", "container", {
          "high-contrast-mode": highContrastMode,
        })}
      >
        {isEmpty(state.board) ? (
          <button onClick={onStartClicked}>start game</button>
        ) : (
          splitEvery(3, toPairs(state.board)).map((triple) => (
            <div className="pure-g card-row">
              {triple.map(([card, isSelected]) => (
                <Card
                  card={card}
                  key={card}
                  isSelected={isSelected}
                  onClick={() => onCardClicked(card)}
                />
              ))}
            </div>
          ))
        )}
      </div>
    </>
  );
}

export default App;
