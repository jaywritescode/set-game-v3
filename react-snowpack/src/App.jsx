import React, { useState, useEffect } from "react";
import Card from "./Card";

import "./App.css";

function App() {
  const [board, setBoard] = useState([]);
  const [selected, setSelected] = useState([]);

  let websocket;
  useEffect(() => {
    websocket = new WebSocket("ws://localhost:3001");

    websocket.onopen = (e) => {
      console.log("[open] connection established");
      websocket.send(JSON.stringify({ action: 'init', }));
    };

    websocket.onmessage = (e) => {
      console.log(`message received from server: ${e.data}`);
      const response = JSON.parse(e.data);
      
      switch (response.action) {
        case 'start':
          setBoard(response.board);
          break;
      }
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
  });

  const onStartClicked = () => {
    console.log('onStartClicked');
    websocket.send(JSON.stringify({ action: 'start', }));
  }

  const onCardClicked = (card) => {
    console.log('onCardClicked: ', card);

    let updated;
    if (selected.includes(card)) {
      updated = [...selected].filter(c => c != card);
    } else {
      updated = [card, ...selected];
    }

    setSelected(updated);
  }
  

  return (
    <div className="App">
      {
        board.length ? 
          board.map(card => (
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
