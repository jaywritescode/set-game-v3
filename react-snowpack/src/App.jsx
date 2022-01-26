import React, { useState, useEffect } from "react";
import logo from "./logo.svg";
import "./App.css";

function App() {
  const [board, setBoard] = useState([]);

  let websocket;
  useEffect(() => {
    websocket = new WebSocket("ws://localhost:3001");

    websocket.onopen = (e) => {
      console.log("[open] connection established");
      websocket.send("hello");
    };

    websocket.onmessage = (e) => {
      console.log(`message received from server: ${e.data}`);
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
  
  if (!board.length) {
    return (
      <button>start game</button>
    );
  }
  
  
  // Create the count state.
  const [count, setCount] = useState(0);
  // Update the count (+1 every second).
  useEffect(() => {
    const timer = setTimeout(() => setCount(count + 1), 1000);
    return () => clearTimeout(timer);
  }, [count, setCount]);
  // Return the App component.
  return (
    <div className="App">
      <header className="App-header">
        <p>
          Page has been open for <code>{count}</code> seconds.
        </p>
        <img src={logo} className="App-logo" alt="logo" />
      </header>
    </div>
  );
}

export default App;
