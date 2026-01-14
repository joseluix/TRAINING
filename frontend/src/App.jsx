// WELCOME TO REACT!
// ----------------------------------------------------------------------
// LESSON 2: State & Interactivity
// 
// 1. Importing 'useState':
// To make our app interactive (remember things), we need 'State'.
// We import the 'useState' hook from React.
// ----------------------------------------------------------------------
import { useState } from 'react';
import './App.css';

function App() {
  // --------------------------------------------------------------------
  // 2. Defining State:
  // 'count' is the current value (starts at 0).
  // 'setCount' is a function to UPDATE that value.
  // When state changes, React automatically re-renders the component!
  // --------------------------------------------------------------------
  const [count, setCount] = useState(0);

  return (
    <div className="app-container">
      <h1>Trading App - Counter</h1>

      <div className="card">
        <p>Current Count: <strong>{count}</strong></p>

        {/* 
           3. Events (onClick):
           We attach an 'onClick' handler to the button.
           When clicked, we call 'setCount' to update the state.
        */}
        <button onClick={() => setCount(count + 1)}>
          Increase Count
        </button>

        <button onClick={() => setCount(count - 1)} style={{ marginLeft: '10px' }}>
          Decrease Count
        </button>
      </div>

      <p className="instruction">
        Notice how the number changes without reloading the page? That's React State!
      </p>
    </div>
  );
}

export default App;
