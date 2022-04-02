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

const useWebsocket = (onMessage) => {
  const [ws, setWebSocket] = useState(null);

  // TODO: Doing this so that we don't try to send messages in the App f.c. when we're not connected.
  //  but managing connection state this way feels wrong.
  const [connected, setConnected] = useState(false);

  const connect = useCallback(async () => {
    console.log("useWebsocket: connect");
    setWebSocket(new WebSocket("ws://localhost:3001" + location.search));
  }, []);

  const sendMessage = useCallback(
    (type, payload = {}) => {
      console.log("useWebsocket: sendMessage");
      if (!ws) {
        return;
      }

      ws.send(JSON.stringify({ type, payload }));
    },
    [ws]
  );

  const onClose = useCallback((e) => {
    if (e.wasClean) {
      console.info(
        `[close] connection closed cleanly, code=${e.code}, reason=${e.reason}`
      );
    } else {
      console.warn("[close] connection died");
    }
    setConnected(false);
  }, []);

  const close = useCallback(
    (code, msg) => {
      ws.close(code, msg);
    },
    [ws]
  );

  // useEffect to make sure the websocket exists before you try adding event handlers to it
  useEffect(
    function setOpenHandler() {
      console.log("setOpenHandler");
      if (!ws) {
        return;
      }
      ws.addEventListener("open", (e) => {
        console.info("[open] connection established");
        setConnected(true);
      });
      return () => ws.removeEventListener("open");
    },
    [ws]
  );

  useEffect(
    function setMessageHandler() {
      console.log("setMessageHandler");
      if (!ws) {
        return;
      }
      ws.addEventListener("message", (e) => {
        console.info(`[message]: ${e.data}`);
        onMessage(JSON.parse(e.data));
      });
      return () => ws.removeEventListener("message");
    },
    [ws]
  );

  useEffect(
    function setCloseHandler() {
      console.log("setCloseHandler");
      if (!ws) {
        return;
      }
      ws.addEventListener("close", onClose);
      return () => ws.removeEventListener("close");
    },
    [ws]
  );

  return [connect, sendMessage, close, connected];
};

function App() {
  const [state, dispatch] = useReducer(reducer, {
    board: [],
    selected: [],
    players: null,
  });

  const [connect, sendMessage, close, connected] = useWebsocket(dispatch);

  function reducer(state, { type, payload }) {
    const { board, selected } = state;

    switch (type) {
      case "enterRoom":
      case "joinRoom": {
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

      return concat(prevBoard.map((card) =>
        cardsToRemove.includes(card) ? cardsToAdd.shift() : card
      ), cardsToAdd);
    }
  }

  useEffect(function roomEntered() {
    console.info("useEffect: roomEntered");
    connect();
    return () => close(1000, "Done");
  }, []);

  useEffect(
    function connectionEstablished() {
      console.log("useEffect: connectionEstablished");

      if (!connected) {
        return;
      }

      const { players } = state;

      players === null && sendMessage("enterRoom");
    },
    [connected]
  );

  useEffect(
    function joinGameIfPossible() {
      console.log("useEffect: joinGameIfPossible");

      const { players } = state;

      if (players === null) {
        return;
      }

      !(playerName in players) &&
        Object.keys(players).length < MAX_PLAYERS &&
        sendMessage("joinRoom", { playerName });
    },
    [state.players]
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

  const onStartClicked = () => sendMessage("start");

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
  }

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
