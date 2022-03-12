import React, { useState, useReducer, useEffect, useCallback } from "react";
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

const useWebsocket = (onMessage) => {
  const [ws, setWebSocket] = useState(null);

  // TODO: Doing this so that we don't try to send messages in the App f.c. when we're not connected.
  //  but managing connection state this way feels wrong.
  const [connected, setConnected] = useState(false);

  const connect = useCallback(() => {
    console.log('useWebsocket: connect');
    setWebSocket(new WebSocket("ws://localhost:3001"));
  }, []);

  const sendMessage = useCallback((args) => {
    console.log('useWebsocket: sendMessage');
    if (!ws) { return; }

    ws.send(JSON.stringify(args))
  }, [ws]);

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

  const close = useCallback((code, msg) => {
    ws.close(code, msg);
  }, [ws]);

  // useEffect to make sure the websocket exists before you try adding event handlers to it
  useEffect(function setOpenHandler() {
    console.log('setOpenHandler');
    if (!ws) { return; }
    ws.addEventListener('open', (e) => {
      console.info('[open] connection established');
      setConnected(true);
    });
    return () => ws.removeEventListener('open');
  }, [ws]);

  useEffect(function setMessageHandler() {
    console.log('setMessageHandler');
    if (!ws) { return; }
    ws.addEventListener('message', (e) => {
      console.info(`[message]: ${e.data}`);
      onMessage(JSON.parse(e.data));
    });
    return () => ws.removeEventListener('message');
  }, [ws]);

  useEffect(function setCloseHandler() {
    console.log('setCloseHandler');
    if (!ws) { return; }
    ws.addEventListener('close', onClose);
    return () => ws.removeEventListener('close');
  }, [ws]);

  return [connect, sendMessage, close, connected];
}
function App() {
  const [state, dispatch] = useReducer(reducer, {
    board: Object.create(null),
    playerName: generate().dashed,
    players: [],
  });

  const [connect, sendMessage, close, connected] = useWebsocket(dispatch);

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
  }, [connected, state.players]);

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
        className={classNames("board", "container")}
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
