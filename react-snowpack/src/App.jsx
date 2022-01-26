import React, { useState, useEffect } from "react";
import logo from "./logo.svg";
import "./App.css";

const ws = new WebSocket("ws://localhost:3001");
ws.onopen = (e) => {
  console.log("[open] connection established");
  ws.send("hello");
}

ws.onerror = (e) => {
  console.error('error', e.message);
}

function App() {
  const [board, setBoard] = useState([]);
  
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
