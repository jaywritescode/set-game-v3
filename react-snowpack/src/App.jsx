import React, { useState, useEffect } from "react";

import "./App.css";
import "./sprites.css";

function App() {
  const [board, setBoard] = useState([]);

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
  

  return (
    <div className="App">
      {
        board.length ? 
          board.map(card => (
            <div className={`card ${card}`} />
          )) :
          (
            <button onClick={onStartClicked}>start game</button>
          )
      }
    </div>
  );
}

export default App;
