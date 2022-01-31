import React, { useReducer, useEffect } from "react";
import { F, identity, toPairs, values, zipObj } from "ramda";
import Card from "./Card";

import "./App.css";

let websocket;
function App() {
  const [state, dispatch] = useReducer(reducer, { board: Object.create(null) });

  function reducer(state, action) {
    switch (action.type) {
      case 'init':
      case 'start':
        return { board: zipObj(action.board, action.board.map(F)) };
      case 'select_card':
        return { 
          board: {
            ...state.board, 
            [action.card]: true 
          } 
        };
    }
  }

  useEffect(() => {
    console.log('useEffect: page inited');

    websocket = new WebSocket("ws://localhost:3001");

    websocket.onopen = (e) => {
      console.log("[open] connection established");
      websocket.send(JSON.stringify({ type: 'init', }));
    };

    websocket.onmessage = (e) => {
      console.log(`message received from server: ${e.data}`);
      const response = JSON.parse(e.data);

      dispatch(response);
    };

    websocket.onclose = (e) => {
      if (e.wasClean) {
        console.log(`[close] connection closed cleanly, code=${e.code}, reason=${e.reason}`);
      } else {
        console.error("[close] connection died");
      }
    };

    websocket.onerror = (err) => {
      console.error('[error]: ', err.message);
    };

    return () => websocket.close(1000, "Done");
  }, []);

  useEffect(() => {
    console.log('useEffect: card selected');

    const selected = toPairs(state.board).filter(([_, isSelected]) => isSelected).map(([card, _]) => card);
    if (selected.length == 3) {
      websocket.send(JSON.stringify({
        type: 'submit',
        cards: selected
      }));
    }
  }, [state.board]);

  const onStartClicked = () => {
    console.log('onStartClicked');
    websocket.send(JSON.stringify({ type: 'start', }));
  }

  const onCardClicked = (card) => {
    console.log("onCardClicked: ", card);
    dispatch({ 
      type: 'select_card',
      card,
    });
  }

  return (
    <div className="App">
      {
        state.board.length ? 
          state.board.map(card => (
            <Card card={card} selected={selected.includes(card)} onClick={() => onCardClicked(card)} />
          )) :
          (
            <button onClick={onStartClicked}>start game</button>
          )
      }
    </div>
  );
}

export default App;
