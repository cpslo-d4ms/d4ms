import logo from './logo.svg';
import './App.css';
import React from 'react';
import Map from './Components/Map';

function App() {
  return (
    <div className="App">
        <header className="App-header">
            <div style={{
                height: '100vh',
                width: '100vw'
            }}>
                <Map />
            </div>
        </header>
    </div>
  );
}

export default App;
