import React, { useState, useReducer, useEffect, useCallback } from "react";
import classNames from "classnames";
import generate from "project-name-generator";
import {
  concat,
  difference,
  isEmpty,
  splitEvery,
  toLower,
  toUpper,
  without,
  zipObj,
} from "ramda";
import useWebSocket, { ReadyState } from "react-use-websocket";

import Card from "./Card";
import Players from "./Players";

import "./App.css";
import "purecss";

const MAX_PLAYERS = 4;

const playerName = generate().dashed;

const cardToStr = ({ number, color, shading, shape }) => {
  return [number, color, shading, shape].map(toLower).join("-");
};

const strToCard = (string) => {
  return zipObj(
    ["number", "color", "shading", "shape"],
    string.split("-").map(toUpper)
  );
};

const socketUrl = "ws://localhost:3001/ws";

function App() {
  const [state, dispatch] = useReducer(reducer, {
    board: [],
    selected: [],
    players: null,
  });

  const { sendJsonMessage, readyState } = useWebSocket(socketUrl, {
    onOpen: (e) => {
      console.log("[useWebSocket:onOpen] event: ", e);
    },
    onMessage: (e) => {
      console.log("[useWebSocket:onMessage] event: ", e);
      dispatch(JSON.parse(e.data));
    },
  });

  function reducer(state, { type, payload }) {
    const { board, selected } = state;

    switch (type) {
      case "enterRoom": {
        return {
          ...state,
          ...payload,
        };
      }
      case "start":
        return {
          ...state,
          board: payload.board.map(cardToStr),
        };
      case "deselectCard": {
        return {
          ...state,
          selected: without([payload.card], selected),
        };
      }
      case "selectCard":
        return {
          ...state,
          selected: [payload.card, ...selected],
        };
      case "submit":
        if (payload.error) {
          return state;
        }
        return {
          board: updateBoard(board, payload.board.map(cardToStr)),
          selected: [],
          players: payload.players,
        };
      case "find_set":
        console.log(payload.map(cardToStr));
        return state;
    }

    function updateBoard(prevBoard, newBoard) {
      const cardsToRemove = difference(prevBoard, newBoard);
      const cardsToAdd = difference(newBoard, prevBoard);

      return concat(
        prevBoard.map((card) =>
          cardsToRemove.includes(card) ? cardsToAdd.shift() : card
        ),
        cardsToAdd
      );
    }
  }

  useEffect(
    function connectionEstablished() {
      if (readyState != ReadyState.OPEN) {
        console.log("[connectionEstablished] connection is not open");
        return;
      }

      console.log("[connectionEstablished] connection is open");
      const { players } = state;

      players === null &&
        sendJsonMessage({
          type: "enterRoom",
          payload: { playerName },
        });
    },
    [readyState]
  );

  useEffect(
    function cardSelected() {
      console.log("useEffect: cardSelected");

      const { selected } = state;

      if (selected.length == 3) {
        sendMessage("submit", {
          cards: selected.map(strToCard),
          player: playerName,
        });
      }
    },
    [state.selected]
  );

  const onStartClicked = () =>
    sendJsonMessage({
      type: "start",
      payload: {},
    });

  const onCardClicked = (card) => {
    console.log("onCardClicked: ", card);

    const { selected } = state;

    const type = selected.includes(card) ? "deselectCard" : "selectCard";
    dispatch({
      type,
      payload: { card },
    });
  };

  const onFindSetClicked = () => {
    sendMessage("find_set");
  };

  return (
    <>
      {state.players && <Players players={state.players} myName={playerName} />}

      <button onClick={onFindSetClicked}>find set</button>

      <div className={classNames("board", "container")}>
        {isEmpty(state.board) ? (
          <button className="startButton" onClick={onStartClicked}>
            start game
          </button>
        ) : (
          splitEvery(3, state.board).map((cards) => (
            <div className="pure-g card-row">
              {cards.map((card) => (
                // TODO: card can be null
                <Card
                  card={card}
                  key={card}
                  isSelected={state.selected.includes(card)}
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
